from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.clients.opsAgentClient import OpsAgentClient
from app.config.applicationSettings import settings
from app.contracts.operationContract import (
    OperationalEventContract,
    OperationsStatusContract,
)
from app.security.adminTokenSecurity import requireAdminToken


router = APIRouter(
    prefix="/operations",
    tags=["operations"],
    dependencies=[Depends(requireAdminToken)],
)

opsAgentClient = OpsAgentClient(
    opsAgentUrl=settings.opsAgentUrl,
    internalToken=settings.opsInternalToken,
)


@router.get("/status", response_model=OperationsStatusContract)
async def getOperationsStatus() -> OperationsStatusContract:
    return await opsAgentClient.getStatus()


@router.get("/events", response_model=list[OperationalEventContract])
async def getOperationalEvents(
    limit: int = Query(default=20, ge=1, le=100),
) -> list[OperationalEventContract]:
    return await opsAgentClient.listEvents(limit)


@router.post(
    "/application/{action}",
    response_model=OperationalEventContract,
)
async def executeApplicationAction(
    action: Literal["START", "STOP", "RESTART"],
) -> OperationalEventContract:
    return await opsAgentClient.executeApplicationAction(action)


@router.post(
    "/services/{serviceKey}/{action}",
    response_model=OperationalEventContract,
)
async def executeServiceAction(
    serviceKey: Literal["backend", "studentWeb"],
    action: Literal["START", "STOP", "RESTART"],
) -> OperationalEventContract:
    return await opsAgentClient.executeServiceAction(serviceKey, action)
