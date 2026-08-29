from uuid import UUID

from app.contracts.academicStageContract import (
    AcademicStageContract,
    AcademicStageCreateContract,
)
from app.persistence.models.academicStageModel import AcademicStageModel


class AcademicStageMapper:
    @staticmethod
    def toModel(
        studentId: UUID,
        contract: AcademicStageCreateContract,
    ) -> AcademicStageModel:
        return AcademicStageModel(
            studentId=studentId,
            educationLevel=contract.educationLevel,
            stageCode=contract.stageCode,
            stageLabel=contract.stageLabel,
            startedAt=contract.startedAt,
            endedAt=contract.endedAt,
            status=contract.status,
        )

    @staticmethod
    def toContract(model: AcademicStageModel) -> AcademicStageContract:
        return AcademicStageContract.model_validate(model)
