from datetime import datetime, timezone

import pytest

from app.contracts.serviceStatusContract import ServiceStatusContract
from app.services.platformHealthService import PlatformHealthService


class FakeHealthDependency:
    def __init__(self, serviceName: str, status: str):
        self.serviceName = serviceName
        self.status = status

    async def checkHealth(self):
        return ServiceStatusContract(
            serviceName=self.serviceName,
            status=self.status,
            checkedAt=datetime.now(timezone.utc),
        )


@pytest.mark.asyncio
async def testPlatformOnlineWhenAllDependenciesAreOnline():
    service = PlatformHealthService(
        environment="TEST",
        release="test",
        backendHealthClient=FakeHealthDependency("lia2-backend", "ONLINE"),
        ollamaHealthClient=FakeHealthDependency("ollama", "ONLINE"),
        postgresHealthRepository=FakeHealthDependency("postgres", "ONLINE"),
    )

    result = await service.getPlatformHealth()

    assert result.contractName == "PlatformHealth.v1"
    assert result.overallStatus == "ONLINE"
    assert len(result.services) == 4


@pytest.mark.asyncio
async def testPlatformDegradedWhenOneDependencyIsOffline():
    service = PlatformHealthService(
        environment="TEST",
        release="test",
        backendHealthClient=FakeHealthDependency("lia2-backend", "ONLINE"),
        ollamaHealthClient=FakeHealthDependency("ollama", "OFFLINE"),
        postgresHealthRepository=FakeHealthDependency("postgres", "ONLINE"),
    )

    result = await service.getPlatformHealth()

    assert result.overallStatus == "DEGRADED"
