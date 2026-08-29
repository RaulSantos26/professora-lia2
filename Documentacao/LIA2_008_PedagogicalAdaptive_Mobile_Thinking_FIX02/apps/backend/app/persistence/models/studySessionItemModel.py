from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column
from app.persistence.models.baseModel import BaseModel

class StudySessionItemModel(BaseModel):
    __tablename__ = "study_session_item"
    __table_args__ = (
        CheckConstraint("status IN ('PENDING','IN_PROGRESS','COMPLETED','SKIPPED')", name="ck_study_session_item_status"),
        CheckConstraint("time_spent_seconds >= 0", name="ck_study_session_item_time"),
        UniqueConstraint("study_session_id", "study_scope_item_id", name="uq_study_session_item_scope_item"),
        {"schema": "lia2"},
    )
    studySessionItemId: Mapped[UUID] = mapped_column("study_session_item_id", PostgresUuid(as_uuid=True), primary_key=True, default=uuid4)
    studySessionId: Mapped[UUID] = mapped_column("study_session_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.study_session.study_session_id", ondelete="RESTRICT"), nullable=False, index=True)
    studyScopeItemId: Mapped[UUID] = mapped_column("study_scope_item_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.study_scope_item.study_scope_item_id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    timeSpentSeconds: Mapped[int] = mapped_column("time_spent_seconds", Integer, nullable=False, default=0)
    startedAt: Mapped[datetime | None] = mapped_column("started_at", DateTime(timezone=True), nullable=True)
    completedAt: Mapped[datetime | None] = mapped_column("completed_at", DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    createdAt: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
