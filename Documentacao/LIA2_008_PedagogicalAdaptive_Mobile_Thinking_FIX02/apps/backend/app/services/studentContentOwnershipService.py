from uuid import UUID
from sqlalchemy.orm import Session
from app.domain.common.domainError import DomainError
from app.repositories.studentLearningContextRepository import StudentLearningContextRepository
from app.repositories.studentLearningUnitRepository import StudentLearningUnitRepository
from app.repositories.studentSubjectRepository import StudentSubjectRepository

class StudentContentOwnershipService:
    def __init__(self, session: Session):
        self.studentLearningContextRepository = StudentLearningContextRepository(session)
        self.studentSubjectRepository = StudentSubjectRepository(session)
        self.studentLearningUnitRepository = StudentLearningUnitRepository(session)

    def resolveUnit(self, studentLearningUnitId: UUID):
        unit = self.studentLearningUnitRepository.findById(studentLearningUnitId)
        if unit is None:
            raise DomainError(
                code="STUDENT_LEARNING_UNIT_NOT_FOUND",
                message="Unidade de aprendizagem não encontrada.",
                httpStatus=404,
            )

        subject = self.studentSubjectRepository.findById(unit.studentSubjectId)
        if subject is None:
            raise DomainError(
                code="STUDENT_SUBJECT_NOT_FOUND",
                message="Matéria da unidade não encontrada.",
                httpStatus=404,
            )

        context = self.studentLearningContextRepository.findById(
            subject.studentLearningContextId
        )
        if context is None:
            raise DomainError(
                code="STUDENT_LEARNING_CONTEXT_NOT_FOUND",
                message="Contexto da unidade não encontrado.",
                httpStatus=404,
            )

        return unit, subject, context

    def assertUnitBelongsToStudent(
        self,
        studentLearningUnitId: UUID,
        studentId: UUID,
    ):
        unit, subject, context = self.resolveUnit(studentLearningUnitId)

        if context.studentId != studentId:
            raise DomainError(
                code="LEARNING_UNIT_NOT_OWNED_BY_STUDENT",
                message="A unidade não pertence ao aluno informado.",
                httpStatus=409,
            )

        return unit, subject, context
