from fastapi import APIRouter

from app.contracts.serviceStatusContract import ServiceStatusContract
from app.services.healthService import HealthService


router = APIRouter(tags=["health"])
healthService = HealthService()


@router.get("/health", response_model=ServiceStatusContract)
def getHealth() -> ServiceStatusContract:
    return healthService.getStatus()
