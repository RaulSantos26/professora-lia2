from datetime import datetime, timezone
from uuid import uuid4

from app.contracts.operationContract import (
    ManagedServiceStatusContract,
    OperationalEventContract,
    OperationsStatusContract,
)


class OperationsService:
    applicationServiceOrder = ["backend", "studentWeb"]

    def __init__(self, dockerOperationsAdapter, operationalEventRepository):
        self.dockerOperationsAdapter = dockerOperationsAdapter
        self.operationalEventRepository = operationalEventRepository

    def getStatus(self) -> OperationsStatusContract:
        services = []

        for serviceKey in self.applicationServiceOrder:
            containerName, state = self.dockerOperationsAdapter.getServiceState(serviceKey)
            services.append(
                ManagedServiceStatusContract(
                    serviceKey=serviceKey,
                    containerName=containerName,
                    state=state,
                )
            )

        return OperationsStatusContract(services=services)

    def executeServiceAction(
        self,
        serviceKey: str,
        action: str,
    ) -> OperationalEventContract:
        return self._execute(
            target=serviceKey,
            action=action,
            serviceKeys=[serviceKey],
        )

    def executeApplicationAction(
        self,
        action: str,
    ) -> OperationalEventContract:
        serviceKeys = list(self.applicationServiceOrder)

        if action == "STOP":
            serviceKeys.reverse()

        return self._execute(
            target="application",
            action=action,
            serviceKeys=serviceKeys,
        )

    def _execute(
        self,
        target: str,
        action: str,
        serviceKeys: list[str],
    ) -> OperationalEventContract:
        startedAt = datetime.now(timezone.utc)
        affectedServices: list[str] = []
        errorType = None
        operationStatus = "SUCCESS"

        try:
            for serviceKey in serviceKeys:
                if action == "START":
                    affectedServices.append(
                        self.dockerOperationsAdapter.startService(serviceKey)
                    )
                elif action == "STOP":
                    affectedServices.append(
                        self.dockerOperationsAdapter.stopService(serviceKey)
                    )
                elif action == "RESTART":
                    affectedServices.append(
                        self.dockerOperationsAdapter.restartService(serviceKey)
                    )
                else:
                    raise ValueError("Ação não permitida.")
        except Exception as error:
            operationStatus = "FAILED"
            errorType = type(error).__name__

        event = OperationalEventContract(
            eventId=str(uuid4()),
            action=action,
            target=target,
            requestedAt=startedAt,
            finishedAt=datetime.now(timezone.utc),
            status=operationStatus,
            affectedServices=affectedServices,
            errorType=errorType,
        )

        self.operationalEventRepository.appendEvent(event)
        return event
