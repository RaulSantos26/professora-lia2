from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.studentModel import StudentModel


class StudentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, student: StudentModel) -> StudentModel:
        self.session.add(student)
        self.session.flush()
        return student

    def findById(self, studentId: UUID) -> StudentModel | None:
        return self.session.get(StudentModel, studentId)

    def listAll(self) -> list[StudentModel]:
        statement = (
            select(StudentModel)
            .order_by(StudentModel.fullName.asc(), StudentModel.createdAt.asc())
        )
        return list(self.session.scalars(statement))
