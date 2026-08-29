from datetime import datetime, timezone

import httpx

from app.contracts.serviceStatusContract import ServiceStatusContract


class OpsAgentHealthClient:
    def __init__(self, opsAgentUrl: str):
        self.opsAgentUrl = opsAgentUrl.rstrip("/")

    async def checkHealth(self) -> ServiceStatusContract:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self.opsAgentUrl}/health")
                response.raise_for_status()
                payload = response.json()

            return ServiceStatusContract(
                serviceName="lia2-ops-agent",
                status="ONLINE",
                checkedAt=datetime.now(timezone.utc),
                version=payload.get("version"),
            )
        except Exception as error:
            return ServiceStatusContract(
                serviceName="lia2-ops-agent",
                status="OFFLINE",
                checkedAt=datetime.now(timezone.utc),
                details={"errorType": type(error).__name__},
            )
