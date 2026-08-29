from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class VisualTaskModel(BaseModel):
    __tablename__ = "visual_task"
    __table_args__ = (
        CheckConstraint(
            "visual_type IN ("
            "'MIND_MAP','DIAGRAM','CHART','ANIMATION_2D','SCENE_3D'"
            ")",
            name="ck_visual_task_type",
        ),
        CheckConstraint(
            "renderer IN ('SVG','CANVAS','THREE')",
            name="ck_visual_task_renderer",
        ),
        CheckConstraint(
            "status IN ('READY','ARCHIVED')",
            name="ck_visual_task_status",
        ),
        {"schema": "lia2"},
    )

    visualTaskId: Mapped[UUID] = mapped_column(
        "visual_task_id",
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
    agentThreadId: Mapped[UUID | None] = mapped_column(
        "agent_thread_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.agent_thread.agent_thread_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    agentRunId: Mapped[UUID | None] = mapped_column(
        "agent_run_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.agent_run.agent_run_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    pedagogicalArtifactId: Mapped[UUID | None] = mapped_column(
        "pedagogical_artifact_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.pedagogical_artifact.pedagogical_artifact_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    visualType: Mapped[str] = mapped_column(
        "visual_type",
        String(30),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="READY",
    )
    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )
    renderer: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    specJson: Mapped[dict] = mapped_column(
        "spec_json",
        JSONB,
        nullable=False,
    )
    evidenceJson: Mapped[list] = mapped_column(
        "evidence_json",
        JSONB,
        nullable=False,
        default=list,
    )
    sourceMaterialIds: Mapped[list] = mapped_column(
        "source_material_ids",
        JSONB,
        nullable=False,
        default=list,
    )
    effectiveModelId: Mapped[str | None] = mapped_column(
        "effective_model_id",
        String(300),
        nullable=True,
    )
    thinkingEnabled: Mapped[bool | None] = mapped_column(
        "thinking_enabled",
        Boolean,
        nullable=True,
    )
    createdAt: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
