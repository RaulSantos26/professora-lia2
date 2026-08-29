from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, UniqueConstraint, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class DocumentModel(BaseModel):
    __tablename__ = "document"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING','PROCESSING','READY','PARTIAL','ERROR')",
            name="ck_document_status",
        ),
        UniqueConstraint("material_id", name="uq_document_material"),
        {"schema": "lia2"},
    )

    documentId: Mapped[UUID] = mapped_column(
        "document_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    materialId: Mapped[UUID] = mapped_column(
        "material_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.material.material_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING",
    )
    pageCount: Mapped[int | None] = mapped_column(
        "page_count",
        nullable=True,
    )
    createdAt: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updatedAt: Mapped[datetime] = mapped_column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
