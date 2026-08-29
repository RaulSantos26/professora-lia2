from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class OperationalEventContract(BaseModel):
    contractName: Literal["OperationalEvent.v1"] = "OperationalEvent.v1"
    eventId: str
    action: Literal["START", "STOP", "RESTART"]
    target: str
    requestedAt: datetime
    finishedAt: datetime
    status: Literal["SUCCESS", "FAILED"]
    affectedServices: list[str] = Field(default_factory=list)
    errorType: str | None = None


class ManagedServiceStatusContract(BaseModel):
    contractName: Literal["ManagedServiceStatus.v1"] = "ManagedServiceStatus.v1"
    serviceKey: Literal["backend", "studentWeb"]
    containerName: str
    state: Literal["RUNNING", "STOPPED", "MISSING", "UNKNOWN"]


class OperationsStatusContract(BaseModel):
    contractName: Literal["OperationsStatus.v1"] = "OperationsStatus.v1"
    services: list[ManagedServiceStatusContract]
