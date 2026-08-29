from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.persistence.models.materialProcessingJobModel import (
    MaterialProcessingJobModel,
)


class MaterialProcessingJobRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        model: MaterialProcessingJobModel,
    ) -> MaterialProcessingJobModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findById(
        self,
        jobId: UUID,
    ) -> MaterialProcessingJobModel | None:
        return self.session.get(
            MaterialProcessingJobModel,
            jobId,
        )

    def listByStudentId(
        self,
        studentId: UUID,
        limit: int = 50,
    ) -> list[MaterialProcessingJobModel]:
        statement = (
            select(MaterialProcessingJobModel)
            .where(
                MaterialProcessingJobModel.studentId == studentId
            )
            .order_by(
                MaterialProcessingJobModel.createdAt.desc()
            )
            .limit(limit)
        )

        return list(self.session.scalars(statement))

    def listActiveByStudentId(
        self,
        studentId: UUID,
    ) -> list[MaterialProcessingJobModel]:
        statement = (
            select(MaterialProcessingJobModel)
            .where(
                MaterialProcessingJobModel.studentId == studentId,
                MaterialProcessingJobModel.status.in_(
                    ["QUEUED", "RUNNING"]
                ),
            )
            .order_by(
                MaterialProcessingJobModel.createdAt.asc()
            )
        )

        return list(self.session.scalars(statement))

    def requeueStale(
        self,
        olderThanMinutes: int = 30,
    ) -> int:
        threshold = (
            datetime.now(timezone.utc)
            - timedelta(minutes=olderThanMinutes)
        )

        statement = (
            select(MaterialProcessingJobModel)
            .where(
                MaterialProcessingJobModel.status == "RUNNING",
                MaterialProcessingJobModel.startedAt.is_not(None),
                MaterialProcessingJobModel.startedAt < threshold,
            )
        )

        jobs = list(self.session.scalars(statement))

        for job in jobs:
            job.status = "QUEUED"
            job.stage = "QUEUED"
            job.progressPercent = max(
                8,
                min(job.progressPercent, 20),
            )
            job.message = (
                "Processamento recuperado após interrupção."
            )
            job.startedAt = None

        self.session.flush()
        return len(jobs)

    def claimNext(
        self,
    ) -> MaterialProcessingJobModel | None:
        statement = (
            select(MaterialProcessingJobModel)
            .where(
                MaterialProcessingJobModel.status == "QUEUED"
            )
            .order_by(
                MaterialProcessingJobModel.createdAt.asc()
            )
            .with_for_update(skip_locked=True)
            .limit(1)
        )

        model = self.session.scalar(statement)

        if model is None:
            return None

        model.status = "RUNNING"
        model.stage = "STARTING"
        model.progressPercent = max(
            model.progressPercent,
            10,
        )
        model.message = "Iniciando processamento."
        model.startedAt = datetime.now(timezone.utc)

        self.session.flush()

        return model

    def updateProgress(
        self,
        model: MaterialProcessingJobModel,
        *,
        stage: str,
        progressPercent: int,
        message: str,
    ) -> None:
        model.stage = stage
        model.progressPercent = max(
            0,
            min(progressPercent, 100),
        )
        model.message = message
        self.session.flush()

    def complete(
        self,
        model: MaterialProcessingJobModel,
        *,
        warnings: bool,
        message: str,
    ) -> None:
        model.status = (
            "COMPLETED_WITH_WARNINGS"
            if warnings
            else "COMPLETED"
        )
        model.stage = "READY"
        model.progressPercent = 100
        model.message = message
        model.finishedAt = datetime.now(timezone.utc)
        self.session.flush()

    def fail(
        self,
        model: MaterialProcessingJobModel,
        *,
        errorCode: str,
        errorMessage: str,
    ) -> None:
        model.status = "FAILED"
        model.stage = "FAILED"
        model.progressPercent = min(
            max(model.progressPercent, 1),
            99,
        )
        model.message = "Falha no processamento."
        model.errorCode = errorCode
        model.errorMessage = errorMessage
        model.finishedAt = datetime.now(timezone.utc)
        self.session.flush()

    def deleteByMaterialId(
        self,
        materialId: UUID,
    ) -> int:
        result = self.session.execute(
            delete(MaterialProcessingJobModel).where(
                MaterialProcessingJobModel.materialId == materialId
            )
        )
        self.session.flush()
        return int(result.rowcount or 0)
