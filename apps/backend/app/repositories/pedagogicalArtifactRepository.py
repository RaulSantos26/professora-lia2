from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.persistence.models.pedagogicalArtifactModel import PedagogicalArtifactModel


class PedagogicalArtifactRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        model: PedagogicalArtifactModel,
    ) -> PedagogicalArtifactModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findById(
        self,
        artifactId: UUID,
    ) -> PedagogicalArtifactModel | None:
        return self.session.get(PedagogicalArtifactModel, artifactId)

    def listByStudent(
        self,
        studentId: UUID,
        limit: int = 30,
    ) -> list[PedagogicalArtifactModel]:
        statement = (
            select(PedagogicalArtifactModel)
            .where(
                PedagogicalArtifactModel.studentId == studentId,
                PedagogicalArtifactModel.status != "ARCHIVED",
            )
            .order_by(PedagogicalArtifactModel.createdAt.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def listByStudentScope(self, studentId: UUID, contextId: UUID, subjectId: UUID, unitId: UUID, limit: int = 30) -> list[PedagogicalArtifactModel]:
        statement = select(PedagogicalArtifactModel).where(
            PedagogicalArtifactModel.studentId == studentId,
            PedagogicalArtifactModel.studentLearningContextId == contextId,
            PedagogicalArtifactModel.studentSubjectId == subjectId,
            PedagogicalArtifactModel.studentLearningUnitId == unitId,
            PedagogicalArtifactModel.status != "ARCHIVED",
        ).order_by(PedagogicalArtifactModel.createdAt.desc()).limit(limit)
        return list(self.session.scalars(statement))

    def listAllByStudent(
        self,
        studentId: UUID,
    ) -> list[PedagogicalArtifactModel]:
        statement = (
            select(PedagogicalArtifactModel)
            .where(
                PedagogicalArtifactModel.studentId == studentId
            )
            .order_by(
                PedagogicalArtifactModel.createdAt.desc()
            )
        )
        return list(self.session.scalars(statement))

    def claimNext(self) -> PedagogicalArtifactModel | None:
        statement = (
            select(PedagogicalArtifactModel)
            .where(PedagogicalArtifactModel.status == "QUEUED")
            .order_by(PedagogicalArtifactModel.createdAt.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        model = self.session.scalar(statement)

        if model is None:
            return None

        model.status = "RUNNING"
        model.progressPercent = 12
        model.message = "Preparando evidências."
        model.startedAt = datetime.now(timezone.utc)
        self.session.flush()
        return model

    def complete(
        self,
        model: PedagogicalArtifactModel,
        *,
        content: dict,
        effectiveTextModelId: str,
        sourceEvidence: list[dict],
    ) -> None:
        model.status = "READY"
        model.progressPercent = 100
        model.message = "Atividade pronta."
        model.contentJson = content
        model.effectiveTextModelId = effectiveTextModelId
        model.sourceEvidenceJson = sourceEvidence
        model.finishedAt = datetime.now(timezone.utc)
        self.session.flush()

    def fail(
        self,
        model: PedagogicalArtifactModel,
        code: str,
        message: str,
    ) -> None:
        model.status = "FAILED"
        model.progressPercent = min(max(model.progressPercent, 1), 99)
        model.message = "Não foi possível gerar esta atividade."
        model.errorCode = code
        model.errorMessage = message
        model.finishedAt = datetime.now(timezone.utc)
        self.session.flush()

    def archive(self, model: PedagogicalArtifactModel) -> None:
        model.status = "ARCHIVED"
        self.session.flush()

    def deleteByStudent(self, studentId: UUID) -> int:
        result = self.session.execute(
            delete(PedagogicalArtifactModel).where(
                PedagogicalArtifactModel.studentId == studentId
            )
        )
        self.session.flush()
        return int(result.rowcount or 0)

    def deleteByIds(
        self,
        artifactIds: list[UUID],
    ) -> int:
        if not artifactIds:
            return 0

        result = self.session.execute(
            delete(PedagogicalArtifactModel).where(
                PedagogicalArtifactModel.pedagogicalArtifactId.in_(
                    artifactIds
                )
            )
        )
        self.session.flush()
        return int(result.rowcount or 0)

    def requeueRunning(self) -> int:
        statement = select(PedagogicalArtifactModel).where(
            PedagogicalArtifactModel.status == "RUNNING"
        )
        models = list(self.session.scalars(statement))

        for model in models:
            model.status = "QUEUED"
            model.progressPercent = max(
                5,
                min(model.progressPercent, 20),
            )
            model.message = "Geração retomada após reinício."
            model.startedAt = None

        self.session.flush()
        return len(models)
