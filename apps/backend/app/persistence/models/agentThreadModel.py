from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class AgentThreadModel(BaseModel):
    __tablename__ = "agent_thread"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE','ARCHIVED')",
            name="ck_agent_thread_status",
        ),
        {"schema": "lia2"},
    )

    agentThreadId: Mapped[UUID] = mapped_column(
        "agent_thread_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    studentId: Mapped[UUID] = mapped_column(
        "student_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.student.student_id", ondelete="RESTRICT"),
        nullable=False,
    )
    studentLearningContextId: Mapped[UUID | None] = mapped_column(
        "student_learning_context_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.student_learning_context.student_learning_context_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    studentSubjectId: Mapped[UUID | None] = mapped_column(
        "student_subject_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.student_subject.student_subject_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    studentLearningUnitId: Mapped[UUID | None] = mapped_column(
        "student_learning_unit_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.student_learning_unit.student_learning_unit_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
    )
    memoryJson: Mapped[dict] = mapped_column(
        "memory_json",
        JSONB,
        nullable=False,
        default=dict,
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
    lastMessageAt: Mapped[datetime | None] = mapped_column(
        "last_message_at",
        DateTime(timezone=True),
        nullable=True,
    )
