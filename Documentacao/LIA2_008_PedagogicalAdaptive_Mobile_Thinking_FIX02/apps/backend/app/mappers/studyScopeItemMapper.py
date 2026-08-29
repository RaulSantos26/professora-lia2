from app.contracts.studyScopeItemContract import StudyScopeItemContract
from app.persistence.models.studyScopeItemModel import StudyScopeItemModel

class StudyScopeItemMapper:
    @staticmethod
    def toContract(model: StudyScopeItemModel) -> StudyScopeItemContract:
        return StudyScopeItemContract.model_validate(model)
