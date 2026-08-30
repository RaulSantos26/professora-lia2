from datetime import date, datetime
from uuid import UUID, uuid4
from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column
from app.persistence.models.baseModel import BaseModel

class LearningGoalModel(BaseModel):
    __tablename__ = "learning_goal"
    __table_args__ = (
        CheckConstraint("goal_type IN ('TEST','EXAM','REVIEW','PROJECT','COURSE','CERTIFICATION','OTHER')", name="ck_learning_goal_type"),
        CheckConstraint("status IN ('ACTIVE','COMPLETED','CANCELLED','ARCHIVED')", name="ck_learning_goal_status"),
        CheckConstraint("priority BETWEEN 1 AND 5", name="ck_learning_goal_priority"),
        {"schema": "lia2"},
    )
    learningGoalId: Mapped[UUID] = mapped_column("learning_goal_id", PostgresUuid(as_uuid=True), primary_key=True, default=uuid4)
    studentId: Mapped[UUID] = mapped_column("student_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.student.student_id", ondelete="RESTRICT"), nullable=False, index=True)
    studentLearningContextId: Mapped[UUID | None] = mapped_column("student_learning_context_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.student_learning_context.student_learning_context_id", ondelete="RESTRICT"), nullable=True, index=True)
    studentSubjectId: Mapped[UUID | None] = mapped_column("student_subject_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.student_subject.student_subject_id", ondelete="RESTRICT"), nullable=True, index=True)
    goalType: Mapped[str] = mapped_column("goal_type", String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1500), nullable=True)
    targetDate: Mapped[date | None] = mapped_column("target_date", Date, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    completedAt: Mapped[datetime | None] = mapped_column("completed_at", DateTime(timezone=True), nullable=True)
    createdAt: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
