from app.contracts.subjectContract import SubjectContract, SubjectCreateContract
from app.persistence.models.subjectModel import SubjectModel


class SubjectMapper:
    @staticmethod
    def toModel(contract: SubjectCreateContract) -> SubjectModel:
        return SubjectModel(
            code=contract.code,
            name=contract.name,
            description=contract.description,
            status="ACTIVE",
        )

    @staticmethod
    def toContract(model: SubjectModel) -> SubjectContract:
        return SubjectContract.model_validate(model)
