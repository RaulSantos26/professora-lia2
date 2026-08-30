from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class AgentMessageModel(BaseModel):
    __tablename__ = "agent_message"
    __table_args__ = (
        CheckConstraint(
            "role IN ('USER','ASSISTANT')",
            name="ck_agent_message_role",
        ),
        {"schema": "lia2"},
    )

    agentMessageId: Mapped[UUID] = mapped_column(
        "agent_message_id",
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
    role: Mapped[str] = mapped_column(
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    citationsJson: Mapped[list] = mapped_column(
        "citations_json",
        JSONB,
        nullable=False,
        default=list,
    )
    visualTaskIds: Mapped[list] = mapped_column(
        "visual_task_ids",
        JSONB,
        nullable=False,
        default=list,
    )
    imageTaskIds: Mapped[list] = mapped_column(
        "image_task_ids",
        JSONB,
        nullable=False,
        default=list,
    )
    actionsJson: Mapped[list] = mapped_column(
        "actions_json",
        JSONB,
        nullable=False,
        default=list,
    )
    createdAt: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
