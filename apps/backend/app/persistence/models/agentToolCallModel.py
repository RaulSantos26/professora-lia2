from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class AgentToolCallModel(BaseModel):
    __tablename__ = "agent_tool_call"
    __table_args__ = (
        CheckConstraint(
            "status IN ('STARTED','COMPLETED','FAILED')",
            name="ck_agent_tool_call_status",
        ),
        {"schema": "lia2"},
    )

    agentToolCallId: Mapped[UUID] = mapped_column(
        "agent_tool_call_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    agentRunId: Mapped[UUID] = mapped_column(
        "agent_run_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.agent_run.agent_run_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    toolName: Mapped[str] = mapped_column(
        "tool_name",
        String(80),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="STARTED",
    )
    requestJson: Mapped[dict] = mapped_column(
        "request_json",
        JSONB,
        nullable=False,
        default=dict,
    )
    responseJson: Mapped[dict | None] = mapped_column(
        "response_json",
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
    startedAt: Mapped[datetime] = mapped_column(
        "started_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    finishedAt: Mapped[datetime | None] = mapped_column(
        "finished_at",
        DateTime(timezone=True),
        nullable=True,
    )
