from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column
from app.persistence.models.baseModel import BaseModel

class StudyScopeItemModel(BaseModel):
    __tablename__ = "study_scope_item"
    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE','REMOVED')", name="ck_study_scope_item_status"),
        UniqueConstraint("study_scope_id", "student_learning_unit_id", name="uq_study_scope_item_unit"),
        {"schema": "lia2"},
    )
    studyScopeItemId: Mapped[UUID] = mapped_column("study_scope_item_id", PostgresUuid(as_uuid=True), primary_key=True, default=uuid4)
    studyScopeId: Mapped[UUID] = mapped_column("study_scope_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.study_scope.study_scope_id", ondelete="RESTRICT"), nullable=False, index=True)
    studentLearningUnitId: Mapped[UUID] = mapped_column("student_learning_unit_id", PostgresUuid(as_uuid=True), ForeignKey("lia2.student_learning_unit.student_learning_unit_id", ondelete="RESTRICT"), nullable=False, index=True)
    displayOrder: Mapped[int | None] = mapped_column("display_order", Integer, nullable=True)
    isRequired: Mapped[bool] = mapped_column("is_required", Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    createdAt: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now())
    updatedAt: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
