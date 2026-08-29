from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StudentCreateContract(BaseModel):
    contractName: Literal["StudentCreate.v1"] = "StudentCreate.v1"
    fullName: str = Field(min_length=2, max_length=200)
    preferredName: str | None = Field(default=None, max_length=120)

    @field_validator("fullName", "preferredName")
    @classmethod
    def normalizeText(cls, value):
        if value is None:
            return None

        normalized = " ".join(value.split())
        return normalized or None


class StudentContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractName: Literal["Student.v1"] = "Student.v1"
    studentId: UUID
    fullName: str
    preferredName: str | None
    status: Literal["ACTIVE", "INACTIVE"]
    createdAt: datetime
    updatedAt: datetime
