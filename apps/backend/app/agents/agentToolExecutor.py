from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.persistence.models.agentToolCallModel import AgentToolCallModel
from app.repositories.agentTutorRepository import AgentTutorRepository


class AgentToolExecutor:
    def __init__(self, session: Session):
        self.session = session
        self.repository = AgentTutorRepository(session)

    def execute(
        self,
        *,
        runId: UUID,
        toolName: str,
        request: dict,
        callback,
    ) -> dict:
        call = AgentToolCallModel(
            agentRunId=runId,
            toolName=toolName,
            status="STARTED",
            requestJson=self._safe(request),
        )
        self.repository.createToolCall(call)
        self.session.commit()

        try:
            result = callback()
            call.status = "COMPLETED"
            call.responseJson = self._safe(result)
            call.finishedAt = datetime.now(timezone.utc)
            self.session.commit()
            return result
        except Exception as error:
            call.status = "FAILED"
            call.errorCode = getattr(
                error,
                "code",
                type(error).__name__,
            )
            call.errorMessage = str(error)[:1000]
            call.finishedAt = datetime.now(timezone.utc)
            self.session.commit()
            raise

    def _safe(self, value):
        if isinstance(value, dict):
            safe = {}

            for key, item in value.items():
                if key == "context":
                    safe[key] = (
                        str(item)[:5000]
                        if item
                        else item
                    )
                else:
                    safe[key] = self._safe(item)

            return safe

        if isinstance(value, list):
            return [
                self._safe(item)
                for item in value[:30]
            ]

        if isinstance(value, UUID):
            return str(value)

        return value
