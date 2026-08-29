from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class MaterialFileModel(BaseModel):
    __tablename__ = "material_file"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE','SUPERSEDED','ERROR')",
            name="ck_material_file_status",
        ),
        UniqueConstraint(
            "storage_key",
            name="uq_material_file_storage_key",
        ),
        {"schema": "lia2"},
    )

    materialFileId: Mapped[UUID] = mapped_column(
        "material_file_id",
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
    originalFileName: Mapped[str] = mapped_column(
        "original_file_name",
        String(500),
        nullable=False,
    )
    storageKey: Mapped[str] = mapped_column(
        "storage_key",
        String(1000),
        nullable=False,
    )
    mimeType: Mapped[str] = mapped_column(
        "mime_type",
        String(200),
        nullable=False,
    )
    sizeBytes: Mapped[int] = mapped_column(
        "size_bytes",
        BigInteger,
        nullable=False,
    )
    sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
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
