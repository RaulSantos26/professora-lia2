from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class DocumentChunkModel(BaseModel):
    __tablename__ = "document_chunk"
    __table_args__ = (
        CheckConstraint(
            "status IN ('READY','PENDING_EMBEDDING','EMBEDDED','ERROR')",
            name="ck_document_chunk_status",
        ),
        UniqueConstraint(
            "document_version_id",
            "chunk_index",
            name="uq_document_chunk_index",
        ),
        {"schema": "lia2"},
    )

    documentChunkId: Mapped[UUID] = mapped_column(
        "document_chunk_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
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
    evidenceId: Mapped[UUID | None] = mapped_column(
        "evidence_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.evidence.evidence_id", ondelete="RESTRICT"),
        nullable=True,
    )
    chunkIndex: Mapped[int] = mapped_column(
        "chunk_index",
        Integer,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    tokenEstimate: Mapped[int | None] = mapped_column(
        "token_estimate",
        Integer,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING_EMBEDDING",
    )
    embedding: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    embeddingModelId: Mapped[str | None] = mapped_column(
        "embedding_model_id",
        String(300),
        nullable=True,
    )
    embeddedAt: Mapped[datetime | None] = mapped_column(
        "embedded_at",
        DateTime(timezone=True),
        nullable=True,
    )
    createdAt: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
