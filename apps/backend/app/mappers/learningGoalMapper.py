from app.contracts.learningGoalContract import LearningGoalContract
from app.persistence.models.learningGoalModel import LearningGoalModel

class LearningGoalMapper:
    @staticmethod
    def toContract(model: LearningGoalModel) -> LearningGoalContract:
        return LearningGoalContract.model_validate(model)
