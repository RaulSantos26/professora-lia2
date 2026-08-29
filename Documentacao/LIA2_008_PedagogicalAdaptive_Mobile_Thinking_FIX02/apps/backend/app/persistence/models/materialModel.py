from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class MaterialModel(BaseModel):
    __tablename__ = "material"
    __table_args__ = (
        CheckConstraint(
            "material_type IN ('PDF','IMAGE','TEXT','DOCUMENT','OTHER')",
            name="ck_material_type",
        ),
        CheckConstraint(
            "source_type IN ('UPLOAD','MANUAL','LINK')",
            name="ck_material_source_type",
        ),
        CheckConstraint(
            "status IN ('UPLOADED','PROCESSING','PARTIAL','READY','ERROR','ARCHIVED')",
            name="ck_material_status",
        ),
        CheckConstraint(
            "ai_mode IN ('AUTO','FIXED','CUSTOM')",
            name="ck_material_ai_mode",
        ),
        CheckConstraint(
            "source_sequence IS NULL OR source_sequence >= 1",
            name="ck_material_source_sequence",
        ),
        CheckConstraint(
            "thinking_mode IN ('AUTO','ON','OFF')",
            name="ck_material_thinking_mode",
        ),
        {"schema": "lia2"},
    )

    materialId: Mapped[UUID] = mapped_column(
        "material_id",
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
    studentLearningContextId: Mapped[UUID | None] = mapped_column(
        "student_learning_context_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.student_learning_context.student_learning_context_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )
    studentSubjectId: Mapped[UUID | None] = mapped_column(
        "student_subject_id",
        PostgresUuid(as_uuid=True),
        ForeignKey("lia2.student_subject.student_subject_id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    studentLearningUnitId: Mapped[UUID | None] = mapped_column(
        "student_learning_unit_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.student_learning_unit.student_learning_unit_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    materialType: Mapped[str] = mapped_column(
        "material_type",
        String(20),
        nullable=False,
    )
    sourceType: Mapped[str] = mapped_column(
        "source_type",
        String(20),
        nullable=False,
        default="UPLOAD",
    )
    description: Mapped[str | None] = mapped_column(
        String(1500),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="UPLOADED",
    )
    analysisRequested: Mapped[bool] = mapped_column(
        "analysis_requested",
        Boolean,
        nullable=False,
        default=True,
    )
    studyEnabled: Mapped[bool] = mapped_column(
        "study_enabled",
        Boolean,
        nullable=False,
        default=True,
    )
    requestedModelId: Mapped[str | None] = mapped_column(
        "requested_model_id",
        String(300),
        nullable=True,
    )
    aiMode: Mapped[str] = mapped_column(
        "ai_mode",
        String(20),
        nullable=False,
        default="AUTO",
    )
    fixedModelId: Mapped[str | None] = mapped_column(
        "fixed_model_id",
        String(300),
        nullable=True,
    )
    textModelId: Mapped[str | None] = mapped_column(
        "text_model_id",
        String(300),
        nullable=True,
    )
    visionModelId: Mapped[str | None] = mapped_column(
        "vision_model_id",
        String(300),
        nullable=True,
    )
    embeddingModelId: Mapped[str | None] = mapped_column(
        "embedding_model_id",
        String(300),
        nullable=True,
    )
    thinkingMode: Mapped[str] = mapped_column(
        "thinking_mode",
        String(10),
        nullable=False,
        default="AUTO",
    )
    sourceGroupId: Mapped[UUID | None] = mapped_column(
        "source_group_id",
        PostgresUuid(as_uuid=True),
        nullable=True,
        index=True,
    )
    sourceSequence: Mapped[int | None] = mapped_column(
        "source_sequence",
        Integer,
        nullable=True,
    )
    lastProcessingErrorCode: Mapped[str | None] = mapped_column(
        "last_processing_error_code",
        String(100),
        nullable=True,
    )
    lastProcessingErrorMessage: Mapped[str | None] = mapped_column(
        "last_processing_error_message",
        String(1000),
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
