from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column
from app.persistence.models.baseModel import BaseModel

class StudentLearningStateModel(BaseModel):
    __tablename__ = "student_learning_state"
    __table_args__ = (
        CheckConstraint("status IN ('NOT_STARTED','LEARNING','REVIEWING','MASTERED')", name="ck_student_learning_state_status"),
        CheckConstraint("mastery_level BETWEEN 0 AND 100", name="ck_student_learning_state_mastery"),
        CheckConstraint("confidence_level BETWEEN 0 AND 100", name="ck_student_learning_state_confidence"),
        CheckConstraint("study_count >= 0", name="ck_student_learning_state_study_count"),
        UniqueConstraint("student_learning_unit_id", name="uq_student_learning_state_unit"),
        {"schema": "lia2"},
    )
    studentLearningStateId: Mapped[UUID] = mapped_column("student_learning_state_id", PostgresUuid(as_uuid=True), primary_key=True, default=uuid4)
    studentId: Mapped[UUID] = mapped_column("student_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.student.student_id", ondelete="RESTRICT"), nullable=False, index=True)
    studentLearningUnitId: Mapped[UUID] = mapped_column("student_learning_unit_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.student_learning_unit.student_learning_unit_id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="NOT_STARTED")
    masteryLevel: Mapped[int] = mapped_column("mastery_level", Integer, nullable=False, default=0)
    confidenceLevel: Mapped[int] = mapped_column("confidence_level", Integer, nullable=False, default=0)
    studyCount: Mapped[int] = mapped_column("study_count", Integer, nullable=False, default=0)
    lastStudiedAt: Mapped[datetime | None] = mapped_column("last_studied_at", DateTime(timezone=True), nullable=True)
    nextReviewAt: Mapped[datetime | None] = mapped_column("next_review_at", DateTime(timezone=True), nullable=True)
    createdAt: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
