from pathlib import Path

from app.repositories.operationalEventRepository import OperationalEventRepository
from app.services.operationsService import OperationsService


class FakeDockerOperationsAdapter:
    def __init__(self):
        self.actions = []

    def getServiceState(self, serviceKey):
        return f"lia2-{serviceKey}", "RUNNING"

    def startService(self, serviceKey):
        self.actions.append(("START", serviceKey))
        return f"lia2-{serviceKey}"

    def stopService(self, serviceKey):
        self.actions.append(("STOP", serviceKey))
        return f"lia2-{serviceKey}"

    def restartService(self, serviceKey):
        self.actions.append(("RESTART", serviceKey))
        return f"lia2-{serviceKey}"


def testApplicationStopKeepsControlPlaneOutsideAllowlist(tmp_path: Path):
    adapter = FakeDockerOperationsAdapter()
    repository = OperationalEventRepository(
        str(tmp_path / "operationalEvents.jsonl")
    )
    service = OperationsService(adapter, repository)

    event = service.executeApplicationAction("STOP")

    assert event.status == "SUCCESS"
    assert adapter.actions == [
        ("STOP", "studentWeb"),
        ("STOP", "backend"),
    ]


def testStatusReturnsOnlyManagedApplicationServices(tmp_path: Path):
    adapter = FakeDockerOperationsAdapter()
    repository = OperationalEventRepository(
        str(tmp_path / "operationalEvents.jsonl")
    )
    service = OperationsService(adapter, repository)

    result = service.getStatus()

    assert [item.serviceKey for item in result.services] == [
        "backend",
        "studentWeb",
    ]
