from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

class StudyScopeCreateContract(BaseModel):
    contractName: Literal["StudyScopeCreate.v1"] = "StudyScopeCreate.v1"
    name: str = Field(min_length=2, max_length=250)
    description: str | None = Field(default=None, max_length=1500)

    @field_validator("name", "description")
    @classmethod
    def normalizeText(cls, value):
        if value is None: return None
        normalized = " ".join(value.split())
        return normalized or None

class StudyScopeContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    contractName: Literal["StudyScope.v1"] = "StudyScope.v1"
    studyScopeId: UUID
    learningGoalId: UUID
    name: str
    description: str | None
    status: Literal["DRAFT","ACTIVE","COMPLETED","ARCHIVED"]
    createdAt: datetime
    updatedAt: datetime
