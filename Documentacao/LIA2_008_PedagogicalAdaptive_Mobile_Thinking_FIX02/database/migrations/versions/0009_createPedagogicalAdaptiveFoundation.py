"""Create pedagogical artifacts, attempts and explicit AI preferences."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "material",
        sa.Column(
            "ai_mode",
            sa.String(length=20),
            nullable=False,
            server_default="AUTO",
        ),
        schema="lia2",
    )
    op.add_column(
        "material",
        sa.Column(
            "fixed_model_id",
            sa.String(length=300),
            nullable=True,
        ),
        schema="lia2",
    )
    op.add_column(
        "material",
        sa.Column(
            "text_model_id",
            sa.String(length=300),
            nullable=True,
        ),
        schema="lia2",
    )
    op.add_column(
        "material",
        sa.Column(
            "vision_model_id",
            sa.String(length=300),
            nullable=True,
        ),
        schema="lia2",
    )
    op.add_column(
        "material",
        sa.Column(
            "embedding_model_id",
            sa.String(length=300),
            nullable=True,
        ),
        schema="lia2",
    )
    op.add_column(
        "material",
        sa.Column(
            "thinking_mode",
            sa.String(length=10),
            nullable=False,
            server_default="AUTO",
        ),
        schema="lia2",
    )
    op.create_check_constraint(
        "ck_material_thinking_mode",
        "material",
        "thinking_mode IN ('AUTO','ON','OFF')",
        schema="lia2",
    )

    op.add_column(
        "material",
        sa.Column(
            "source_group_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        schema="lia2",
    )
    op.add_column(
        "material",
        sa.Column(
            "source_sequence",
            sa.Integer(),
            nullable=True,
        ),
        schema="lia2",
    )
    op.create_check_constraint(
        "ck_material_source_sequence",
        "material",
        "source_sequence IS NULL OR source_sequence >= 1",
        schema="lia2",
    )

    op.create_check_constraint(
        "ck_material_ai_mode",
        "material",
        "ai_mode IN ('AUTO','FIXED','CUSTOM')",
        schema="lia2",
    )

    op.create_table(
        "pedagogical_artifact",
        sa.Column(
            "pedagogical_artifact_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "artifact_type",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="QUEUED",
        ),
        sa.Column(
            "progress_percent",
            sa.Integer(),
            nullable=False,
            server_default="5",
        ),
        sa.Column(
            "message",
            sa.String(length=500),
            nullable=False,
            server_default="Na fila para geração.",
        ),
        sa.Column(
            "title",
            sa.String(length=250),
            nullable=False,
        ),
        sa.Column(
            "instruction",
            sa.String(length=2000),
            nullable=True,
        ),
        sa.Column(
            "difficulty",
            sa.String(length=20),
            nullable=True,
        ),
        sa.Column(
            "question_count",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "requested_text_model_id",
            sa.String(length=300),
            nullable=True,
        ),
        sa.Column(
            "effective_text_model_id",
            sa.String(length=300),
            nullable=True,
        ),
        sa.Column(
            "thinking_mode",
            sa.String(length=10),
            nullable=False,
            server_default="AUTO",
        ),
        sa.Column(
            "effective_thinking_enabled",
            sa.Boolean(),
            nullable=True,
        ),
        sa.Column(
            "source_material_ids",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "source_evidence_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "content_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "error_code",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "error_message",
            sa.String(length=1000),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "finished_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "artifact_type IN ("
            "'TEACH','EXPLAIN','SUMMARY','MIND_MAP',"
            "'FLASHCARDS','EXERCISES','QUIZ'"
            ")",
            name="ck_pedagogical_artifact_type",
        ),
        sa.CheckConstraint(
            "status IN ('QUEUED','RUNNING','READY','FAILED','ARCHIVED')",
            name="ck_pedagogical_artifact_status",
        ),
        sa.CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name="ck_pedagogical_artifact_progress",
        ),
        sa.CheckConstraint(
            "difficulty IS NULL OR difficulty IN ('AUTO','EASY','MEDIUM','HARD')",
            name="ck_pedagogical_artifact_difficulty",
        ),
        sa.CheckConstraint(
            "thinking_mode IN ('AUTO','ON','OFF')",
            name="ck_pedagogical_artifact_thinking_mode",
        ),
        sa.CheckConstraint(
            "question_count IS NULL OR (question_count >= 1 AND question_count <= 30)",
            name="ck_pedagogical_artifact_question_count",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["lia2.student.student_id"],
            name="fk_pedagogical_artifact_student",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "pedagogical_artifact_id",
            name="pk_pedagogical_artifact",
        ),
        schema="lia2",
    )
    op.create_index(
        "ix_pedagogical_artifact_student_created",
        "pedagogical_artifact",
        ["student_id", "created_at"],
        schema="lia2",
    )
    op.create_index(
        "ix_pedagogical_artifact_status_created",
        "pedagogical_artifact",
        ["status", "created_at"],
        schema="lia2",
    )

    op.create_table(
        "learning_attempt",
        sa.Column(
            "learning_attempt_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "pedagogical_artifact_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "attempt_type",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "score_percent",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "correct_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "total_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "submitted_answers",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "result_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "attempt_type IN ('EXERCISES','QUIZ')",
            name="ck_learning_attempt_type",
        ),
        sa.CheckConstraint(
            "score_percent >= 0 AND score_percent <= 100",
            name="ck_learning_attempt_score",
        ),
        sa.CheckConstraint(
            "correct_count >= 0 AND total_count >= 1 AND correct_count <= total_count",
            name="ck_learning_attempt_counts",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["lia2.student.student_id"],
            name="fk_learning_attempt_student",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["pedagogical_artifact_id"],
            ["lia2.pedagogical_artifact.pedagogical_artifact_id"],
            name="fk_learning_attempt_artifact",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "learning_attempt_id",
            name="pk_learning_attempt",
        ),
        schema="lia2",
    )
    op.create_index(
        "ix_learning_attempt_student_created",
        "learning_attempt",
        ["student_id", "created_at"],
        schema="lia2",
    )
    op.create_index(
        "ix_learning_attempt_artifact",
        "learning_attempt",
        ["pedagogical_artifact_id"],
        schema="lia2",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_learning_attempt_artifact",
        table_name="learning_attempt",
        schema="lia2",
    )
    op.drop_index(
        "ix_learning_attempt_student_created",
        table_name="learning_attempt",
        schema="lia2",
    )
    op.drop_table("learning_attempt", schema="lia2")

    op.drop_index(
        "ix_pedagogical_artifact_status_created",
        table_name="pedagogical_artifact",
        schema="lia2",
    )
    op.drop_index(
        "ix_pedagogical_artifact_student_created",
        table_name="pedagogical_artifact",
        schema="lia2",
    )
    op.drop_table("pedagogical_artifact", schema="lia2")

    op.drop_constraint(
        "ck_material_source_sequence",
        "material",
        schema="lia2",
        type_="check",
    )
    op.drop_column("material", "source_sequence", schema="lia2")
    op.drop_column("material", "source_group_id", schema="lia2")

    op.drop_constraint(
        "ck_material_thinking_mode",
        "material",
        schema="lia2",
        type_="check",
    )
    op.drop_column("material", "thinking_mode", schema="lia2")

    op.drop_constraint(
        "ck_material_ai_mode",
        "material",
        schema="lia2",
        type_="check",
    )
    op.drop_column("material", "embedding_model_id", schema="lia2")
    op.drop_column("material", "vision_model_id", schema="lia2")
    op.drop_column("material", "text_model_id", schema="lia2")
    op.drop_column("material", "fixed_model_id", schema="lia2")
    op.drop_column("material", "ai_mode", schema="lia2")
