from app.contracts.studySessionContract import StudySessionContract, StudySessionItemContract
from app.persistence.models.studySessionItemModel import StudySessionItemModel
from app.persistence.models.studySessionModel import StudySessionModel

class StudySessionMapper:
    @staticmethod
    def toContract(model: StudySessionModel) -> StudySessionContract:
        return StudySessionContract.model_validate(model)

    @staticmethod
    def itemToContract(model: StudySessionItemModel) -> StudySessionItemContract:
        return StudySessionItemContract.model_validate(model)
