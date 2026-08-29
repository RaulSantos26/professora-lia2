from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


LearningUnitType = Literal["LESSON", "MODULE", "CHAPTER", "SECTION"]
LearningUnitStatus = Literal["DRAFT", "ACTIVE", "INACTIVE", "ARCHIVED"]


class LearningUnitCreateContract(BaseModel):
    contractName: Literal["LearningUnitCreate.v1"] = "LearningUnitCreate.v1"
    parentLearningUnitId: UUID | None = None
    unitType: LearningUnitType = "LESSON"
    code: str = Field(min_length=2, max_length=100)
    title: str = Field(min_length=2, max_length=250)
    description: str | None = Field(default=None, max_length=1500)
    displayOrder: int | None = Field(default=None, ge=0)
    status: LearningUnitStatus = "ACTIVE"

    @field_validator("code")
    @classmethod
    def normalizeCode(cls, value: str) -> str:
        return value.strip().upper().replace(" ", "_")

    @field_validator("title", "description")
    @classmethod
    def normalizeText(cls, value):
        if value is None:
            return None

        normalized = " ".join(value.split())
        return normalized or None


class LearningUnitContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractName: Literal["LearningUnit.v1"] = "LearningUnit.v1"
    learningUnitId: UUID
    learningContextSubjectId: UUID
    parentLearningUnitId: UUID | None
    unitType: LearningUnitType
    code: str
    title: str
    description: str | None
    displayOrder: int | None
    status: LearningUnitStatus
    createdAt: datetime
    updatedAt: datetime
