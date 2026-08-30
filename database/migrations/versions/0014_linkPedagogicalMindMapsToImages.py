"""Link interactive mind maps to their Z-Image companion tasks."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "pedagogical_artifact",
        sa.Column("image_task_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema="lia2",
    )
    op.add_column(
        "image_generation_task",
        sa.Column(
            "related_pedagogical_artifact_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        schema="lia2",
    )
    op.create_foreign_key(
        "fk_pedagogical_artifact_image_task",
        "pedagogical_artifact",
        "image_generation_task",
        ["image_task_id"],
        ["image_task_id"],
        source_schema="lia2",
        referent_schema="lia2",
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_image_generation_task_pedagogical",
        "image_generation_task",
        "pedagogical_artifact",
        ["related_pedagogical_artifact_id"],
        ["pedagogical_artifact_id"],
        source_schema="lia2",
        referent_schema="lia2",
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_pedagogical_artifact_image_task",
        "pedagogical_artifact",
        ["image_task_id"],
        schema="lia2",
    )
    op.create_index(
        "ix_image_generation_task_pedagogical",
        "image_generation_task",
        ["related_pedagogical_artifact_id"],
        schema="lia2",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_image_generation_task_pedagogical",
        table_name="image_generation_task",
        schema="lia2",
    )
    op.drop_index(
        "ix_pedagogical_artifact_image_task",
        table_name="pedagogical_artifact",
        schema="lia2",
    )
    op.drop_constraint(
        "fk_image_generation_task_pedagogical",
        "image_generation_task",
        schema="lia2",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_pedagogical_artifact_image_task",
        "pedagogical_artifact",
        schema="lia2",
        type_="foreignkey",
    )
    op.drop_column(
        "image_generation_task",
        "related_pedagogical_artifact_id",
        schema="lia2",
    )
    op.drop_column(
        "pedagogical_artifact",
        "image_task_id",
        schema="lia2",
    )
