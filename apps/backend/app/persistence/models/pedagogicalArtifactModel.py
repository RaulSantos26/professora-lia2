from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class PedagogicalArtifactModel(BaseModel):
    __tablename__ = "pedagogical_artifact"
    __table_args__ = (
        CheckConstraint(
            "artifact_type IN ("
            "'TEACH','EXPLAIN','SUMMARY','MIND_MAP',"
            "'FLASHCARDS','EXERCISES','QUIZ'"
            ")",
            name="ck_pedagogical_artifact_type",
        ),
        CheckConstraint(
            "status IN ('QUEUED','RUNNING','READY','FAILED','ARCHIVED')",
            name="ck_pedagogical_artifact_status",
        ),
        CheckConstraint(
            "progress_percent BETWEEN 0 AND 100",
            name="ck_pedagogical_artifact_progress",
        ),
        CheckConstraint(
            "difficulty IS NULL OR difficulty IN ('AUTO','EASY','MEDIUM','HARD')",
            name="ck_pedagogical_artifact_difficulty",
        ),
        CheckConstraint(
            "thinking_mode IN ('AUTO','ON','OFF')",
            name="ck_pedagogical_artifact_thinking_mode",
        ),
        {"schema": "lia2"},
    )

    pedagogicalArtifactId: Mapped[UUID] = mapped_column(
        "pedagogical_artifact_id",
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
    studentLearningContextId: Mapped[UUID | None] = mapped_column("student_learning_context_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.student_learning_context.student_learning_context_id", ondelete="RESTRICT"), nullable=True, index=True)
    studentSubjectId: Mapped[UUID | None] = mapped_column("student_subject_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.student_subject.student_subject_id", ondelete="RESTRICT"), nullable=True, index=True)
    studentLearningUnitId: Mapped[UUID | None] = mapped_column("student_learning_unit_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.student_learning_unit.student_learning_unit_id", ondelete="RESTRICT"), nullable=True, index=True)
    artifactType: Mapped[str] = mapped_column(
        "artifact_type",
        String(30),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
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
        default="Na fila para geração.",
    )
    title: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )
    instruction: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )
    difficulty: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    questionCount: Mapped[int | None] = mapped_column(
        "question_count",
        Integer,
        nullable=True,
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
    sourceMaterialIds: Mapped[list] = mapped_column(
        "source_material_ids",
        JSONB,
        nullable=False,
        default=list,
    )
    sourceEvidenceJson: Mapped[list] = mapped_column(
        "source_evidence_json",
        JSONB,
        nullable=False,
        default=list,
    )
    contentJson: Mapped[dict | None] = mapped_column(
        "content_json",
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
