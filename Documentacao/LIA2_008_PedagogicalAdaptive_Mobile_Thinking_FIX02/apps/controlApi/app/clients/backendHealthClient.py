from datetime import datetime, timezone

import httpx

from app.contracts.serviceStatusContract import ServiceStatusContract


class BackendHealthClient:
    def __init__(self, backendUrl: str):
        self.backendUrl = backendUrl.rstrip("/")

    async def checkHealth(self) -> ServiceStatusContract:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self.backendUrl}/health")
                response.raise_for_status()
                payload = response.json()

            return ServiceStatusContract(
                serviceName="lia2-backend",
                status="ONLINE",
                checkedAt=datetime.now(timezone.utc),
                version=payload.get("version"),
                details={"contract": payload.get("contractName")},
            )
        except Exception as error:
            return ServiceStatusContract(
                serviceName="lia2-backend",
                status="OFFLINE",
                checkedAt=datetime.now(timezone.utc),
                details={"errorType": type(error).__name__},
            )
