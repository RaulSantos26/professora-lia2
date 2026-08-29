from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class StudyScopeItemCreateContract(BaseModel):
    contractName: Literal["StudyScopeItemCreate.v1"] = "StudyScopeItemCreate.v1"
    studentLearningUnitId: UUID
    displayOrder: int | None = Field(default=None, ge=0)
    isRequired: bool = True

class StudyScopeItemContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    contractName: Literal["StudyScopeItem.v1"] = "StudyScopeItem.v1"
    studyScopeItemId: UUID
    studyScopeId: UUID
    studentLearningUnitId: UUID
    displayOrder: int | None
    isRequired: bool
    status: Literal["ACTIVE","REMOVED"]
    createdAt: datetime
    updatedAt: datetime

class StudyScopeCandidateContract(BaseModel):
    contractName: Literal["StudyScopeCandidate.v1"] = "StudyScopeCandidate.v1"
    studentLearningContextId: UUID
    contextName: str
    studentSubjectId: UUID
    subjectName: str
    studentLearningUnitId: UUID
    unitCode: str
    unitTitle: str
    unitType: str
    isSelected: bool
    studyScopeItemId: UUID | None
