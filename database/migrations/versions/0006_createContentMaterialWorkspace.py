"""Create Content & Material Workspace and RAG foundation."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "material",
        sa.Column("material_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_learning_context_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("student_subject_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("student_learning_unit_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("material_type", sa.String(length=20), nullable=False),
        sa.Column("source_type", sa.String(length=20), nullable=False, server_default="UPLOAD"),
        sa.Column("description", sa.String(length=1500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="UPLOADED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("material_type IN ('PDF','IMAGE','TEXT','DOCUMENT','OTHER')", name="ck_material_type"),
        sa.CheckConstraint("source_type IN ('UPLOAD','MANUAL','LINK')", name="ck_material_source_type"),
        sa.CheckConstraint("status IN ('UPLOADED','PROCESSING','READY','ERROR','ARCHIVED')", name="ck_material_status"),
        sa.ForeignKeyConstraint(["student_id"], ["lia2.student.student_id"], name="fk_material_student", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_learning_context_id"], ["lia2.student_learning_context.student_learning_context_id"], name="fk_material_student_context", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_subject_id"], ["lia2.student_subject.student_subject_id"], name="fk_material_student_subject", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_learning_unit_id"], ["lia2.student_learning_unit.student_learning_unit_id"], name="fk_material_student_unit", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("material_id", name="pk_material"),
        schema="lia2",
    )
    op.create_index("ix_material_student_id", "material", ["student_id"], schema="lia2")

    op.create_table(
        "material_file",
        sa.Column("material_file_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("material_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("original_file_name", sa.String(length=500), nullable=False),
        sa.Column("storage_key", sa.String(length=1000), nullable=False),
        sa.Column("mime_type", sa.String(length=200), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('ACTIVE','SUPERSEDED','ERROR')", name="ck_material_file_status"),
        sa.ForeignKeyConstraint(["material_id"], ["lia2.material.material_id"], name="fk_material_file_material", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("material_file_id", name="pk_material_file"),
        sa.UniqueConstraint("storage_key", name="uq_material_file_storage_key"),
        schema="lia2",
    )
    op.create_index("ix_material_file_sha256", "material_file", ["sha256"], schema="lia2")

    op.create_table(
        "document",
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("material_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('PENDING','PROCESSING','READY','PARTIAL','ERROR')", name="ck_document_status"),
        sa.ForeignKeyConstraint(["material_id"], ["lia2.material.material_id"], name="fk_document_material", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("document_id", name="pk_document"),
        sa.UniqueConstraint("material_id", name="uq_document_material"),
        schema="lia2",
    )

    op.create_table(
        "document_version",
        sa.Column("document_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("material_file_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("extraction_status", sa.String(length=30), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("extraction_status IN ('PENDING','NATIVE_TEXT_READY','VISUAL_PENDING','READY','PARTIAL','ERROR')", name="ck_document_version_extraction_status"),
        sa.ForeignKeyConstraint(["document_id"], ["lia2.document.document_id"], name="fk_document_version_document", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["material_file_id"], ["lia2.material_file.material_file_id"], name="fk_document_version_file", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("document_version_id", name="pk_document_version"),
        sa.UniqueConstraint("document_id", "version_number", name="uq_document_version_number"),
        schema="lia2",
    )

    op.create_table(
        "document_page",
        sa.Column("document_page_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("native_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="EMPTY"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('READY','TEXT_READY','VISUAL_PENDING','EMPTY','ERROR')", name="ck_document_page_status"),
        sa.ForeignKeyConstraint(["document_version_id"], ["lia2.document_version.document_version_id"], name="fk_document_page_version", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("document_page_id", name="pk_document_page"),
        sa.UniqueConstraint("document_version_id", "page_number", name="uq_document_page_number"),
        schema="lia2",
    )

    op.create_table(
        "document_block",
        sa.Column("document_block_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_page_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("block_type", sa.String(length=20), nullable=False),
        sa.Column("text_content", sa.Text(), nullable=True),
        sa.Column("structured_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("bbox", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("processing_status", sa.String(length=30), nullable=False, server_default="READY"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("block_type IN ('TEXT','FIGURE','CAPTION','TABLE','IMAGE','OTHER')", name="ck_document_block_type"),
        sa.CheckConstraint("processing_status IN ('READY','PENDING_OCR','PENDING_VISION','PENDING_STRUCTURE','ERROR')", name="ck_document_block_processing_status"),
        sa.ForeignKeyConstraint(["document_page_id"], ["lia2.document_page.document_page_id"], name="fk_document_block_page", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("document_block_id", name="pk_document_block"),
        schema="lia2",
    )

    op.create_table(
        "evidence",
        sa.Column("evidence_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("material_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_page_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("document_block_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("evidence_type", sa.String(length=20), nullable=False),
        sa.Column("locator", sa.String(length=300), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("evidence_type IN ('TEXT','FIGURE','TABLE','IMAGE','DOCUMENT')", name="ck_evidence_type"),
        sa.CheckConstraint("status IN ('ACTIVE','SUPERSEDED','ARCHIVED')", name="ck_evidence_status"),
        sa.ForeignKeyConstraint(["student_id"], ["lia2.student.student_id"], name="fk_evidence_student", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["material_id"], ["lia2.material.material_id"], name="fk_evidence_material", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["document_version_id"], ["lia2.document_version.document_version_id"], name="fk_evidence_version", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["document_page_id"], ["lia2.document_page.document_page_id"], name="fk_evidence_page", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["document_block_id"], ["lia2.document_block.document_block_id"], name="fk_evidence_block", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("evidence_id", name="pk_evidence"),
        schema="lia2",
    )

    op.create_table(
        "document_chunk",
        sa.Column("document_chunk_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_page_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("document_block_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("evidence_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_estimate", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="PENDING_EMBEDDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('READY','PENDING_EMBEDDING','EMBEDDED','ERROR')", name="ck_document_chunk_status"),
        sa.ForeignKeyConstraint(["document_version_id"], ["lia2.document_version.document_version_id"], name="fk_document_chunk_version", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["document_page_id"], ["lia2.document_page.document_page_id"], name="fk_document_chunk_page", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["document_block_id"], ["lia2.document_block.document_block_id"], name="fk_document_chunk_block", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["evidence_id"], ["lia2.evidence.evidence_id"], name="fk_document_chunk_evidence", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("document_chunk_id", name="pk_document_chunk"),
        sa.UniqueConstraint("document_version_id", "chunk_index", name="uq_document_chunk_index"),
        schema="lia2",
    )


def downgrade() -> None:
    op.drop_table("document_chunk", schema="lia2")
    op.drop_table("evidence", schema="lia2")
    op.drop_table("document_block", schema="lia2")
    op.drop_table("document_page", schema="lia2")
    op.drop_table("document_version", schema="lia2")
    op.drop_table("document", schema="lia2")
    op.drop_index("ix_material_file_sha256", table_name="material_file", schema="lia2")
    op.drop_table("material_file", schema="lia2")
    op.drop_index("ix_material_student_id", table_name="material", schema="lia2")
    op.drop_table("material", schema="lia2")
