from datetime import date, datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

LearningGoalType = Literal["TEST","EXAM","REVIEW","PROJECT","COURSE","CERTIFICATION","OTHER"]

class LearningGoalCreateContract(BaseModel):
    contractName: Literal["LearningGoalCreate.v1"] = "LearningGoalCreate.v1"
    studentLearningContextId: UUID | None = None
    studentSubjectId: UUID | None = None
    goalType: LearningGoalType = "OTHER"
    title: str = Field(min_length=2, max_length=250)
    description: str | None = Field(default=None, max_length=1500)
    targetDate: date | None = None
    priority: int = Field(default=3, ge=1, le=5)

    @field_validator("title", "description")
    @classmethod
    def normalizeText(cls, value):
        if value is None: return None
        normalized = " ".join(value.split())
        return normalized or None

class LearningGoalContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    contractName: Literal["LearningGoal.v1"] = "LearningGoal.v1"
    learningGoalId: UUID
    studentId: UUID
    studentLearningContextId: UUID | None
    studentSubjectId: UUID | None
    goalType: LearningGoalType
    title: str
    description: str | None
    targetDate: date | None
    priority: int
    status: Literal["ACTIVE","COMPLETED","CANCELLED","ARCHIVED"]
    completedAt: datetime | None
    createdAt: datetime
    updatedAt: datetime
