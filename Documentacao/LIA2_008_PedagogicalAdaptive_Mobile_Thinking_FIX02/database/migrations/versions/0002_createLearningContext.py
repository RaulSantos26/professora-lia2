"""Create LearningContext and StudentLearningContext."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "learning_context",
        sa.Column(
            "learning_context_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("context_type", sa.String(length=40), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("starts_at", sa.Date(), nullable=True),
        sa.Column("ends_at", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "context_type IN ("
            "'REGULAR_EDUCATION', 'ENEM', 'VESTIBULAR', 'PUBLIC_EXAM', "
            "'GRADUATION', 'POSTGRAD', 'FREE_COURSE', 'OTHER'"
            ")",
            name="ck_learning_context_type",
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_learning_context_status",
        ),
        sa.CheckConstraint(
            "ends_at IS NULL OR starts_at IS NULL OR ends_at >= starts_at",
            name="ck_learning_context_dates",
        ),
        sa.PrimaryKeyConstraint(
            "learning_context_id",
            name="pk_learning_context",
        ),
        sa.UniqueConstraint(
            "code",
            name="uq_learning_context_code",
        ),
        schema="lia2",
    )

    op.create_table(
        "student_learning_context",
        sa.Column(
            "student_learning_context_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "learning_context_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "academic_stage_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column(
            "enrolled_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE', 'COMPLETED')",
            name="ck_student_learning_context_status",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["lia2.student.student_id"],
            name="fk_student_learning_context_student",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["learning_context_id"],
            ["lia2.learning_context.learning_context_id"],
            name="fk_student_learning_context_context",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["academic_stage_id"],
            ["lia2.academic_stage.academic_stage_id"],
            name="fk_student_learning_context_academic_stage",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "student_learning_context_id",
            name="pk_student_learning_context",
        ),
        schema="lia2",
    )

    op.create_index(
        "ix_student_learning_context_student_id",
        "student_learning_context",
        ["student_id"],
        unique=False,
        schema="lia2",
    )

    op.create_index(
        "ix_student_learning_context_learning_context_id",
        "student_learning_context",
        ["learning_context_id"],
        unique=False,
        schema="lia2",
    )

    op.create_index(
        "uq_student_learning_context_active",
        "student_learning_context",
        ["student_id", "learning_context_id"],
        unique=True,
        schema="lia2",
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_student_learning_context_active",
        table_name="student_learning_context",
        schema="lia2",
    )
    op.drop_index(
        "ix_student_learning_context_learning_context_id",
        table_name="student_learning_context",
        schema="lia2",
    )
    op.drop_index(
        "ix_student_learning_context_student_id",
        table_name="student_learning_context",
        schema="lia2",
    )
    op.drop_table("student_learning_context", schema="lia2")
    op.drop_table("learning_context", schema="lia2")
