"""Create lia2 Student and AcademicStage foundation."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS lia2")

    op.create_table(
        "student",
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("preferred_name", sa.String(length=120), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="ACTIVE",
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
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_student_status",
        ),
        sa.PrimaryKeyConstraint("student_id", name="pk_student"),
        schema="lia2",
    )

    op.create_index(
        "ix_student_full_name",
        "student",
        ["full_name"],
        unique=False,
        schema="lia2",
    )

    op.create_table(
        "academic_stage",
        sa.Column(
            "academic_stage_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("education_level", sa.String(length=80), nullable=False),
        sa.Column("stage_code", sa.String(length=80), nullable=True),
        sa.Column("stage_label", sa.String(length=160), nullable=False),
        sa.Column("started_at", sa.Date(), nullable=True),
        sa.Column("ended_at", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="CURRENT",
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
            "status IN ('CURRENT', 'COMPLETED', 'CANCELLED')",
            name="ck_academic_stage_status",
        ),
        sa.CheckConstraint(
            "ended_at IS NULL OR started_at IS NULL OR ended_at >= started_at",
            name="ck_academic_stage_dates",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["lia2.student.student_id"],
            name="fk_academic_stage_student",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "academic_stage_id",
            name="pk_academic_stage",
        ),
        schema="lia2",
    )

    op.create_index(
        "ix_academic_stage_student_id",
        "academic_stage",
        ["student_id"],
        unique=False,
        schema="lia2",
    )

    op.create_index(
        "uq_academic_stage_current_per_student",
        "academic_stage",
        ["student_id"],
        unique=True,
        schema="lia2",
        postgresql_where=sa.text("status = 'CURRENT'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_academic_stage_current_per_student",
        table_name="academic_stage",
        schema="lia2",
    )
    op.drop_index(
        "ix_academic_stage_student_id",
        table_name="academic_stage",
        schema="lia2",
    )
    op.drop_table("academic_stage", schema="lia2")
    op.drop_index(
        "ix_student_full_name",
        table_name="student",
        schema="lia2",
    )
    op.drop_table("student", schema="lia2")
    op.execute("DROP SCHEMA IF EXISTS lia2")
