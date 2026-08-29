import httpx

from app.contracts.operationContract import (
    OperationalEventContract,
    OperationsStatusContract,
)


class OpsAgentClient:
    def __init__(
        self,
        opsAgentUrl: str,
        internalToken: str,
    ):
        self.opsAgentUrl = opsAgentUrl.rstrip("/")
        self.internalToken = internalToken

    def _headers(self) -> dict[str, str]:
        return {
            "X-Lia2-Ops-Token": self.internalToken,
            "Accept": "application/json",
        }

    async def getStatus(self) -> OperationsStatusContract:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{self.opsAgentUrl}/operations/status",
                headers=self._headers(),
            )
            response.raise_for_status()

        return OperationsStatusContract.model_validate(response.json())

    async def listEvents(
        self,
        limit: int = 20,
    ) -> list[OperationalEventContract]:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{self.opsAgentUrl}/operations/events",
                params={"limit": limit},
                headers=self._headers(),
            )
            response.raise_for_status()

        return [
            OperationalEventContract.model_validate(item)
            for item in response.json()
        ]

    async def executeApplicationAction(
        self,
        action: str,
    ) -> OperationalEventContract:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.opsAgentUrl}/operations/application/{action}",
                headers=self._headers(),
            )
            response.raise_for_status()

        return OperationalEventContract.model_validate(response.json())

    async def executeServiceAction(
        self,
        serviceKey: str,
        action: str,
    ) -> OperationalEventContract:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.opsAgentUrl}/operations/services/{serviceKey}/{action}",
                headers=self._headers(),
            )
            response.raise_for_status()

        return OperationalEventContract.model_validate(response.json())
