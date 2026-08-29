from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class EvidenceModel(BaseModel):
    __tablename__ = "evidence"
    __table_args__ = (
        CheckConstraint(
            "evidence_type IN ('TEXT','FIGURE','TABLE','IMAGE','DOCUMENT')",
            name="ck_evidence_type",
        ),
        CheckConstraint(
            "status IN ('ACTIVE','SUPERSEDED','ARCHIVED')",
            name="ck_evidence_status",
        ),
        {"schema": "lia2"},
    )

    evidenceId: Mapped[UUID] = mapped_column(
        "evidence_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    studentId: Mapped[UUID] = mapped_column(
        "student_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.student.student_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    materialId: Mapped[UUID] = mapped_column(
        "material_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.material.material_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    documentVersionId: Mapped[UUID] = mapped_column(
        "document_version_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.document_version.document_version_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    documentPageId: Mapped[UUID | None] = mapped_column(
        "document_page_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.document_page.document_page_id", ondelete="RESTRICT"),
        nullable=True,
    )
    documentBlockId: Mapped[UUID | None] = mapped_column(
        "document_block_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.document_block.document_block_id", ondelete="RESTRICT"),
        nullable=True,
    )
    evidenceType: Mapped[str] = mapped_column(
        "evidence_type",
        String(20),
        nullable=False,
    )
    locator: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    excerpt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
    )
    createdAt: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
