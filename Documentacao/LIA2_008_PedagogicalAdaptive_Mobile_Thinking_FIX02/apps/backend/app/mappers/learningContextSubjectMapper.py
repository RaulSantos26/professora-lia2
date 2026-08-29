from app.contracts.learningContextSubjectContract import (
    LearningContextSubjectContract,
)
from app.persistence.models.learningContextSubjectModel import (
    LearningContextSubjectModel,
)


class LearningContextSubjectMapper:
    @staticmethod
    def toContract(
        model: LearningContextSubjectModel,
    ) -> LearningContextSubjectContract:
        return LearningContextSubjectContract.model_validate(model)
