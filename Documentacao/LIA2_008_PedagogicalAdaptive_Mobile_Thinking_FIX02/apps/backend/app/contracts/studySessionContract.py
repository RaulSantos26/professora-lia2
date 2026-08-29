from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

StudySessionType = Literal["STUDY","REVIEW","PRACTICE","MOCK_EXAM"]

class StudySessionStartContract(BaseModel):
    contractName: Literal["StudySessionStart.v1"] = "StudySessionStart.v1"
    sessionType: StudySessionType = "STUDY"
    notes: str | None = Field(default=None, max_length=2000)

class StudySessionItemContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    contractName: Literal["StudySessionItem.v1"] = "StudySessionItem.v1"
    studySessionItemId: UUID
    studySessionId: UUID
    studyScopeItemId: UUID
    status: Literal["PENDING","IN_PROGRESS","COMPLETED","SKIPPED"]
    timeSpentSeconds: int
    startedAt: datetime | None
    completedAt: datetime | None
    notes: str | None
    createdAt: datetime
    updatedAt: datetime

class StudySessionContract(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    contractName: Literal["StudySession.v1"] = "StudySession.v1"
    studySessionId: UUID
    studyScopeId: UUID
    studentId: UUID
    sessionType: StudySessionType
    status: Literal["IN_PROGRESS","COMPLETED","CANCELLED"]
    startedAt: datetime
    endedAt: datetime | None
    notes: str | None
    createdAt: datetime
    updatedAt: datetime

class StudySessionViewContract(BaseModel):
    contractName: Literal["StudySessionView.v1"] = "StudySessionView.v1"
    session: StudySessionContract
    items: list[StudySessionItemContract]
