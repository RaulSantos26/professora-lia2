"""Create student-specific subject and learning unit ownership."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_subject",
        sa.Column(
            "student_subject_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "student_learning_context_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "subject_definition_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
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
            "status IN ('ACTIVE', 'INACTIVE', 'ARCHIVED')",
            name="ck_student_subject_status",
        ),
        sa.ForeignKeyConstraint(
            ["student_learning_context_id"],
            ["lia2.student_learning_context.student_learning_context_id"],
            name="fk_student_subject_student_learning_context",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["subject_definition_id"],
            ["lia2.subject.subject_id"],
            name="fk_student_subject_subject_definition",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "student_subject_id",
            name="pk_student_subject",
        ),
        sa.UniqueConstraint(
            "student_learning_context_id",
            "code",
            name="uq_student_subject_code_per_context",
        ),
        schema="lia2",
    )

    op.create_index(
        "ix_student_subject_context_id",
        "student_subject",
        ["student_learning_context_id"],
        unique=False,
        schema="lia2",
    )

    op.create_table(
        "student_learning_unit",
        sa.Column(
            "student_learning_unit_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "student_subject_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "parent_student_learning_unit_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("unit_type", sa.String(length=20), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("description", sa.String(length=1500), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=True),
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
            "unit_type IN ('LESSON', 'MODULE', 'CHAPTER', 'SECTION')",
            name="ck_student_learning_unit_type",
        ),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'ACTIVE', 'INACTIVE', 'ARCHIVED')",
            name="ck_student_learning_unit_status",
        ),
        sa.ForeignKeyConstraint(
            ["student_subject_id"],
            ["lia2.student_subject.student_subject_id"],
            name="fk_student_learning_unit_subject",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["parent_student_learning_unit_id"],
            ["lia2.student_learning_unit.student_learning_unit_id"],
            name="fk_student_learning_unit_parent",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "student_learning_unit_id",
            name="pk_student_learning_unit",
        ),
        sa.UniqueConstraint(
            "student_subject_id",
            "code",
            name="uq_student_learning_unit_code_per_subject",
        ),
        schema="lia2",
    )

    op.create_index(
        "ix_student_learning_unit_subject_id",
        "student_learning_unit",
        ["student_subject_id"],
        unique=False,
        schema="lia2",
    )

    # No automatic legacy-content backfill.
    # Ownership cannot be inferred safely across Students.


def downgrade() -> None:
    op.drop_index(
        "ix_student_learning_unit_subject_id",
        table_name="student_learning_unit",
        schema="lia2",
    )
    op.drop_table("student_learning_unit", schema="lia2")
    op.drop_index(
        "ix_student_subject_context_id",
        table_name="student_subject",
        schema="lia2",
    )
    op.drop_table("student_subject", schema="lia2")
