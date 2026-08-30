from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.imageGenerationTaskModel import ImageGenerationTaskModel


class ImageGenerationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, model: ImageGenerationTaskModel) -> ImageGenerationTaskModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findById(self, imageTaskId: UUID) -> ImageGenerationTaskModel | None:
        return self.session.get(ImageGenerationTaskModel, imageTaskId)
    def findByPedagogicalArtifactId(
        self,
        pedagogicalArtifactId: UUID,
    ) -> ImageGenerationTaskModel | None:
        return self.session.scalar(
            select(ImageGenerationTaskModel)
            .where(
                ImageGenerationTaskModel.relatedPedagogicalArtifactId
                == pedagogicalArtifactId
            )
            .order_by(ImageGenerationTaskModel.createdAt.desc())
            .limit(1)
        )

    def listByStudent(self, studentId: UUID, taskIds: list[UUID] | None = None) -> list[ImageGenerationTaskModel]:
        statement = select(ImageGenerationTaskModel).where(ImageGenerationTaskModel.studentId == studentId)
        if taskIds is not None:
            if not taskIds:
                return []
            statement = statement.where(ImageGenerationTaskModel.imageTaskId.in_(taskIds))
        return list(self.session.scalars(statement.order_by(ImageGenerationTaskModel.createdAt.asc())))

    def claimNext(self) -> ImageGenerationTaskModel | None:
        task = self.session.scalar(select(ImageGenerationTaskModel).where(ImageGenerationTaskModel.status == "QUEUED").order_by(ImageGenerationTaskModel.createdAt.asc()).with_for_update(skip_locked=True).limit(1))
        if task is None:
            return None
        task.status = "PREPARING"
        task.progressPercent = 15
        task.message = "Preparando a geração da imagem."
        task.startedAt = datetime.now(timezone.utc)
        task.attempts += 1
        self.session.flush()
        return task

    def requeueActive(self) -> int:
        tasks = list(self.session.scalars(select(ImageGenerationTaskModel).where(ImageGenerationTaskModel.status.in_(["PREPARING", "GENERATING", "LABELING"]))))
        for task in tasks:
            task.status = "QUEUED"
            task.progressPercent = 5
            task.message = "Retomando imagem após reinício."
            task.startedAt = None
        self.session.flush()
        return len(tasks)
