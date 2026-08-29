"""Create Subject, LearningContextSubject and LearningUnit."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "subject",
        sa.Column(
            "subject_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
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
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_subject_status",
        ),
        sa.PrimaryKeyConstraint("subject_id", name="pk_subject"),
        sa.UniqueConstraint("code", name="uq_subject_code"),
        schema="lia2",
    )

    op.create_table(
        "learning_context_subject",
        sa.Column(
            "learning_context_subject_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "learning_context_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "subject_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
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
            "status IN ('ACTIVE', 'INACTIVE')",
            name="ck_learning_context_subject_status",
        ),
        sa.ForeignKeyConstraint(
            ["learning_context_id"],
            ["lia2.learning_context.learning_context_id"],
            name="fk_learning_context_subject_context",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["lia2.subject.subject_id"],
            name="fk_learning_context_subject_subject",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "learning_context_subject_id",
            name="pk_learning_context_subject",
        ),
        sa.UniqueConstraint(
            "learning_context_id",
            "subject_id",
            name="uq_learning_context_subject",
        ),
        schema="lia2",
    )

    op.create_index(
        "ix_learning_context_subject_context_id",
        "learning_context_subject",
        ["learning_context_id"],
        unique=False,
        schema="lia2",
    )

    op.create_index(
        "ix_learning_context_subject_subject_id",
        "learning_context_subject",
        ["subject_id"],
        unique=False,
        schema="lia2",
    )

    op.create_table(
        "learning_unit",
        sa.Column(
            "learning_unit_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "learning_context_subject_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "parent_learning_unit_id",
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
            name="ck_learning_unit_type",
        ),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'ACTIVE', 'INACTIVE', 'ARCHIVED')",
            name="ck_learning_unit_status",
        ),
        sa.ForeignKeyConstraint(
            ["learning_context_subject_id"],
            ["lia2.learning_context_subject.learning_context_subject_id"],
            name="fk_learning_unit_context_subject",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["parent_learning_unit_id"],
            ["lia2.learning_unit.learning_unit_id"],
            name="fk_learning_unit_parent",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "learning_unit_id",
            name="pk_learning_unit",
        ),
        sa.UniqueConstraint(
            "learning_context_subject_id",
            "code",
            name="uq_learning_unit_code_per_context_subject",
        ),
        schema="lia2",
    )

    op.create_index(
        "ix_learning_unit_context_subject_id",
        "learning_unit",
        ["learning_context_subject_id"],
        unique=False,
        schema="lia2",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_learning_unit_context_subject_id",
        table_name="learning_unit",
        schema="lia2",
    )
    op.drop_table("learning_unit", schema="lia2")
    op.drop_index(
        "ix_learning_context_subject_subject_id",
        table_name="learning_context_subject",
        schema="lia2",
    )
    op.drop_index(
        "ix_learning_context_subject_context_id",
        table_name="learning_context_subject",
        schema="lia2",
    )
    op.drop_table("learning_context_subject", schema="lia2")
    op.drop_table("subject", schema="lia2")
