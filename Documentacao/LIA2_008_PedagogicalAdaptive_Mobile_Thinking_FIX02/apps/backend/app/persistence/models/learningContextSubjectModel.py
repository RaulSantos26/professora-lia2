from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class LearningContextSubjectModel(BaseModel):
    __tablename__ = "learning_context_subject"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_learning_context_subject_status",
        ),
        UniqueConstraint(
            "learning_context_id",
            "subject_id",
            name="uq_learning_context_subject",
        ),
        {"schema": "lia2"},
    )

    learningContextSubjectId: Mapped[UUID] = mapped_column(
        "learning_context_subject_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    learningContextId: Mapped[UUID] = mapped_column(
        "learning_context_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.learning_context.learning_context_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    subjectId: Mapped[UUID] = mapped_column(
        "subject_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.subject.subject_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    displayOrder: Mapped[int | None] = mapped_column(
        "display_order",
        Integer,
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
    updatedAt: Mapped[datetime] = mapped_column(
        "updated_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
