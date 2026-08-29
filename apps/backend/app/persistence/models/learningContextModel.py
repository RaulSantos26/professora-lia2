from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUuid
from sqlalchemy.orm import Mapped, mapped_column

from app.persistence.models.baseModel import BaseModel


class LearningContextModel(BaseModel):
    __tablename__ = "learning_context"
    __table_args__ = (
        CheckConstraint(
            "context_type IN ("
            "'REGULAR_EDUCATION', 'ENEM', 'VESTIBULAR', 'PUBLIC_EXAM', "
            "'GRADUATION', 'POSTGRAD', 'FREE_COURSE', 'OTHER'"
            ")",
            name="ck_learning_context_type",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_learning_context_status",
        ),
        CheckConstraint(
            "ends_at IS NULL OR starts_at IS NULL OR ends_at >= starts_at",
            name="ck_learning_context_dates",
        ),
        UniqueConstraint(
            "code",
            name="uq_learning_context_code",
        ),
        {"schema": "lia2"},
    )

    learningContextId: Mapped[UUID] = mapped_column(
        "learning_context_id",
        PostgresUuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    contextType: Mapped[str] = mapped_column(
        "context_type",
        String(40),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
    )
    startsAt: Mapped[date | None] = mapped_column(
        "starts_at",
        Date,
        nullable=True,
    )
    endsAt: Mapped[date | None] = mapped_column(
        "ends_at",
        Date,
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
