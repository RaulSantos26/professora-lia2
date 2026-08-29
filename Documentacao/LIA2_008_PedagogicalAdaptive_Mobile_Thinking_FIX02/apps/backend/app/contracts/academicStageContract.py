from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AcademicStageCreateContract(BaseModel):
    contractName: Literal["AcademicStageCreate.v1"] = "AcademicStageCreate.v1"
    educationLevel: str = Field(min_length=2, max_length=80)
    stageCode: str | None = Field(default=None, max_length=80)
    stageLabel: str = Field(min_length=2, max_length=160)
    startedAt: date | None = None
    endedAt: date | None = None
    status: Literal["CURRENT", "COMPLETED", "CANCELLED"] = "CURRENT"

    @model_validator(mode="after")
    def validateDates(self):
        if (
            self.startedAt is not None
            and self.endedAt is not None
            and self.endedAt < self.startedAt
        ):
            raise ValueError("endedAt não pode ser anterior a startedAt.")

        return self


class AcademicStageContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractName: Literal["AcademicStage.v1"] = "AcademicStage.v1"
    academicStageId: UUID
    studentId: UUID
    educationLevel: str
    stageCode: str | None
    stageLabel: str
    startedAt: date | None
    endedAt: date | None
    status: Literal["CURRENT", "COMPLETED", "CANCELLED"]
    createdAt: datetime
    updatedAt: datetime
