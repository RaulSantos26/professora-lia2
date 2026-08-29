import json
from pathlib import Path

from app.contracts.operationContract import OperationalEventContract


class OperationalEventRepository:
    def __init__(self, auditPath: str):
        self.auditPath = Path(auditPath)

    def appendEvent(self, event: OperationalEventContract) -> None:
        self.auditPath.parent.mkdir(parents=True, exist_ok=True)

        with self.auditPath.open("a", encoding="utf-8") as file:
            file.write(event.model_dump_json())
            file.write("\n")

    def listEvents(self, limit: int = 20) -> list[OperationalEventContract]:
        if not self.auditPath.exists():
            return []

        lines = self.auditPath.read_text(encoding="utf-8").splitlines()
        selected = lines[-max(1, min(limit, 100)):]

        events: list[OperationalEventContract] = []
        for line in reversed(selected):
            try:
                events.append(
                    OperationalEventContract.model_validate(json.loads(line))
                )
            except Exception:
                continue

        return events
