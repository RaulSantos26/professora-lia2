from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.learningUnitModel import LearningUnitModel


class LearningUnitRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        learningUnit: LearningUnitModel,
    ) -> LearningUnitModel:
        self.session.add(learningUnit)
        self.session.flush()
        return learningUnit

    def findById(
        self,
        learningUnitId: UUID,
    ) -> LearningUnitModel | None:
        return self.session.get(LearningUnitModel, learningUnitId)

    def findByAssociationAndCode(
        self,
        learningContextSubjectId: UUID,
        code: str,
    ) -> LearningUnitModel | None:
        statement = (
            select(LearningUnitModel)
            .where(
                LearningUnitModel.learningContextSubjectId == learningContextSubjectId,
                LearningUnitModel.code == code,
            )
            .limit(1)
        )
        return self.session.scalar(statement)

    def listByAssociationId(
        self,
        learningContextSubjectId: UUID,
    ) -> list[LearningUnitModel]:
        statement = (
            select(LearningUnitModel)
            .where(
                LearningUnitModel.learningContextSubjectId
                == learningContextSubjectId
            )
            .order_by(
                LearningUnitModel.displayOrder.asc().nullslast(),
                LearningUnitModel.createdAt.asc(),
            )
        )
        return list(self.session.scalars(statement))
