from datetime import datetime, timezone

from fastapi import APIRouter

from app.clients.backendHealthClient import BackendHealthClient
from app.clients.ollamaHealthClient import OllamaHealthClient
from app.clients.opsAgentHealthClient import OpsAgentHealthClient
from app.config.applicationSettings import settings
from app.contracts.serviceStatusContract import (
    PlatformHealthContract,
    ServiceStatusContract,
)
from app.repositories.postgresHealthRepository import PostgresHealthRepository
from app.services.platformHealthService import PlatformHealthService


router = APIRouter(tags=["platform"])

platformHealthService = PlatformHealthService(
    environment=settings.environment,
    release=settings.release,
    backendHealthClient=BackendHealthClient(settings.backendUrl),
    ollamaHealthClient=OllamaHealthClient(settings.ollamaUrl),
    postgresHealthRepository=PostgresHealthRepository(
        host=settings.postgresHost,
        port=settings.postgresPort,
        user=settings.postgresUser,
        password=settings.postgresPassword,
        database=settings.postgresDb,
    ),
    additionalHealthClients=[
        OpsAgentHealthClient(settings.opsAgentUrl),
    ],
)


@router.get("/health", response_model=ServiceStatusContract)
def getControlApiHealth() -> ServiceStatusContract:
    return ServiceStatusContract(
        serviceName="lia2-control-api",
        status="ONLINE",
        checkedAt=datetime.now(timezone.utc),
        version=settings.release,
    )


@router.get("/platform/health", response_model=PlatformHealthContract)
async def getPlatformHealth() -> PlatformHealthContract:
    return await platformHealthService.getPlatformHealth()
