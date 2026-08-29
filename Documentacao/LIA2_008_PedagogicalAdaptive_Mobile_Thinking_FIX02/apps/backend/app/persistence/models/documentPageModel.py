from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class DocumentPageModel(BaseModel):
    __tablename__ = "document_page"
    __table_args__ = (
        CheckConstraint(
            "status IN ('READY','TEXT_READY','VISUAL_PENDING','EMPTY','ERROR')",
            name="ck_document_page_status",
        ),
        UniqueConstraint(
            "document_version_id",
            "page_number",
            name="uq_document_page_number",
        ),
        {"schema": "lia2"},
    )

    documentPageId: Mapped[UUID] = mapped_column(
        "document_page_id",
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
    pageNumber: Mapped[int] = mapped_column(
        "page_number",
        Integer,
        nullable=False,
    )
    nativeText: Mapped[str | None] = mapped_column(
        "native_text",
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="EMPTY",
    )
    createdAt: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
