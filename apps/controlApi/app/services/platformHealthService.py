from datetime import datetime, timezone

from app.contracts.serviceStatusContract import (
    PlatformHealthContract,
    ServiceStatusContract,
)


class PlatformHealthService:
    def __init__(
        self,
        environment: str,
        release: str,
        backendHealthClient,
        ollamaHealthClient,
        postgresHealthRepository,
        additionalHealthClients=None,
    ):
        self.environment = environment
        self.release = release
        self.backendHealthClient = backendHealthClient
        self.ollamaHealthClient = ollamaHealthClient
        self.postgresHealthRepository = postgresHealthRepository
        self.additionalHealthClients = additionalHealthClients or []

    async def getPlatformHealth(self) -> PlatformHealthContract:
        services = [
            ServiceStatusContract(
                serviceName="lia2-control-api",
                status="ONLINE",
                checkedAt=datetime.now(timezone.utc),
                version=self.release,
            ),
            await self.backendHealthClient.checkHealth(),
            await self.postgresHealthRepository.checkHealth(),
            await self.ollamaHealthClient.checkHealth(),
        ]

        for healthClient in self.additionalHealthClients:
            services.append(await healthClient.checkHealth())

        statuses = {service.status for service in services}

        if statuses == {"ONLINE"}:
            overallStatus = "ONLINE"
        elif "ONLINE" not in statuses:
            overallStatus = "OFFLINE"
        else:
            overallStatus = "DEGRADED"

        return PlatformHealthContract(
            environment=self.environment,
            release=self.release,
            overallStatus=overallStatus,
            checkedAt=datetime.now(timezone.utc),
            services=services,
        )
