from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class StudentSubjectModel(BaseModel):
    __tablename__ = "student_subject"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE', 'ARCHIVED')",
            name="ck_student_subject_status",
        ),
        UniqueConstraint(
            "student_learning_context_id",
            "code",
            name="uq_student_subject_code_per_context",
        ),
        {"schema": "lia2"},
    )

    studentSubjectId: Mapped[UUID] = mapped_column(
        "student_subject_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    studentLearningContextId: Mapped[UUID] = mapped_column(
        "student_learning_context_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.student_learning_context.student_learning_context_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    subjectDefinitionId: Mapped[UUID | None] = mapped_column(
        "subject_definition_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.subject.subject_id", ondelete="RESTRICT"),
        nullable=True,
    )
    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(1000),
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
