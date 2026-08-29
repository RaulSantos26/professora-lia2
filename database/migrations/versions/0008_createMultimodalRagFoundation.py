"""Create multimodal processing jobs and RAG metadata."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_material_status",
        "material",
        schema="lia2",
        type_="check",
    )
    op.create_check_constraint(
        "ck_material_status",
        "material",
        "status IN ('UPLOADED','PROCESSING','PARTIAL','READY','ERROR','ARCHIVED')",
        schema="lia2",
    )
    op.add_column(
        "document_block",
        sa.Column(
            "asset_storage_key",
            sa.String(length=1200),
            nullable=True,
        ),
        schema="lia2",
    )
    op.add_column(
        "document_block",
        sa.Column(
            "orientation_degrees",
            sa.Integer(),
            nullable=True,
        ),
        schema="lia2",
    )
    op.add_column(
        "document_block",
        sa.Column(
            "vision_model_id",
            sa.String(length=300),
            nullable=True,
        ),
        schema="lia2",
    )

    op.add_column(
        "document_chunk",
        sa.Column(
            "embedding",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        schema="lia2",
    )
    op.add_column(
        "document_chunk",
        sa.Column(
            "embedding_model_id",
            sa.String(length=300),
            nullable=True,
        ),
        schema="lia2",
    )
    op.add_column(
        "document_chunk",
        sa.Column(
            "embedded_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        schema="lia2",
    )

    op.create_table(
        "material_processing_job",
        sa.Column(
            "material_processing_job_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "material_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "job_type",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default="QUEUED",
        ),
        sa.Column(
            "stage",
            sa.String(length=40),
            nullable=False,
            server_default="QUEUED",
        ),
        sa.Column(
            "progress_percent",
            sa.Integer(),
            nullable=False,
            server_default="5",
        ),
        sa.Column(
            "message",
            sa.String(length=500),
            nullable=False,
            server_default="Na fila para processamento.",
        ),
        sa.Column(
            "requested_model_id",
            sa.String(length=300),
            nullable=True,
        ),
        sa.Column(
            "effective_vision_model_id",
            sa.String(length=300),
            nullable=True,
        ),
        sa.Column(
            "effective_embedding_model_id",
            sa.String(length=300),
            nullable=True,
        ),
        sa.Column(
            "fallback_reason",
            sa.String(length=1000),
            nullable=True,
        ),
        sa.Column(
            "error_code",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "error_message",
            sa.String(length=1000),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "finished_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "job_type IN ('ANALYZE','INDEX_RAG')",
            name="ck_material_processing_job_type",
        ),
        sa.CheckConstraint(
            "status IN ('QUEUED','RUNNING','COMPLETED','COMPLETED_WITH_WARNINGS','FAILED','CANCELLED')",
            name="ck_material_processing_job_status",
        ),
        sa.CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name="ck_material_processing_job_progress",
        ),
        sa.ForeignKeyConstraint(
            ["material_id"],
            ["lia2.material.material_id"],
            name="fk_material_processing_job_material",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["lia2.student.student_id"],
            name="fk_material_processing_job_student",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "material_processing_job_id",
            name="pk_material_processing_job",
        ),
        schema="lia2",
    )

    op.create_index(
        "ix_material_processing_job_status_created",
        "material_processing_job",
        ["status", "created_at"],
        schema="lia2",
    )
    op.create_index(
        "ix_material_processing_job_material",
        "material_processing_job",
        ["material_id"],
        schema="lia2",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_material_status",
        "material",
        schema="lia2",
        type_="check",
    )
    op.execute(
        "UPDATE lia2.material SET status = 'PROCESSING' "
        "WHERE status = 'PARTIAL'"
    )
    op.create_check_constraint(
        "ck_material_status",
        "material",
        "status IN ('UPLOADED','PROCESSING','READY','ERROR','ARCHIVED')",
        schema="lia2",
    )
    op.drop_index(
        "ix_material_processing_job_material",
        table_name="material_processing_job",
        schema="lia2",
    )
    op.drop_index(
        "ix_material_processing_job_status_created",
        table_name="material_processing_job",
        schema="lia2",
    )
    op.drop_table(
        "material_processing_job",
        schema="lia2",
    )

    op.drop_column(
        "document_chunk",
        "embedded_at",
        schema="lia2",
    )
    op.drop_column(
        "document_chunk",
        "embedding_model_id",
        schema="lia2",
    )
    op.drop_column(
        "document_chunk",
        "embedding",
        schema="lia2",
    )

    op.drop_column(
        "document_block",
        "vision_model_id",
        schema="lia2",
    )
    op.drop_column(
        "document_block",
        "orientation_degrees",
        schema="lia2",
    )
    op.drop_column(
        "document_block",
        "asset_storage_key",
        schema="lia2",
    )
