from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class LearningAttemptModel(BaseModel):
    __tablename__ = "learning_attempt"
    __table_args__ = (
        CheckConstraint(
            "attempt_type IN ('EXERCISES','QUIZ')",
            name="ck_learning_attempt_type",
        ),
        CheckConstraint(
            "score_percent BETWEEN 0 AND 100",
            name="ck_learning_attempt_score",
        ),
        CheckConstraint(
            "correct_count >= 0 AND total_count >= 1 "
            "AND correct_count <= total_count",
            name="ck_learning_attempt_counts",
        ),
        {"schema": "lia2"},
    )

    learningAttemptId: Mapped[UUID] = mapped_column(
        "learning_attempt_id",
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
    pedagogicalArtifactId: Mapped[UUID] = mapped_column(
        "pedagogical_artifact_id",
        PostgresUuid(as_uuid=True),
        ForeignKey(
            "lia2.pedagogical_artifact.pedagogical_artifact_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    attemptType: Mapped[str] = mapped_column(
        "attempt_type",
        String(20),
        nullable=False,
    )
    scorePercent: Mapped[int] = mapped_column(
        "score_percent",
        Integer,
        nullable=False,
    )
    correctCount: Mapped[int] = mapped_column(
        "correct_count",
        Integer,
        nullable=False,
    )
    totalCount: Mapped[int] = mapped_column(
        "total_count",
        Integer,
        nullable=False,
    )
    submittedAnswers: Mapped[dict] = mapped_column(
        "submitted_answers",
        JSONB,
        nullable=False,
    )
    resultJson: Mapped[dict] = mapped_column(
        "result_json",
        JSONB,
        nullable=False,
    )
    createdAt: Mapped[datetime] = mapped_column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    completedAt: Mapped[datetime] = mapped_column(
        "completed_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
