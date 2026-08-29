from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ServiceStatusContract(BaseModel):
    contractName: Literal["ServiceStatus.v1"] = "ServiceStatus.v1"
    serviceName: str
    status: Literal["ONLINE", "OFFLINE", "DEGRADED"]
    checkedAt: datetime
    version: str
    environment: str
