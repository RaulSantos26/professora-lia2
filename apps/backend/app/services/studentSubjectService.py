from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.contracts.studentSubjectContract import (
    StudentSubjectContract,
    StudentSubjectCreateContract,
)
from app.domain.common.domainError import DomainError
from app.mappers.studentSubjectMapper import StudentSubjectMapper
from app.persistence.models.studentSubjectModel import StudentSubjectModel
from app.repositories.studentLearningContextRepository import (
    StudentLearningContextRepository,
)
from app.repositories.studentSubjectRepository import StudentSubjectRepository
from app.repositories.subjectRepository import SubjectRepository


class StudentSubjectService:
    def __init__(self, session: Session):
        self.session = session
        self.studentLearningContextRepository = StudentLearningContextRepository(
            session
        )
        self.studentSubjectRepository = StudentSubjectRepository(session)
        self.subjectRepository = SubjectRepository(session)

    def createStudentSubject(
        self,
        studentLearningContextId: UUID,
        request: StudentSubjectCreateContract,
    ) -> StudentSubjectContract:
        association = self.studentLearningContextRepository.findById(
            studentLearningContextId
        )

        if association is None or association.status != "ACTIVE":
            raise DomainError(
                code="STUDENT_LEARNING_CONTEXT_NOT_FOUND",
                message="Contexto do aluno não encontrado ou inativo.",
                httpStatus=404,
            )

        if self.studentSubjectRepository.findByContextAndCode(
            studentLearningContextId,
            request.code,
        ) is not None:
            raise DomainError(
                code="STUDENT_SUBJECT_CODE_EXISTS",
                message="O aluno já possui uma matéria com esse código neste contexto.",
                httpStatus=409,
            )

        definitionId = request.subjectDefinitionId
        if definitionId is not None:
            definition = self.subjectRepository.findById(definitionId)
            if definition is None:
                raise DomainError(
                    code="SUBJECT_DEFINITION_NOT_FOUND",
                    message="Referência de matéria não encontrada.",
                    httpStatus=404,
                )

        model = StudentSubjectModel(
            studentLearningContextId=studentLearningContextId,
            subjectDefinitionId=definitionId,
            code=request.code,
            name=request.name,
            description=request.description,
            status="ACTIVE",
        )

        try:
            self.studentSubjectRepository.create(model)
            self.session.commit()
            self.session.refresh(model)
        except IntegrityError as error:
            self.session.rollback()
            raise DomainError(
                code="STUDENT_SUBJECT_CONFLICT",
                message="Não foi possível criar a matéria do aluno.",
                httpStatus=409,
            ) from error

        return StudentSubjectMapper.toContract(model)

    def listStudentSubjects(
        self,
        studentLearningContextId: UUID,
    ) -> list[StudentSubjectContract]:
        association = self.studentLearningContextRepository.findById(
            studentLearningContextId
        )

        if association is None:
            raise DomainError(
                code="STUDENT_LEARNING_CONTEXT_NOT_FOUND",
                message="Contexto do aluno não encontrado.",
                httpStatus=404,
            )

        return [
            StudentSubjectMapper.toContract(model)
            for model in self.studentSubjectRepository.listActiveByContextId(
                studentLearningContextId
            )
        ]
