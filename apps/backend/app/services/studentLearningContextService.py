from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.contracts.studentLearningContextContract import (
    StudentLearningContextCreateContract,
    StudentLearningContextViewContract,
)
from app.domain.common.domainError import DomainError
from app.mappers.learningContextMapper import LearningContextMapper
from app.mappers.studentLearningContextMapper import StudentLearningContextMapper
from app.persistence.models.studentLearningContextModel import (
    StudentLearningContextModel,
)
from app.repositories.academicStageRepository import AcademicStageRepository
from app.repositories.learningContextRepository import LearningContextRepository
from app.repositories.studentLearningContextRepository import (
    StudentLearningContextRepository,
)
from app.repositories.studentRepository import StudentRepository


class StudentLearningContextService:
    def __init__(self, session: Session):
        self.session = session
        self.studentRepository = StudentRepository(session)
        self.academicStageRepository = AcademicStageRepository(session)
        self.learningContextRepository = LearningContextRepository(session)
        self.studentLearningContextRepository = StudentLearningContextRepository(
            session
        )

    def assignLearningContext(
        self,
        studentId: UUID,
        learningContextId: UUID,
        request: StudentLearningContextCreateContract,
    ) -> StudentLearningContextViewContract:
        student = self.studentRepository.findById(studentId)

        if student is None:
            raise DomainError(
                code="STUDENT_NOT_FOUND",
                message="Aluno não encontrado.",
                httpStatus=404,
            )

        learningContext = self.learningContextRepository.findById(
            learningContextId
        )

        if learningContext is None or learningContext.status != "ACTIVE":
            raise DomainError(
                code="LEARNING_CONTEXT_NOT_FOUND",
                message="Contexto de aprendizagem não encontrado ou inativo.",
                httpStatus=404,
            )

        if self.studentLearningContextRepository.findActive(
            studentId,
            learningContextId,
        ) is not None:
            raise DomainError(
                code="STUDENT_LEARNING_CONTEXT_EXISTS",
                message="O aluno já possui esse contexto de aprendizagem ativo.",
                httpStatus=409,
            )

        if request.academicStageId is not None:
            stages = self.academicStageRepository.listByStudentId(studentId)
            validStageIds = {stage.academicStageId for stage in stages}

            if request.academicStageId not in validStageIds:
                raise DomainError(
                    code="ACADEMIC_STAGE_NOT_OWNED_BY_STUDENT",
                    message="A etapa acadêmica informada não pertence ao aluno.",
                    httpStatus=409,
                )

        association = StudentLearningContextModel(
            studentId=studentId,
            learningContextId=learningContextId,
            academicStageId=request.academicStageId,
            status="ACTIVE",
        )

        try:
            self.studentLearningContextRepository.create(association)
            self.session.commit()
            self.session.refresh(association)
        except IntegrityError as error:
            self.session.rollback()
            raise DomainError(
                code="STUDENT_LEARNING_CONTEXT_CONFLICT",
                message="Não foi possível vincular o contexto ao aluno.",
                httpStatus=409,
            ) from error

        return StudentLearningContextViewContract(
            association=StudentLearningContextMapper.toContract(association),
            context=LearningContextMapper.toContract(learningContext),
        )

    def listStudentLearningContexts(
        self,
        studentId: UUID,
    ) -> list[StudentLearningContextViewContract]:
        student = self.studentRepository.findById(studentId)

        if student is None:
            raise DomainError(
                code="STUDENT_NOT_FOUND",
                message="Aluno não encontrado.",
                httpStatus=404,
            )

        results = []

        for association in self.studentLearningContextRepository.listActiveByStudentId(
            studentId
        ):
            context = self.learningContextRepository.findById(
                association.learningContextId
            )
            if context is None:
                continue

            results.append(
                StudentLearningContextViewContract(
                    association=StudentLearningContextMapper.toContract(
                        association
                    ),
                    context=LearningContextMapper.toContract(context),
                )
            )

        return results
