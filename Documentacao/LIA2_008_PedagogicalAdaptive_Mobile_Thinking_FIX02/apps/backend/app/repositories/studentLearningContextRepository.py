from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.studentLearningContextModel import (
    StudentLearningContextModel,
)


class StudentLearningContextRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        association: StudentLearningContextModel,
    ) -> StudentLearningContextModel:
        self.session.add(association)
        self.session.flush()
        return association

    def findById(
        self,
        studentLearningContextId: UUID,
    ) -> StudentLearningContextModel | None:
        return self.session.get(
            StudentLearningContextModel,
            studentLearningContextId,
        )

    def findActive(
        self,
        studentId: UUID,
        learningContextId: UUID,
    ) -> StudentLearningContextModel | None:
        statement = (
            select(StudentLearningContextModel)
            .where(
                StudentLearningContextModel.studentId == studentId,
                StudentLearningContextModel.learningContextId == learningContextId,
                StudentLearningContextModel.status == "ACTIVE",
            )
            .limit(1)
        )
        return self.session.scalar(statement)

    def listActiveByStudentId(
        self,
        studentId: UUID,
    ) -> list[StudentLearningContextModel]:
        statement = (
            select(StudentLearningContextModel)
            .where(
                StudentLearningContextModel.studentId == studentId,
                StudentLearningContextModel.status == "ACTIVE",
            )
            .order_by(StudentLearningContextModel.enrolledAt.asc())
        )
        return list(self.session.scalars(statement))
