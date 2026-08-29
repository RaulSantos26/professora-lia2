from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.studentSubjectModel import StudentSubjectModel


class StudentSubjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, subject: StudentSubjectModel) -> StudentSubjectModel:
        self.session.add(subject)
        self.session.flush()
        return subject

    def findById(
        self,
        studentSubjectId: UUID,
    ) -> StudentSubjectModel | None:
        return self.session.get(StudentSubjectModel, studentSubjectId)

    def findByContextAndCode(
        self,
        studentLearningContextId: UUID,
        code: str,
    ) -> StudentSubjectModel | None:
        statement = (
            select(StudentSubjectModel)
            .where(
                StudentSubjectModel.studentLearningContextId
                == studentLearningContextId,
                StudentSubjectModel.code == code,
            )
            .limit(1)
        )
        return self.session.scalar(statement)

    def listActiveByContextId(
        self,
        studentLearningContextId: UUID,
    ) -> list[StudentSubjectModel]:
        statement = (
            select(StudentSubjectModel)
            .where(
                StudentSubjectModel.studentLearningContextId
                == studentLearningContextId,
                StudentSubjectModel.status == "ACTIVE",
            )
            .order_by(StudentSubjectModel.name.asc())
        )
        return list(self.session.scalars(statement))
