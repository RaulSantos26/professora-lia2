from app.contracts.studentContract import (
    StudentContract,
    StudentCreateContract,
)
from app.persistence.models.studentModel import StudentModel


class StudentMapper:
    @staticmethod
    def toModel(contract: StudentCreateContract) -> StudentModel:
        return StudentModel(
            fullName=contract.fullName,
            preferredName=contract.preferredName,
            status="ACTIVE",
        )

    @staticmethod
    def toContract(model: StudentModel) -> StudentContract:
        return StudentContract.model_validate(model)
