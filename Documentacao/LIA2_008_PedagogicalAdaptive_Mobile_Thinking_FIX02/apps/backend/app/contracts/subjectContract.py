from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubjectCreateContract(BaseModel):
    contractName: Literal["SubjectCreate.v1"] = "SubjectCreate.v1"
    code: str = Field(min_length=2, max_length=100)
    name: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("code")
    @classmethod
    def normalizeCode(cls, value: str) -> str:
        return value.strip().upper().replace(" ", "_")

    @field_validator("name", "description")
    @classmethod
    def normalizeText(cls, value):
        if value is None:
            return None

        normalized = " ".join(value.split())
        return normalized or None


class SubjectContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractName: Literal["Subject.v1"] = "Subject.v1"
    subjectId: UUID
    code: str
    name: str
    description: str | None
    status: Literal["ACTIVE", "INACTIVE"]
    createdAt: datetime
    updatedAt: datetime
