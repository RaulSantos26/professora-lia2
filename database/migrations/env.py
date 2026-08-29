from logging.config import fileConfig

from alembic import context
from sqlalchemy import URL, create_engine, pool

from app.config.databaseSettings import databaseSettings
from app.persistence.models.academicStageModel import AcademicStageModel
from app.persistence.models.baseModel import BaseModel
from app.persistence.models.studentModel import StudentModel
from app.persistence.models.learningContextModel import LearningContextModel
from app.persistence.models.studentLearningContextModel import StudentLearningContextModel
from app.persistence.models.subjectModel import SubjectModel
from app.persistence.models.learningContextSubjectModel import LearningContextSubjectModel
from app.persistence.models.learningUnitModel import LearningUnitModel
from app.persistence.models.studentSubjectModel import StudentSubjectModel
from app.persistence.models.studentLearningUnitModel import StudentLearningUnitModel
from app.persistence.models.learningGoalModel import LearningGoalModel
from app.persistence.models.studyScopeModel import StudyScopeModel
from app.persistence.models.studyScopeItemModel import StudyScopeItemModel
from app.persistence.models.studySessionModel import StudySessionModel
from app.persistence.models.studySessionItemModel import StudySessionItemModel
from app.persistence.models.studentLearningStateModel import StudentLearningStateModel
from app.persistence.models.materialModel import MaterialModel
from app.persistence.models.materialFileModel import MaterialFileModel
from app.persistence.models.documentModel import DocumentModel
from app.persistence.models.documentVersionModel import DocumentVersionModel
from app.persistence.models.documentPageModel import DocumentPageModel
from app.persistence.models.documentBlockModel import DocumentBlockModel
from app.persistence.models.evidenceModel import EvidenceModel
from app.persistence.models.documentChunkModel import DocumentChunkModel
from app.persistence.models.materialProcessingJobModel import MaterialProcessingJobModel
from app.persistence.models.pedagogicalArtifactModel import PedagogicalArtifactModel
from app.persistence.models.learningAttemptModel import LearningAttemptModel
from app.persistence.models.agentThreadModel import AgentThreadModel
from app.persistence.models.agentMessageModel import AgentMessageModel
from app.persistence.models.agentRunModel import AgentRunModel
from app.persistence.models.agentToolCallModel import AgentToolCallModel
from app.persistence.models.visualTaskModel import VisualTaskModel


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

databaseUrl = URL.create(
    drivername="postgresql+psycopg",
    username=databaseSettings.user,
    password=databaseSettings.password,
    host=databaseSettings.host,
    port=databaseSettings.port,
    database=databaseSettings.database,
)

target_metadata = BaseModel.metadata


def runMigrationsOffline() -> None:
    context.configure(
        url=databaseUrl,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table="lia2_alembic_version",
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def runMigrationsOnline() -> None:
    connectable = create_engine(
        databaseUrl,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table="lia2_alembic_version",
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    runMigrationsOffline()
else:
    runMigrationsOnline()
