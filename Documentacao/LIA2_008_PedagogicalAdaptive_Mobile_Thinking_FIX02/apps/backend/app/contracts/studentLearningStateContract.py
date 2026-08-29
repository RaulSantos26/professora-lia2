from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

LearningStateStatus = Literal["NOT_STARTED","LEARNING","REVIEWING","MASTERED"]

class StudentLearningStateUpdateContract(BaseModel):
    contractName: Literal["StudentLearningStateUpdate.v1"] = "StudentLearningStateUpdate.v1"
    status: LearningStateStatus
    masteryLevel: int = Field(ge=0, le=100)
    confidenceLevel: int = Field(ge=0, le=100)
    nextReviewAt: datetime | None = None

class StudentLearningStateContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    contractName: Literal["StudentLearningState.v1"] = "StudentLearningState.v1"
    studentLearningStateId: UUID
    studentId: UUID
    studentLearningUnitId: UUID
    status: LearningStateStatus
    masteryLevel: int
    confidenceLevel: int
    studyCount: int
    lastStudiedAt: datetime | None
    nextReviewAt: datetime | None
    createdAt: datetime
    updatedAt: datetime

class StudentLearningStateViewContract(BaseModel):
    contractName: Literal["StudentLearningStateView.v1"] = "StudentLearningStateView.v1"
    studentLearningContextId: UUID
    contextName: str
    studentSubjectId: UUID
    subjectName: str
    studentLearningUnitId: UUID
    unitCode: str
    unitTitle: str
    state: StudentLearningStateContract | None
