from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


OperationAction = Literal["START", "STOP", "RESTART"]
OperationStatus = Literal["SUCCESS", "FAILED"]
ServiceKey = Literal["backend", "studentWeb"]


class OperationRequestContract(BaseModel):
    contractName: Literal["OperationRequest.v1"] = "OperationRequest.v1"
    action: OperationAction
    target: str


class OperationalEventContract(BaseModel):
    contractName: Literal["OperationalEvent.v1"] = "OperationalEvent.v1"
    eventId: str
    action: OperationAction
    target: str
    requestedAt: datetime
    finishedAt: datetime
    status: OperationStatus
    affectedServices: list[str] = Field(default_factory=list)
    errorType: str | None = None


class ManagedServiceStatusContract(BaseModel):
    contractName: Literal["ManagedServiceStatus.v1"] = "ManagedServiceStatus.v1"
    serviceKey: ServiceKey
    containerName: str
    state: Literal["RUNNING", "STOPPED", "MISSING", "UNKNOWN"]


class OperationsStatusContract(BaseModel):
    contractName: Literal["OperationsStatus.v1"] = "OperationsStatus.v1"
    services: list[ManagedServiceStatusContract]
