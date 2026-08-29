from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


StudentLearningUnitType = Literal["LESSON", "MODULE", "CHAPTER", "SECTION"]
StudentLearningUnitStatus = Literal["DRAFT", "ACTIVE", "INACTIVE", "ARCHIVED"]


class StudentLearningUnitCreateContract(BaseModel):
    contractName: Literal[
        "StudentLearningUnitCreate.v1"
    ] = "StudentLearningUnitCreate.v1"
    parentStudentLearningUnitId: UUID | None = None
    unitType: StudentLearningUnitType = "LESSON"
    code: str = Field(min_length=2, max_length=100)
    title: str = Field(min_length=2, max_length=250)
    description: str | None = Field(default=None, max_length=1500)
    displayOrder: int | None = Field(default=None, ge=0)
    status: StudentLearningUnitStatus = "ACTIVE"

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


class StudentLearningUnitContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractName: Literal["StudentLearningUnit.v1"] = "StudentLearningUnit.v1"
    studentLearningUnitId: UUID
    studentSubjectId: UUID
    parentStudentLearningUnitId: UUID | None
    unitType: StudentLearningUnitType
    code: str
    title: str
    description: str | None
    displayOrder: int | None
    status: StudentLearningUnitStatus
    createdAt: datetime
    updatedAt: datetime
