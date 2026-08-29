from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ServiceStatusContract(BaseModel):
    contractName: Literal["ServiceStatus.v1"] = "ServiceStatus.v1"
    serviceName: str
    status: Literal["ONLINE", "OFFLINE", "DEGRADED"]
    checkedAt: datetime
    version: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class PlatformHealthContract(BaseModel):
    contractName: Literal["PlatformHealth.v1"] = "PlatformHealth.v1"
    environment: str
    release: str
    overallStatus: Literal["ONLINE", "DEGRADED", "OFFLINE"]
    checkedAt: datetime
    services: list[ServiceStatusContract]
