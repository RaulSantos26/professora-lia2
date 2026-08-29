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


class LearningUnitModel(BaseModel):
    __tablename__ = "learning_unit"
    __table_args__ = (
        CheckConstraint(
            "unit_type IN ('LESSON', 'MODULE', 'CHAPTER', 'SECTION')",
            name="ck_learning_unit_type",
        ),
        CheckConstraint(
            "status IN ('DRAFT', 'ACTIVE', 'INACTIVE', 'ARCHIVED')",
            name="ck_learning_unit_status",
        ),
        UniqueConstraint(
            "learning_context_subject_id",
            "code",
            name="uq_learning_unit_code_per_context_subject",
        ),
        {"schema": "lia2"},
    )

    learningUnitId: Mapped[UUID] = mapped_column(
        "learning_unit_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    learningContextSubjectId: Mapped[UUID] = mapped_column(
        "learning_context_subject_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.learning_context_subject.learning_context_subject_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    parentLearningUnitId: Mapped[UUID | None] = mapped_column(
        "parent_learning_unit_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.learning_unit.learning_unit_id", ondelete="RESTRICT"),
        nullable=True,
    )
    unitType: Mapped[str] = mapped_column(
        "unit_type",
        String(20),
        nullable=False,
        default="LESSON",
    )
    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(1500),
        nullable=True,
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
