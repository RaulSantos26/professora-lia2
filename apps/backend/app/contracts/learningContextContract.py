from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


LearningContextType = Literal[
    "REGULAR_EDUCATION",
    "ENEM",
    "VESTIBULAR",
    "PUBLIC_EXAM",
    "GRADUATION",
    "POSTGRAD",
    "FREE_COURSE",
    "OTHER",
]


class LearningContextCreateContract(BaseModel):
    contractName: Literal["LearningContextCreate.v1"] = "LearningContextCreate.v1"
    contextType: LearningContextType
    code: str = Field(min_length=2, max_length=100)
    name: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    startsAt: date | None = None
    endsAt: date | None = None

    @field_validator("code", "name", "description")
    @classmethod
    def normalizeText(cls, value):
        if value is None:
            return None

        normalized = " ".join(value.split())
        return normalized or None

    @field_validator("code")
    @classmethod
    def normalizeCode(cls, value):
        return value.strip().upper().replace(" ", "_")

    @model_validator(mode="after")
    def validateDates(self):
        if (
            self.startsAt is not None
            and self.endsAt is not None
            and self.endsAt < self.startsAt
        ):
            raise ValueError("endsAt não pode ser anterior a startsAt.")

        return self


class LearningContextContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractName: Literal["LearningContext.v1"] = "LearningContext.v1"
    learningContextId: UUID
    contextType: LearningContextType
    code: str
    name: str
    description: str | None
    status: Literal["ACTIVE", "INACTIVE"]
    startsAt: date | None
    endsAt: date | None
    createdAt: datetime
    updatedAt: datetime
