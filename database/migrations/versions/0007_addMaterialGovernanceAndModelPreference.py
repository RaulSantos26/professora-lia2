"""Add material governance, processing preference and model selection."""

from alembic import op
import sqlalchemy as sa


revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "material",
        sa.Column(
            "analysis_requested",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        schema="lia2",
    )
    op.add_column(
        "material",
        sa.Column(
            "study_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        schema="lia2",
    )
    op.add_column(
        "material",
        sa.Column(
            "requested_model_id",
            sa.String(length=300),
            nullable=True,
        ),
        schema="lia2",
    )
    op.add_column(
        "material",
        sa.Column(
            "last_processing_error_code",
            sa.String(length=100),
            nullable=True,
        ),
        schema="lia2",
    )
    op.add_column(
        "material",
        sa.Column(
            "last_processing_error_message",
            sa.String(length=1000),
            nullable=True,
        ),
        schema="lia2",
    )

    op.create_index(
        "ix_material_study_enabled",
        "material",
        ["study_enabled"],
        schema="lia2",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_material_study_enabled",
        table_name="material",
        schema="lia2",
    )
    op.drop_column("material", "last_processing_error_message", schema="lia2")
    op.drop_column("material", "last_processing_error_code", schema="lia2")
    op.drop_column("material", "requested_model_id", schema="lia2")
    op.drop_column("material", "study_enabled", schema="lia2")
    op.drop_column("material", "analysis_requested", schema="lia2")
