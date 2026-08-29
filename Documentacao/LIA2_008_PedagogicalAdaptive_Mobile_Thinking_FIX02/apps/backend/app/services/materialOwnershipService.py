from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.common.domainError import DomainError
from app.repositories.studentLearningContextRepository import (
    StudentLearningContextRepository,
)
from app.repositories.studentLearningUnitRepository import (
    StudentLearningUnitRepository,
)
from app.repositories.studentRepository import StudentRepository
from app.repositories.studentSubjectRepository import StudentSubjectRepository


class MaterialOwnershipService:
    def __init__(self, session: Session):
        self.studentRepository = StudentRepository(session)
        self.contextRepository = StudentLearningContextRepository(session)
        self.subjectRepository = StudentSubjectRepository(session)
        self.unitRepository = StudentLearningUnitRepository(session)

    def validate(
        self,
        studentId: UUID,
        studentLearningContextId: UUID | None,
        studentSubjectId: UUID | None,
        studentLearningUnitId: UUID | None,
    ) -> None:
        if self.studentRepository.findById(studentId) is None:
            raise DomainError(
                code="STUDENT_NOT_FOUND",
                message="Aluno não encontrado.",
                httpStatus=404,
            )

        context = None
        if studentLearningContextId is not None:
            context = self.contextRepository.findById(studentLearningContextId)
            if context is None or context.studentId != studentId:
                raise DomainError(
                    code="MATERIAL_CONTEXT_NOT_OWNED",
                    message="O contexto do material não pertence ao aluno.",
                    httpStatus=409,
                )

        subject = None
        if studentSubjectId is not None:
            subject = self.subjectRepository.findById(studentSubjectId)
            if subject is None:
                raise DomainError(
                    code="MATERIAL_SUBJECT_NOT_FOUND",
                    message="Matéria do material não encontrada.",
                    httpStatus=404,
                )

            subjectContext = self.contextRepository.findById(
                subject.studentLearningContextId
            )
            if subjectContext is None or subjectContext.studentId != studentId:
                raise DomainError(
                    code="MATERIAL_SUBJECT_NOT_OWNED",
                    message="A matéria do material não pertence ao aluno.",
                    httpStatus=409,
                )

            if (
                context is not None
                and subject.studentLearningContextId
                != context.studentLearningContextId
            ):
                raise DomainError(
                    code="MATERIAL_SUBJECT_CONTEXT_MISMATCH",
                    message="A matéria não pertence ao contexto informado.",
                    httpStatus=409,
                )

        if studentLearningUnitId is not None:
            unit = self.unitRepository.findById(studentLearningUnitId)
            if unit is None:
                raise DomainError(
                    code="MATERIAL_UNIT_NOT_FOUND",
                    message="Unidade do material não encontrada.",
                    httpStatus=404,
                )

            unitSubject = self.subjectRepository.findById(unit.studentSubjectId)
            if unitSubject is None:
                raise DomainError(
                    code="MATERIAL_UNIT_SUBJECT_NOT_FOUND",
                    message="Matéria da unidade não encontrada.",
                    httpStatus=404,
                )

            unitContext = self.contextRepository.findById(
                unitSubject.studentLearningContextId
            )
            if unitContext is None or unitContext.studentId != studentId:
                raise DomainError(
                    code="MATERIAL_UNIT_NOT_OWNED",
                    message="A unidade do material não pertence ao aluno.",
                    httpStatus=409,
                )

            if subject is not None and unit.studentSubjectId != subject.studentSubjectId:
                raise DomainError(
                    code="MATERIAL_UNIT_SUBJECT_MISMATCH",
                    message="A unidade não pertence à matéria informada.",
                    httpStatus=409,
                )

            if (
                context is not None
                and unitSubject.studentLearningContextId
                != context.studentLearningContextId
            ):
                raise DomainError(
                    code="MATERIAL_UNIT_CONTEXT_MISMATCH",
                    message="A unidade não pertence ao contexto informado.",
                    httpStatus=409,
                )
