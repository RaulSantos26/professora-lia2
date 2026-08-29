from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.persistence.models.learningAttemptModel import LearningAttemptModel


class LearningAttemptRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        model: LearningAttemptModel,
    ) -> LearningAttemptModel:
        self.session.add(model)
        self.session.flush()
        return model

    def listByStudent(
        self,
        studentId: UUID,
        limit: int = 50,
    ) -> list[LearningAttemptModel]:
        statement = (
            select(LearningAttemptModel)
            .where(LearningAttemptModel.studentId == studentId)
            .order_by(LearningAttemptModel.createdAt.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def deleteByArtifactIds(
        self,
        artifactIds: list[UUID],
    ) -> int:
        if not artifactIds:
            return 0

        result = self.session.execute(
            delete(LearningAttemptModel).where(
                LearningAttemptModel.pedagogicalArtifactId.in_(
                    artifactIds
                )
            )
        )
        self.session.flush()
        return int(result.rowcount or 0)
