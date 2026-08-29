from app.contracts.learningContextContract import (
    LearningContextContract,
    LearningContextCreateContract,
)
from app.persistence.models.learningContextModel import LearningContextModel


class LearningContextMapper:
    @staticmethod
    def toModel(
        contract: LearningContextCreateContract,
    ) -> LearningContextModel:
        return LearningContextModel(
            contextType=contract.contextType,
            code=contract.code,
            name=contract.name,
            description=contract.description,
            status="ACTIVE",
            startsAt=contract.startsAt,
            endsAt=contract.endsAt,
        )

    @staticmethod
    def toContract(
        model: LearningContextModel,
    ) -> LearningContextContract:
        return LearningContextContract.model_validate(model)
