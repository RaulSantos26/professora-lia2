from datetime import datetime, timezone

import httpx

from app.contracts.serviceStatusContract import ServiceStatusContract


class OllamaHealthClient:
    def __init__(self, ollamaUrl: str):
        self.ollamaUrl = ollamaUrl.rstrip("/")

    async def checkHealth(self) -> ServiceStatusContract:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self.ollamaUrl}/api/tags")
                response.raise_for_status()
                payload = response.json()

            return ServiceStatusContract(
                serviceName="ollama",
                status="ONLINE",
                checkedAt=datetime.now(timezone.utc),
                details={"modelsVisible": len(payload.get("models", []))},
            )
        except Exception as error:
            return ServiceStatusContract(
                serviceName="ollama",
                status="OFFLINE",
                checkedAt=datetime.now(timezone.utc),
                details={"errorType": type(error).__name__},
            )
