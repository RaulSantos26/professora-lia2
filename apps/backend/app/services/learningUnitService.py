from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.contracts.learningUnitContract import (
    LearningUnitContract,
    LearningUnitCreateContract,
)
from app.domain.common.domainError import DomainError
from app.mappers.learningUnitMapper import LearningUnitMapper
from app.repositories.learningContextSubjectRepository import (
    LearningContextSubjectRepository,
)
from app.repositories.learningUnitRepository import LearningUnitRepository


class LearningUnitService:
    def __init__(self, session: Session):
        self.session = session
        self.learningContextSubjectRepository = (
            LearningContextSubjectRepository(session)
        )
        self.learningUnitRepository = LearningUnitRepository(session)

    def createLearningUnit(
        self,
        learningContextSubjectId: UUID,
        request: LearningUnitCreateContract,
    ) -> LearningUnitContract:
        association = self.learningContextSubjectRepository.findById(
            learningContextSubjectId
        )
        if association is None or association.status != "ACTIVE":
            raise DomainError(
                code="LEARNING_CONTEXT_SUBJECT_NOT_FOUND",
                message="Associação entre contexto e matéria não encontrada.",
                httpStatus=404,
            )

        if self.learningUnitRepository.findByAssociationAndCode(
            learningContextSubjectId,
            request.code,
        ) is not None:
            raise DomainError(
                code="LEARNING_UNIT_CODE_EXISTS",
                message="Já existe uma unidade com esse código nessa matéria/contexto.",
                httpStatus=409,
            )

        if request.parentLearningUnitId is not None:
            parent = self.learningUnitRepository.findById(
                request.parentLearningUnitId
            )
            if parent is None:
                raise DomainError(
                    code="PARENT_LEARNING_UNIT_NOT_FOUND",
                    message="Unidade pai não encontrada.",
                    httpStatus=404,
                )

            if (
                parent.learningContextSubjectId
                != learningContextSubjectId
            ):
                raise DomainError(
                    code="PARENT_LEARNING_UNIT_CONTEXT_MISMATCH",
                    message="A unidade pai pertence a outra matéria/contexto.",
                    httpStatus=409,
                )

        model = LearningUnitMapper.toModel(
            learningContextSubjectId,
            request,
        )

        try:
            self.learningUnitRepository.create(model)
            self.session.commit()
            self.session.refresh(model)
        except IntegrityError as error:
            self.session.rollback()
            raise DomainError(
                code="LEARNING_UNIT_CONFLICT",
                message="Não foi possível criar a unidade de aprendizagem.",
                httpStatus=409,
            ) from error

        return LearningUnitMapper.toContract(model)

    def listLearningUnits(
        self,
        learningContextSubjectId: UUID,
    ) -> list[LearningUnitContract]:
        association = self.learningContextSubjectRepository.findById(
            learningContextSubjectId
        )
        if association is None:
            raise DomainError(
                code="LEARNING_CONTEXT_SUBJECT_NOT_FOUND",
                message="Associação entre contexto e matéria não encontrada.",
                httpStatus=404,
            )

        return [
            LearningUnitMapper.toContract(model)
            for model in self.learningUnitRepository.listByAssociationId(
                learningContextSubjectId
            )
        ]
