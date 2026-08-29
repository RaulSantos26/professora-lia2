from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column
from app.persistence.models.baseModel import BaseModel

class StudySessionModel(BaseModel):
    __tablename__ = "study_session"
    __table_args__ = (
        CheckConstraint("session_type IN ('STUDY','REVIEW','PRACTICE','MOCK_EXAM')", name="ck_study_session_type"),
        CheckConstraint("status IN ('IN_PROGRESS','COMPLETED','CANCELLED')", name="ck_study_session_status"),
        {"schema": "lia2"},
    )
    studySessionId: Mapped[UUID] = mapped_column("study_session_id", PostgresUuid(as_uuid=True), primary_key=True, default=uuid4)
    studyScopeId: Mapped[UUID] = mapped_column("study_scope_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.study_scope.study_scope_id", ondelete="RESTRICT"), nullable=False, index=True)
    studentId: Mapped[UUID] = mapped_column("student_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.student.student_id", ondelete="RESTRICT"), nullable=False, index=True)
    sessionType: Mapped[str] = mapped_column("session_type", String(20), nullable=False, default="STUDY")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="IN_PROGRESS")
    startedAt: Mapped[datetime] = mapped_column("started_at", DateTime(timezone=True), nullable=False, server_default=func.now())
    endedAt: Mapped[datetime | None] = mapped_column("ended_at", DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    createdAt: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
