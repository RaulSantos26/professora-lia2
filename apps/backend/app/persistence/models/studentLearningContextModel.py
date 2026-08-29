from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class StudentLearningContextModel(BaseModel):
    __tablename__ = "student_learning_context"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE', 'COMPLETED')",
            name="ck_student_learning_context_status",
        ),
        {"schema": "lia2"},
    )

    studentLearningContextId: Mapped[UUID] = mapped_column(
        "student_learning_context_id",
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
    learningContextId: Mapped[UUID] = mapped_column(
        "learning_context_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.learning_context.learning_context_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    academicStageId: Mapped[UUID | None] = mapped_column(
        "academic_stage_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.academic_stage.academic_stage_id", ondelete="RESTRICT"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
    )
    enrolledAt: Mapped[datetime] = mapped_column(
        "enrolled_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    completedAt: Mapped[datetime | None] = mapped_column(
        "completed_at",
        DateTime(timezone=True),
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
