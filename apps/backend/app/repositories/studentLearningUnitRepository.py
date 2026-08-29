from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.studentLearningUnitModel import (
    StudentLearningUnitModel,
)


class StudentLearningUnitRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        learningUnit: StudentLearningUnitModel,
    ) -> StudentLearningUnitModel:
        self.session.add(learningUnit)
        self.session.flush()
        return learningUnit

    def findById(
        self,
        studentLearningUnitId: UUID,
    ) -> StudentLearningUnitModel | None:
        return self.session.get(
            StudentLearningUnitModel,
            studentLearningUnitId,
        )

    def findBySubjectAndCode(
        self,
        studentSubjectId: UUID,
        code: str,
    ) -> StudentLearningUnitModel | None:
        statement = (
            select(StudentLearningUnitModel)
            .where(
                StudentLearningUnitModel.studentSubjectId == studentSubjectId,
                StudentLearningUnitModel.code == code,
            )
            .limit(1)
        )
        return self.session.scalar(statement)

    def listBySubjectId(
        self,
        studentSubjectId: UUID,
    ) -> list[StudentLearningUnitModel]:
        statement = (
            select(StudentLearningUnitModel)
            .where(
                StudentLearningUnitModel.studentSubjectId == studentSubjectId
            )
            .order_by(
                StudentLearningUnitModel.displayOrder.asc().nullslast(),
                StudentLearningUnitModel.createdAt.asc(),
            )
        )
        return list(self.session.scalars(statement))
