"""Add learning scope isolation."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None

def upgrade():
    for column, table, constraint in (
        ("student_learning_context_id", "student_learning_context", "fk_pedagogical_artifact_context"),
        ("student_subject_id", "student_subject", "fk_pedagogical_artifact_subject"),
        ("student_learning_unit_id", "student_learning_unit", "fk_pedagogical_artifact_unit"),
    ):
        op.add_column("pedagogical_artifact", sa.Column(column, postgresql.UUID(as_uuid=True), nullable=True), schema="lia2")
        op.create_foreign_key(constraint, "pedagogical_artifact", table, [column], [column], source_schema="lia2", referent_schema="lia2", ondelete="RESTRICT")
    op.create_index("ix_pedagogical_artifact_scope", "pedagogical_artifact", ["student_id", "student_learning_context_id", "student_subject_id", "student_learning_unit_id"], schema="lia2")
    op.add_column("learning_goal", sa.Column("student_subject_id", postgresql.UUID(as_uuid=True), nullable=True), schema="lia2")
    op.create_foreign_key("fk_learning_goal_subject", "learning_goal", "student_subject", ["student_subject_id"], ["student_subject_id"], source_schema="lia2", referent_schema="lia2", ondelete="RESTRICT")
    op.create_index("ix_learning_goal_student_subject", "learning_goal", ["student_id", "student_subject_id"], schema="lia2")
    op.execute("""
        WITH resolved_scope AS (
          SELECT artifact.pedagogical_artifact_id, min(material.student_learning_context_id::text)::uuid context_id, min(material.student_subject_id::text)::uuid subject_id, min(material.student_learning_unit_id::text)::uuid unit_id, count(*) source_count, count(DISTINCT material.student_learning_context_id) context_count, count(DISTINCT material.student_subject_id) subject_count, count(DISTINCT material.student_learning_unit_id) unit_count
          FROM lia2.pedagogical_artifact artifact
          CROSS JOIN LATERAL jsonb_array_elements_text(coalesce(artifact.source_material_ids, '[]'::jsonb)) source(material_id)
          JOIN lia2.material material ON material.material_id::text = source.material_id
          GROUP BY artifact.pedagogical_artifact_id, artifact.source_material_ids
        )
        UPDATE lia2.pedagogical_artifact artifact
        SET student_learning_context_id = resolved_scope.context_id, student_subject_id = resolved_scope.subject_id, student_learning_unit_id = resolved_scope.unit_id
        FROM resolved_scope
        WHERE artifact.pedagogical_artifact_id = resolved_scope.pedagogical_artifact_id
          AND resolved_scope.source_count = jsonb_array_length(artifact.source_material_ids)
          AND resolved_scope.context_count = 1 AND resolved_scope.subject_count = 1 AND resolved_scope.unit_count = 1
          AND resolved_scope.context_id IS NOT NULL AND resolved_scope.subject_id IS NOT NULL AND resolved_scope.unit_id IS NOT NULL
    """)
    op.execute("""
        WITH resolved_goal_subject AS (
          SELECT scope.learning_goal_id, min(unit.student_subject_id::text)::uuid subject_id, count(DISTINCT unit.student_subject_id) subject_count
          FROM lia2.study_scope scope
          JOIN lia2.study_scope_item item ON item.study_scope_id = scope.study_scope_id AND item.status = 'ACTIVE'
          JOIN lia2.student_learning_unit unit ON unit.student_learning_unit_id = item.student_learning_unit_id
          GROUP BY scope.learning_goal_id
        )
        UPDATE lia2.learning_goal goal SET student_subject_id = resolved_goal_subject.subject_id
        FROM resolved_goal_subject
        WHERE goal.learning_goal_id = resolved_goal_subject.learning_goal_id AND resolved_goal_subject.subject_count = 1
    """)

def downgrade():
    op.drop_index("ix_learning_goal_student_subject", table_name="learning_goal", schema="lia2")
    op.drop_constraint("fk_learning_goal_subject", "learning_goal", schema="lia2", type_="foreignkey")
    op.drop_column("learning_goal", "student_subject_id", schema="lia2")
    op.drop_index("ix_pedagogical_artifact_scope", table_name="pedagogical_artifact", schema="lia2")
    for column, constraint in (("student_learning_unit_id", "fk_pedagogical_artifact_unit"), ("student_subject_id", "fk_pedagogical_artifact_subject"), ("student_learning_context_id", "fk_pedagogical_artifact_context")):
        op.drop_constraint(constraint, "pedagogical_artifact", schema="lia2", type_="foreignkey")
        op.drop_column("pedagogical_artifact", column, schema="lia2")
