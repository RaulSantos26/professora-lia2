"""Create persistent Z-Image generation tasks."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("agent_message", sa.Column("image_task_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")), schema="lia2")
    op.create_table(
        "image_generation_task",
        sa.Column("image_task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_thread_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("related_visual_task_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("image_mode", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="QUEUED"),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("message", sa.String(length=500), nullable=False, server_default="Imagem aguardando a vez na GPU."),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("labels_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("evidence_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("source_material_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("asset_filename", sa.String(length=300), nullable=True),
        sa.Column("seed", sa.Integer(), nullable=True),
        sa.Column("elapsed_seconds", sa.Float(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("image_mode IN ('ILLUSTRATION','MIND_MAP_COMPANION')", name="ck_image_generation_task_mode"),
        sa.CheckConstraint("status IN ('QUEUED','PREPARING','GENERATING','LABELING','READY','ERROR','CANCELLED')", name="ck_image_generation_task_status"),
        sa.CheckConstraint("progress_percent BETWEEN 0 AND 100", name="ck_image_generation_task_progress"),
        sa.ForeignKeyConstraint(["student_id"], ["lia2.student.student_id"], name="fk_image_generation_task_student", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["agent_thread_id"], ["lia2.agent_thread.agent_thread_id"], name="fk_image_generation_task_thread", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["agent_run_id"], ["lia2.agent_run.agent_run_id"], name="fk_image_generation_task_run", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["related_visual_task_id"], ["lia2.visual_task.visual_task_id"], name="fk_image_generation_task_visual", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("image_task_id", name="pk_image_generation_task"),
        schema="lia2",
    )
    op.create_index("ix_image_generation_task_status_created", "image_generation_task", ["status", "created_at"], schema="lia2")
    op.create_index("ix_image_generation_task_student_created", "image_generation_task", ["student_id", "created_at"], schema="lia2")


def downgrade() -> None:
    op.drop_index("ix_image_generation_task_student_created", table_name="image_generation_task", schema="lia2")
    op.drop_index("ix_image_generation_task_status_created", table_name="image_generation_task", schema="lia2")
    op.drop_table("image_generation_task", schema="lia2")
    op.drop_column("agent_message", "image_task_ids", schema="lia2")
