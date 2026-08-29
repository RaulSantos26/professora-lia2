from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class MaterialProcessingJobModel(BaseModel):
    __tablename__ = "material_processing_job"
    __table_args__ = (
        CheckConstraint(
            "job_type IN ('ANALYZE','INDEX_RAG')",
            name="ck_material_processing_job_type",
        ),
        CheckConstraint(
            "status IN ('QUEUED','RUNNING','COMPLETED','COMPLETED_WITH_WARNINGS','FAILED','CANCELLED')",
            name="ck_material_processing_job_status",
        ),
        CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name="ck_material_processing_job_progress",
        ),
        {"schema": "lia2"},
    )

    materialProcessingJobId: Mapped[UUID] = mapped_column(
        "material_processing_job_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    materialId: Mapped[UUID] = mapped_column(
        "material_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.material.material_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    studentId: Mapped[UUID] = mapped_column(
        "student_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.student.student_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    jobType: Mapped[str] = mapped_column(
        "job_type",
        String(30),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
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
        default="Na fila para processamento.",
    )
    requestedModelId: Mapped[str | None] = mapped_column(
        "requested_model_id",
        String(300),
        nullable=True,
    )
    effectiveVisionModelId: Mapped[str | None] = mapped_column(
        "effective_vision_model_id",
        String(300),
        nullable=True,
    )
    effectiveEmbeddingModelId: Mapped[str | None] = mapped_column(
        "effective_embedding_model_id",
        String(300),
        nullable=True,
    )
    fallbackReason: Mapped[str | None] = mapped_column(
        "fallback_reason",
        String(1000),
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
