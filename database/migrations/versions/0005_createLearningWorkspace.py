"""Create Learning Workspace entities."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "learning_goal",
        sa.Column("learning_goal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_learning_context_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("goal_type", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("description", sa.String(length=1500), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("goal_type IN ('TEST','EXAM','REVIEW','PROJECT','COURSE','CERTIFICATION','OTHER')", name="ck_learning_goal_type"),
        sa.CheckConstraint("status IN ('ACTIVE','COMPLETED','CANCELLED','ARCHIVED')", name="ck_learning_goal_status"),
        sa.CheckConstraint("priority BETWEEN 1 AND 5", name="ck_learning_goal_priority"),
        sa.ForeignKeyConstraint(["student_id"], ["lia2.student.student_id"], name="fk_learning_goal_student", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_learning_context_id"], ["lia2.student_learning_context.student_learning_context_id"], name="fk_learning_goal_student_context", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("learning_goal_id", name="pk_learning_goal"),
        schema="lia2",
    )
    op.create_index("ix_learning_goal_student_id", "learning_goal", ["student_id"], schema="lia2")

    op.create_table(
        "study_scope",
        sa.Column("study_scope_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("learning_goal_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=250), nullable=False),
        sa.Column("description", sa.String(length=1500), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('DRAFT','ACTIVE','COMPLETED','ARCHIVED')", name="ck_study_scope_status"),
        sa.ForeignKeyConstraint(["learning_goal_id"], ["lia2.learning_goal.learning_goal_id"], name="fk_study_scope_learning_goal", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("study_scope_id", name="pk_study_scope"),
        schema="lia2",
    )

    op.create_table(
        "study_scope_item",
        sa.Column("study_scope_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("study_scope_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_learning_unit_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=True),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('ACTIVE','REMOVED')", name="ck_study_scope_item_status"),
        sa.ForeignKeyConstraint(["study_scope_id"], ["lia2.study_scope.study_scope_id"], name="fk_study_scope_item_scope", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_learning_unit_id"], ["lia2.student_learning_unit.student_learning_unit_id"], name="fk_study_scope_item_unit", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("study_scope_item_id", name="pk_study_scope_item"),
        sa.UniqueConstraint("study_scope_id", "student_learning_unit_id", name="uq_study_scope_item_unit"),
        schema="lia2",
    )

    op.create_table(
        "study_session",
        sa.Column("study_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("study_scope_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_type", sa.String(length=20), nullable=False, server_default="STUDY"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="IN_PROGRESS"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("session_type IN ('STUDY','REVIEW','PRACTICE','MOCK_EXAM')", name="ck_study_session_type"),
        sa.CheckConstraint("status IN ('IN_PROGRESS','COMPLETED','CANCELLED')", name="ck_study_session_status"),
        sa.ForeignKeyConstraint(["study_scope_id"], ["lia2.study_scope.study_scope_id"], name="fk_study_session_scope", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_id"], ["lia2.student.student_id"], name="fk_study_session_student", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("study_session_id", name="pk_study_session"),
        schema="lia2",
    )

    op.create_table(
        "study_session_item",
        sa.Column("study_session_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("study_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("study_scope_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING"),
        sa.Column("time_spent_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('PENDING','IN_PROGRESS','COMPLETED','SKIPPED')", name="ck_study_session_item_status"),
        sa.CheckConstraint("time_spent_seconds >= 0", name="ck_study_session_item_time"),
        sa.ForeignKeyConstraint(["study_session_id"], ["lia2.study_session.study_session_id"], name="fk_study_session_item_session", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["study_scope_item_id"], ["lia2.study_scope_item.study_scope_item_id"], name="fk_study_session_item_scope_item", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("study_session_item_id", name="pk_study_session_item"),
        sa.UniqueConstraint("study_session_id", "study_scope_item_id", name="uq_study_session_item_scope_item"),
        schema="lia2",
    )

    op.create_table(
        "student_learning_state",
        sa.Column("student_learning_state_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_learning_unit_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="NOT_STARTED"),
        sa.Column("mastery_level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confidence_level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("study_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_studied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("status IN ('NOT_STARTED','LEARNING','REVIEWING','MASTERED')", name="ck_student_learning_state_status"),
        sa.CheckConstraint("mastery_level BETWEEN 0 AND 100", name="ck_student_learning_state_mastery"),
        sa.CheckConstraint("confidence_level BETWEEN 0 AND 100", name="ck_student_learning_state_confidence"),
        sa.CheckConstraint("study_count >= 0", name="ck_student_learning_state_study_count"),
        sa.ForeignKeyConstraint(["student_id"], ["lia2.student.student_id"], name="fk_student_learning_state_student", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_learning_unit_id"], ["lia2.student_learning_unit.student_learning_unit_id"], name="fk_student_learning_state_unit", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("student_learning_state_id", name="pk_student_learning_state"),
        sa.UniqueConstraint("student_learning_unit_id", name="uq_student_learning_state_unit"),
        schema="lia2",
    )

def downgrade() -> None:
    op.drop_table("student_learning_state", schema="lia2")
    op.drop_table("study_session_item", schema="lia2")
    op.drop_table("study_session", schema="lia2")
    op.drop_table("study_scope_item", schema="lia2")
    op.drop_table("study_scope", schema="lia2")
    op.drop_index("ix_learning_goal_student_id", table_name="learning_goal", schema="lia2")
    op.drop_table("learning_goal", schema="lia2")
