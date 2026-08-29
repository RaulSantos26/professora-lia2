from app.contracts.studyScopeContract import StudyScopeContract
from app.persistence.models.studyScopeModel import StudyScopeModel

class StudyScopeMapper:
    @staticmethod
    def toContract(model: StudyScopeModel) -> StudyScopeContract:
        return StudyScopeContract.model_validate(model)
