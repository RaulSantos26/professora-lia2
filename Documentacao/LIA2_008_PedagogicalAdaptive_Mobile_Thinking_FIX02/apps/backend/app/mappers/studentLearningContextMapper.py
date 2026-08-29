from app.contracts.studentLearningContextContract import (
    StudentLearningContextContract,
)
from app.persistence.models.studentLearningContextModel import (
    StudentLearningContextModel,
)


class StudentLearningContextMapper:
    @staticmethod
    def toContract(
        model: StudentLearningContextModel,
    ) -> StudentLearningContextContract:
        return StudentLearningContextContract.model_validate(model)
