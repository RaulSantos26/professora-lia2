from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class AcademicStageModel(BaseModel):
    __tablename__ = "academic_stage"
    __table_args__ = (
        CheckConstraint(
            "status IN ('CURRENT', 'COMPLETED', 'CANCELLED')",
            name="ck_academic_stage_status",
        ),
        CheckConstraint(
            "ended_at IS NULL OR started_at IS NULL OR ended_at >= started_at",
            name="ck_academic_stage_dates",
        ),
        {"schema": "lia2"},
    )

    academicStageId: Mapped[UUID] = mapped_column(
        "academic_stage_id",
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
    educationLevel: Mapped[str] = mapped_column(
        "education_level",
        String(80),
        nullable=False,
    )
    stageCode: Mapped[str | None] = mapped_column(
        "stage_code",
        String(80),
        nullable=True,
    )
    stageLabel: Mapped[str] = mapped_column(
        "stage_label",
        String(160),
        nullable=False,
    )
    startedAt: Mapped[date | None] = mapped_column(
        "started_at",
        Date,
        nullable=True,
    )
    endedAt: Mapped[date | None] = mapped_column(
        "ended_at",
        Date,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="CURRENT",
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
