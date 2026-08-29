from dataclasses import dataclass

import docker
from docker.errors import APIError, NotFound


@dataclass(frozen=True)
class ManagedContainer:
    serviceKey: str
    containerName: str


class DockerOperationsAdapter:
    managedContainers = {
        "backend": ManagedContainer(
            serviceKey="backend",
            containerName="lia2-backend",
        ),
        "studentWeb": ManagedContainer(
            serviceKey="studentWeb",
            containerName="lia2-student-web",
        ),
    }

    def __init__(self, dockerClient=None):
        self.dockerClient = dockerClient or docker.from_env()

    def getManagedContainer(self, serviceKey: str):
        managed = self.managedContainers.get(serviceKey)

        if managed is None:
            raise ValueError("Serviço não permitido.")

        return self.dockerClient.containers.get(managed.containerName)

    def getServiceState(self, serviceKey: str) -> tuple[str, str]:
        managed = self.managedContainers.get(serviceKey)

        if managed is None:
            raise ValueError("Serviço não permitido.")

        try:
            container = self.dockerClient.containers.get(managed.containerName)
            container.reload()
            dockerState = (container.status or "").lower()

            if dockerState == "running":
                state = "RUNNING"
            elif dockerState in {"exited", "created", "dead"}:
                state = "STOPPED"
            else:
                state = "UNKNOWN"

            return managed.containerName, state
        except NotFound:
            return managed.containerName, "MISSING"

    def startService(self, serviceKey: str) -> str:
        container = self.getManagedContainer(serviceKey)
        container.start()
        return container.name

    def stopService(self, serviceKey: str) -> str:
        container = self.getManagedContainer(serviceKey)
        container.stop(timeout=10)
        return container.name

    def restartService(self, serviceKey: str) -> str:
        container = self.getManagedContainer(serviceKey)
        container.restart(timeout=10)
        return container.name
