from uuid import UUID

from sqlalchemy.orm import Session

from app.contracts.studentContract import (
    StudentContract,
    StudentCreateContract,
)
from app.domain.common.domainError import DomainError
from app.mappers.studentMapper import StudentMapper
from app.repositories.studentRepository import StudentRepository


class StudentService:
    def __init__(self, session: Session):
        self.session = session
        self.studentRepository = StudentRepository(session)

    def createStudent(
        self,
        request: StudentCreateContract,
    ) -> StudentContract:
        student = StudentMapper.toModel(request)
        self.studentRepository.create(student)
        self.session.commit()
        self.session.refresh(student)
        return StudentMapper.toContract(student)

    def getStudent(self, studentId: UUID) -> StudentContract:
        student = self.studentRepository.findById(studentId)

        if student is None:
            raise DomainError(
                code="STUDENT_NOT_FOUND",
                message="Aluno não encontrado.",
                httpStatus=404,
            )

        return StudentMapper.toContract(student)

    def listStudents(self) -> list[StudentContract]:
        return [
            StudentMapper.toContract(student)
            for student in self.studentRepository.listAll()
        ]
