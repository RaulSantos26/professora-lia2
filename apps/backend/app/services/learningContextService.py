from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.contracts.learningContextContract import (
    LearningContextContract,
    LearningContextCreateContract,
)
from app.domain.common.domainError import DomainError
from app.mappers.learningContextMapper import LearningContextMapper
from app.repositories.learningContextRepository import LearningContextRepository


class LearningContextService:
    def __init__(self, session: Session):
        self.session = session
        self.learningContextRepository = LearningContextRepository(session)

    def createLearningContext(
        self,
        request: LearningContextCreateContract,
    ) -> LearningContextContract:
        existing = self.learningContextRepository.findByCode(request.code)

        if existing is not None:
            raise DomainError(
                code="LEARNING_CONTEXT_CODE_EXISTS",
                message="Já existe um contexto de aprendizagem com esse código.",
                httpStatus=409,
            )

        model = LearningContextMapper.toModel(request)

        try:
            self.learningContextRepository.create(model)
            self.session.commit()
            self.session.refresh(model)
        except IntegrityError as error:
            self.session.rollback()
            raise DomainError(
                code="LEARNING_CONTEXT_CONFLICT",
                message="Não foi possível criar o contexto de aprendizagem.",
                httpStatus=409,
            ) from error

        return LearningContextMapper.toContract(model)

    def listLearningContexts(self) -> list[LearningContextContract]:
        return [
            LearningContextMapper.toContract(model)
            for model in self.learningContextRepository.listActive()
        ]
