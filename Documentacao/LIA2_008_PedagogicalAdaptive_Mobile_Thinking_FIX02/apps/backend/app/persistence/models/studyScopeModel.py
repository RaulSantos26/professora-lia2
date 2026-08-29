from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column
from app.persistence.models.baseModel import BaseModel

class StudyScopeModel(BaseModel):
    __tablename__ = "study_scope"
    __table_args__ = (
        CheckConstraint("status IN ('DRAFT','ACTIVE','COMPLETED','ARCHIVED')", name="ck_study_scope_status"),
        {"schema": "lia2"},
    )
    studyScopeId: Mapped[UUID] = mapped_column("study_scope_id", PostgresUuid(as_uuid=True), primary_key=True, default=uuid4)
    learningGoalId: Mapped[UUID] = mapped_column("learning_goal_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.learning_goal.learning_goal_id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    createdAt: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
