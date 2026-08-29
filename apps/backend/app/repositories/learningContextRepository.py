from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.learningContextModel import LearningContextModel


class LearningContextRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        learningContext: LearningContextModel,
    ) -> LearningContextModel:
        self.session.add(learningContext)
        self.session.flush()
        return learningContext

    def findById(
        self,
        learningContextId: UUID,
    ) -> LearningContextModel | None:
        return self.session.get(LearningContextModel, learningContextId)

    def findByCode(
        self,
        code: str,
    ) -> LearningContextModel | None:
        statement = (
            select(LearningContextModel)
            .where(LearningContextModel.code == code)
            .limit(1)
        )
        return self.session.scalar(statement)

    def listActive(self) -> list[LearningContextModel]:
        statement = (
            select(LearningContextModel)
            .where(LearningContextModel.status == "ACTIVE")
            .order_by(
                LearningContextModel.contextType.asc(),
                LearningContextModel.name.asc(),
            )
        )
        return list(self.session.scalars(statement))
