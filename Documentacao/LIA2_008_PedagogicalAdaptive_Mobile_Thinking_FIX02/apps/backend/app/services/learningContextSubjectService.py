from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.contracts.learningContextSubjectContract import (
    LearningContextSubjectCreateContract,
    LearningContextSubjectViewContract,
)
from app.domain.common.domainError import DomainError
from app.mappers.learningContextSubjectMapper import (
    LearningContextSubjectMapper,
)
from app.mappers.subjectMapper import SubjectMapper
from app.persistence.models.learningContextSubjectModel import (
    LearningContextSubjectModel,
)
from app.repositories.learningContextRepository import LearningContextRepository
from app.repositories.learningContextSubjectRepository import (
    LearningContextSubjectRepository,
)
from app.repositories.subjectRepository import SubjectRepository


class LearningContextSubjectService:
    def __init__(self, session: Session):
        self.session = session
        self.learningContextRepository = LearningContextRepository(session)
        self.subjectRepository = SubjectRepository(session)
        self.learningContextSubjectRepository = (
            LearningContextSubjectRepository(session)
        )

    def assignSubject(
        self,
        learningContextId: UUID,
        subjectId: UUID,
        request: LearningContextSubjectCreateContract,
    ) -> LearningContextSubjectViewContract:
        context = self.learningContextRepository.findById(learningContextId)
        if context is None or context.status != "ACTIVE":
            raise DomainError(
                code="LEARNING_CONTEXT_NOT_FOUND",
                message="Contexto de aprendizagem não encontrado ou inativo.",
                httpStatus=404,
            )

        subject = self.subjectRepository.findById(subjectId)
        if subject is None or subject.status != "ACTIVE":
            raise DomainError(
                code="SUBJECT_NOT_FOUND",
                message="Matéria não encontrada ou inativa.",
                httpStatus=404,
            )

        if self.learningContextSubjectRepository.findByContextAndSubject(
            learningContextId,
            subjectId,
        ) is not None:
            raise DomainError(
                code="LEARNING_CONTEXT_SUBJECT_EXISTS",
                message="A matéria já está vinculada a esse contexto.",
                httpStatus=409,
            )

        association = LearningContextSubjectModel(
            learningContextId=learningContextId,
            subjectId=subjectId,
            displayOrder=request.displayOrder,
            status="ACTIVE",
        )

        try:
            self.learningContextSubjectRepository.create(association)
            self.session.commit()
            self.session.refresh(association)
        except IntegrityError as error:
            self.session.rollback()
            raise DomainError(
                code="LEARNING_CONTEXT_SUBJECT_CONFLICT",
                message="Não foi possível vincular a matéria ao contexto.",
                httpStatus=409,
            ) from error

        return LearningContextSubjectViewContract(
            association=LearningContextSubjectMapper.toContract(association),
            subject=SubjectMapper.toContract(subject),
        )

    def listSubjectsForContext(
        self,
        learningContextId: UUID,
    ) -> list[LearningContextSubjectViewContract]:
        context = self.learningContextRepository.findById(learningContextId)
        if context is None:
            raise DomainError(
                code="LEARNING_CONTEXT_NOT_FOUND",
                message="Contexto de aprendizagem não encontrado.",
                httpStatus=404,
            )

        results = []
        for association in (
            self.learningContextSubjectRepository.listActiveByLearningContextId(
                learningContextId
            )
        ):
            subject = self.subjectRepository.findById(association.subjectId)
            if subject is None:
                continue

            results.append(
                LearningContextSubjectViewContract(
                    association=LearningContextSubjectMapper.toContract(
                        association
                    ),
                    subject=SubjectMapper.toContract(subject),
                )
            )

        return results
