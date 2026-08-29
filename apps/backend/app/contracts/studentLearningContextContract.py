from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StudentLearningContextCreateContract(BaseModel):
    contractName: Literal[
        "StudentLearningContextCreate.v1"
    ] = "StudentLearningContextCreate.v1"
    academicStageId: UUID | None = None


class StudentLearningContextContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractName: Literal[
        "StudentLearningContext.v1"
    ] = "StudentLearningContext.v1"
    studentLearningContextId: UUID
    studentId: UUID
    learningContextId: UUID
    academicStageId: UUID | None
    status: Literal["ACTIVE", "INACTIVE", "COMPLETED"]
    enrolledAt: datetime
    completedAt: datetime | None
    createdAt: datetime
    updatedAt: datetime


class StudentLearningContextViewContract(BaseModel):
    contractName: Literal[
        "StudentLearningContextView.v1"
    ] = "StudentLearningContextView.v1"
    association: StudentLearningContextContract
    context: "LearningContextContract"


from app.contracts.learningContextContract import LearningContextContract

StudentLearningContextViewContract.model_rebuild()
