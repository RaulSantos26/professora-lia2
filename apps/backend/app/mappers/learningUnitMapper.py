from app.contracts.learningUnitContract import (
    LearningUnitContract,
    LearningUnitCreateContract,
)
from app.persistence.models.learningUnitModel import LearningUnitModel


class LearningUnitMapper:
    @staticmethod
    def toModel(
        learningContextSubjectId,
        contract: LearningUnitCreateContract,
    ) -> LearningUnitModel:
        return LearningUnitModel(
            learningContextSubjectId=learningContextSubjectId,
            parentLearningUnitId=contract.parentLearningUnitId,
            unitType=contract.unitType,
            code=contract.code,
            title=contract.title,
            description=contract.description,
            displayOrder=contract.displayOrder,
            status=contract.status,
        )

    @staticmethod
    def toContract(model: LearningUnitModel) -> LearningUnitContract:
        return LearningUnitContract.model_validate(model)
