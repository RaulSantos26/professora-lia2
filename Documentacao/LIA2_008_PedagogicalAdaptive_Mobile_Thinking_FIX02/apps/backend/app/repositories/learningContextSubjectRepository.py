from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.learningContextSubjectModel import (
    LearningContextSubjectModel,
)


class LearningContextSubjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        association: LearningContextSubjectModel,
    ) -> LearningContextSubjectModel:
        self.session.add(association)
        self.session.flush()
        return association

    def findById(
        self,
        learningContextSubjectId: UUID,
    ) -> LearningContextSubjectModel | None:
        return self.session.get(
            LearningContextSubjectModel,
            learningContextSubjectId,
        )

    def findByContextAndSubject(
        self,
        learningContextId: UUID,
        subjectId: UUID,
    ) -> LearningContextSubjectModel | None:
        statement = (
            select(LearningContextSubjectModel)
            .where(
                LearningContextSubjectModel.learningContextId == learningContextId,
                LearningContextSubjectModel.subjectId == subjectId,
            )
            .limit(1)
        )
        return self.session.scalar(statement)

    def listActiveByLearningContextId(
        self,
        learningContextId: UUID,
    ) -> list[LearningContextSubjectModel]:
        statement = (
            select(LearningContextSubjectModel)
            .where(
                LearningContextSubjectModel.learningContextId == learningContextId,
                LearningContextSubjectModel.status == "ACTIVE",
            )
            .order_by(
                LearningContextSubjectModel.displayOrder.asc().nullslast(),
                LearningContextSubjectModel.createdAt.asc(),
            )
        )
        return list(self.session.scalars(statement))
