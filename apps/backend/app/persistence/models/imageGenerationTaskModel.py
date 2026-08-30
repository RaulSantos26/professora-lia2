from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class ImageGenerationTaskModel(BaseModel):
    __tablename__ = "image_generation_task"
    __table_args__ = (
        CheckConstraint("image_mode IN ('ILLUSTRATION','MIND_MAP_COMPANION')", name="ck_image_generation_task_mode"),
        CheckConstraint("status IN ('QUEUED','PREPARING','GENERATING','LABELING','READY','ERROR','CANCELLED')", name="ck_image_generation_task_status"),
        CheckConstraint("progress_percent BETWEEN 0 AND 100", name="ck_image_generation_task_progress"),
        {"schema": "lia2"},
    )

    imageTaskId: Mapped[UUID] = mapped_column("image_task_id", PostgresUuid(as_uuid=True), primary_key=True, default=uuid4)
    studentId: Mapped[UUID] = mapped_column("student_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.student.student_id", ondelete="RESTRICT"), nullable=False)
    agentThreadId: Mapped[UUID | None] = mapped_column("agent_thread_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.agent_thread.agent_thread_id", ondelete="SET NULL"), nullable=True)
    agentRunId: Mapped[UUID | None] = mapped_column("agent_run_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.agent_run.agent_run_id", ondelete="SET NULL"), nullable=True)
    relatedVisualTaskId: Mapped[UUID | None] = mapped_column("related_visual_task_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.visual_task.visual_task_id", ondelete="SET NULL"), nullable=True)
    relatedPedagogicalArtifactId: Mapped[UUID | None] = mapped_column("related_pedagogical_artifact_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.pedagogical_artifact.pedagogical_artifact_id", ondelete="SET NULL"), nullable=True, index=True)
    imageMode: Mapped[str] = mapped_column("image_mode", String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="QUEUED")
    progressPercent: Mapped[int] = mapped_column("progress_percent", Integer, nullable=False, default=5)
    message: Mapped[str] = mapped_column(String(500), nullable=False, default="Imagem aguardando a vez na GPU.")
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    labelsJson: Mapped[list] = mapped_column("labels_json", JSONB, nullable=False, default=list)
    evidenceJson: Mapped[list] = mapped_column("evidence_json", JSONB, nullable=False, default=list)
    sourceMaterialIds: Mapped[list] = mapped_column("source_material_ids", JSONB, nullable=False, default=list)
    assetFilename: Mapped[str | None] = mapped_column("asset_filename", String(300), nullable=True)
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    elapsedSeconds: Mapped[float | None] = mapped_column("elapsed_seconds", Float, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    errorCode: Mapped[str | None] = mapped_column("error_code", String(100), nullable=True)
    errorMessage: Mapped[str | None] = mapped_column("error_message", String(1000), nullable=True)
    createdAt: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now())
    startedAt: Mapped[datetime | None] = mapped_column("started_at", DateTime(timezone=True), nullable=True)
    finishedAt: Mapped[datetime | None] = mapped_column("finished_at", DateTime(timezone=True), nullable=True)
