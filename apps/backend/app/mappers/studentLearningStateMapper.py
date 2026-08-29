from app.contracts.studentLearningStateContract import StudentLearningStateContract
from app.persistence.models.studentLearningStateModel import StudentLearningStateModel

class StudentLearningStateMapper:
    @staticmethod
    def toContract(model: StudentLearningStateModel) -> StudentLearningStateContract:
        return StudentLearningStateContract.model_validate(model)
