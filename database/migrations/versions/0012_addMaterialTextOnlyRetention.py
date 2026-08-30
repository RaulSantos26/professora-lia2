"""Track text-only retention for new image materials."""

from alembic import op
import sqlalchemy as sa


revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "material",
        sa.Column(
            "source_file_retained",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        schema="lia2",
    )
    op.add_column(
        "material",
        sa.Column(
            "discard_source_after_extraction",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        schema="lia2",
    )


def downgrade():
    op.drop_column(
        "material",
        "discard_source_after_extraction",
        schema="lia2",
    )
    op.drop_column(
        "material", "source_file_retained", schema="lia2"
    )