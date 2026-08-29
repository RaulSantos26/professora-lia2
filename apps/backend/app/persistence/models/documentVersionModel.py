from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class DocumentVersionModel(BaseModel):
    __tablename__ = "document_version"
    __table_args__ = (
        CheckConstraint(
            "extraction_status IN ('PENDING','NATIVE_TEXT_READY','VISUAL_PENDING','READY','PARTIAL','ERROR')",
            name="ck_document_version_extraction_status",
        ),
        UniqueConstraint(
            "document_id",
            "version_number",
            name="uq_document_version_number",
        ),
        {"schema": "lia2"},
    )

    documentVersionId: Mapped[UUID] = mapped_column(
        "document_version_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    documentId: Mapped[UUID] = mapped_column(
        "document_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.document.document_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    materialFileId: Mapped[UUID] = mapped_column(
        "material_file_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.material_file.material_file_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    versionNumber: Mapped[int] = mapped_column(
        "version_number",
        Integer,
        nullable=False,
        default=1,
    )
    extractionStatus: Mapped[str] = mapped_column(
        "extraction_status",
        String(30),
        nullable=False,
        default="PENDING",
    )
    createdAt: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
