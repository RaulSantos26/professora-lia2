from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.adapters.dockerOperationsAdapter import DockerOperationsAdapter
from app.config.opsSettings import settings
from app.contracts.operationContract import (
    OperationalEventContract,
    OperationsStatusContract,
)
from app.repositories.operationalEventRepository import OperationalEventRepository
from app.security.internalTokenSecurity import requireInternalToken
from app.services.operationsService import OperationsService


router = APIRouter(
    prefix="/operations",
    tags=["operations"],
    dependencies=[Depends(requireInternalToken)],
)

operationsService = OperationsService(
    dockerOperationsAdapter=DockerOperationsAdapter(),
    operationalEventRepository=OperationalEventRepository(settings.auditPath),
)


@router.get("/status", response_model=OperationsStatusContract)
def getOperationsStatus() -> OperationsStatusContract:
    return operationsService.getStatus()


@router.get("/events", response_model=list[OperationalEventContract])
def getOperationalEvents(
    limit: int = Query(default=20, ge=1, le=100),
) -> list[OperationalEventContract]:
    return operationsService.operationalEventRepository.listEvents(limit)


@router.post(
    "/application/{action}",
    response_model=OperationalEventContract,
)
def executeApplicationAction(
    action: Literal["START", "STOP", "RESTART"],
) -> OperationalEventContract:
    return operationsService.executeApplicationAction(action)


@router.post(
    "/services/{serviceKey}/{action}",
    response_model=OperationalEventContract,
)
def executeServiceAction(
    serviceKey: Literal["backend", "studentWeb"],
    action: Literal["START", "STOP", "RESTART"],
) -> OperationalEventContract:
    return operationsService.executeServiceAction(serviceKey, action)
