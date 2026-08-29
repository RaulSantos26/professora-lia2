from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class DocumentBlockModel(BaseModel):
    __tablename__ = "document_block"
    __table_args__ = (
        CheckConstraint(
            "block_type IN ('TEXT','FIGURE','CAPTION','TABLE','IMAGE','OTHER')",
            name="ck_document_block_type",
        ),
        CheckConstraint(
            "processing_status IN ('READY','PENDING_OCR','PENDING_VISION','PENDING_STRUCTURE','ERROR')",
            name="ck_document_block_processing_status",
        ),
        {"schema": "lia2"},
    )

    documentBlockId: Mapped[UUID] = mapped_column(
        "document_block_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    documentPageId: Mapped[UUID] = mapped_column(
        "document_page_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.document_page.document_page_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequenceNumber: Mapped[int] = mapped_column(
        "sequence_number",
        Integer,
        nullable=False,
        default=1,
    )
    blockType: Mapped[str] = mapped_column(
        "block_type",
        String(20),
        nullable=False,
    )
    textContent: Mapped[str | None] = mapped_column(
        "text_content",
        Text,
        nullable=True,
    )
    structuredData: Mapped[dict | None] = mapped_column(
        "structured_data",
        JSONB,
        nullable=True,
    )
    bbox: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    processingStatus: Mapped[str] = mapped_column(
        "processing_status",
        String(30),
        nullable=False,
        default="READY",
    )
    assetStorageKey: Mapped[str | None] = mapped_column(
        "asset_storage_key",
        String(1200),
        nullable=True,
    )
    orientationDegrees: Mapped[int | None] = mapped_column(
        "orientation_degrees",
        Integer,
        nullable=True,
    )
    visionModelId: Mapped[str | None] = mapped_column(
        "vision_model_id",
        String(300),
        nullable=True,
    )
    createdAt: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
