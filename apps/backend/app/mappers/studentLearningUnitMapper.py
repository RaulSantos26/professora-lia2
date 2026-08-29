from app.contracts.studentLearningUnitContract import (
    StudentLearningUnitContract,
)
from app.persistence.models.studentLearningUnitModel import (
    StudentLearningUnitModel,
)


class StudentLearningUnitMapper:
    @staticmethod
    def toContract(
        model: StudentLearningUnitModel,
    ) -> StudentLearningUnitContract:
        return StudentLearningUnitContract.model_validate(model)
