from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class AgentRunModel(BaseModel):
    __tablename__ = "agent_run"
    __table_args__ = (
        CheckConstraint(
            "status IN ('QUEUED','RUNNING','READY','FAILED','CANCELLED')",
            name="ck_agent_run_status",
        ),
        CheckConstraint(
            "thinking_mode IN ('AUTO','ON','OFF')",
            name="ck_agent_run_thinking_mode",
        ),
        CheckConstraint(
            "progress_percent BETWEEN 0 AND 100",
            name="ck_agent_run_progress",
        ),
        {"schema": "lia2"},
    )

    agentRunId: Mapped[UUID] = mapped_column(
        "agent_run_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    agentThreadId: Mapped[UUID] = mapped_column(
        "agent_thread_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.agent_thread.agent_thread_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    userMessageId: Mapped[UUID] = mapped_column(
        "user_message_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.agent_message.agent_message_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    assistantMessageId: Mapped[UUID | None] = mapped_column(
        "assistant_message_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.agent_message.agent_message_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="QUEUED",
    )
    stage: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="QUEUED",
    )
    progressPercent: Mapped[int] = mapped_column(
        "progress_percent",
        Integer,
        nullable=False,
        default=5,
    )
    message: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        default="Na fila para a Lia.",
    )
    requestedTextModelId: Mapped[str | None] = mapped_column(
        "requested_text_model_id",
        String(300),
        nullable=True,
    )
    effectiveTextModelId: Mapped[str | None] = mapped_column(
        "effective_text_model_id",
        String(300),
        nullable=True,
    )
    thinkingMode: Mapped[str] = mapped_column(
        "thinking_mode",
        String(10),
        nullable=False,
        default="AUTO",
    )
    effectiveThinkingEnabled: Mapped[bool | None] = mapped_column(
        "effective_thinking_enabled",
        Boolean,
        nullable=True,
    )
    planJson: Mapped[dict | None] = mapped_column(
        "plan_json",
        JSONB,
        nullable=True,
    )
    errorCode: Mapped[str | None] = mapped_column(
        "error_code",
        String(100),
        nullable=True,
    )
    errorMessage: Mapped[str | None] = mapped_column(
        "error_message",
        String(1000),
        nullable=True,
    )
    createdAt: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    startedAt: Mapped[datetime | None] = mapped_column(
        "started_at",
        DateTime(timezone=True),
        nullable=True,
    )
    finishedAt: Mapped[datetime | None] = mapped_column(
        "finished_at",
        DateTime(timezone=True),
        nullable=True,
    )
