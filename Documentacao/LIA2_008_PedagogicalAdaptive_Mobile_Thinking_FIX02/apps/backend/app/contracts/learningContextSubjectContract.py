from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.subjectContract import SubjectContract


class LearningContextSubjectCreateContract(BaseModel):
    contractName: Literal[
        "LearningContextSubjectCreate.v1"
    ] = "LearningContextSubjectCreate.v1"
    displayOrder: int | None = Field(default=None, ge=0)


class LearningContextSubjectContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractName: Literal[
        "LearningContextSubject.v1"
    ] = "LearningContextSubject.v1"
    learningContextSubjectId: UUID
    learningContextId: UUID
    subjectId: UUID
    displayOrder: int | None
    status: Literal["ACTIVE", "INACTIVE"]
    createdAt: datetime
    updatedAt: datetime


class LearningContextSubjectViewContract(BaseModel):
    contractName: Literal[
        "LearningContextSubjectView.v1"
    ] = "LearningContextSubjectView.v1"
    association: LearningContextSubjectContract
    subject: SubjectContract
