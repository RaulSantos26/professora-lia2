from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.config.opsSettings import settings


class OpsAgentHealthContract(BaseModel):
    contractName: Literal["ServiceStatus.v1"] = "ServiceStatus.v1"
    serviceName: str = "lia2-ops-agent"
    status: Literal["ONLINE"] = "ONLINE"
    checkedAt: datetime
    version: str


router = APIRouter(tags=["health"])


@router.get("/health", response_model=OpsAgentHealthContract)
def getHealth() -> OpsAgentHealthContract:
    return OpsAgentHealthContract(
        checkedAt=datetime.now(timezone.utc),
        version=settings.release,
    )
