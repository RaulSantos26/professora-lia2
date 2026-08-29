from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistence.models.agentMessageModel import AgentMessageModel
from app.persistence.models.agentRunModel import AgentRunModel
from app.persistence.models.agentThreadModel import AgentThreadModel
from app.persistence.models.agentToolCallModel import AgentToolCallModel


class AgentTutorRepository:
    def __init__(self, session: Session):
        self.session = session

    def createThread(
        self,
        model: AgentThreadModel,
    ) -> AgentThreadModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findThread(
        self,
        threadId: UUID,
    ) -> AgentThreadModel | None:
        return self.session.get(AgentThreadModel, threadId)

    def listThreads(
        self,
        studentId: UUID,
        limit: int = 50,
    ) -> list[AgentThreadModel]:
        statement = (
            select(AgentThreadModel)
            .where(
                AgentThreadModel.studentId == studentId,
                AgentThreadModel.status == "ACTIVE",
            )
            .order_by(
                AgentThreadModel.lastMessageAt.desc().nullslast(),
                AgentThreadModel.updatedAt.desc(),
            )
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def createMessage(
        self,
        model: AgentMessageModel,
    ) -> AgentMessageModel:
        self.session.add(model)
        self.session.flush()
        return model

    def listMessages(
        self,
        threadId: UUID,
        limit: int = 100,
    ) -> list[AgentMessageModel]:
        statement = (
            select(AgentMessageModel)
            .where(
                AgentMessageModel.agentThreadId == threadId
            )
            .order_by(AgentMessageModel.createdAt.asc())
            .limit(limit)
        )
        return list(self.session.scalars(statement))

    def findMessage(
        self,
        messageId: UUID,
    ) -> AgentMessageModel | None:
        return self.session.get(
            AgentMessageModel,
            messageId,
        )

    def createRun(
        self,
        model: AgentRunModel,
    ) -> AgentRunModel:
        self.session.add(model)
        self.session.flush()
        return model

    def findRun(
        self,
        runId: UUID,
    ) -> AgentRunModel | None:
        return self.session.get(AgentRunModel, runId)

    def lastRun(
        self,
        threadId: UUID,
    ) -> AgentRunModel | None:
        statement = (
            select(AgentRunModel)
            .where(
                AgentRunModel.agentThreadId == threadId
            )
            .order_by(AgentRunModel.createdAt.desc())
            .limit(1)
        )
        return self.session.scalar(statement)

    def activeRun(
        self,
        threadId: UUID,
    ) -> AgentRunModel | None:
        statement = (
            select(AgentRunModel)
            .where(
                AgentRunModel.agentThreadId == threadId,
                AgentRunModel.status.in_(
                    ["QUEUED", "RUNNING"]
                ),
            )
            .order_by(AgentRunModel.createdAt.desc())
            .limit(1)
        )
        return self.session.scalar(statement)

    def claimNextRun(self) -> AgentRunModel | None:
        statement = (
            select(AgentRunModel)
            .where(AgentRunModel.status == "QUEUED")
            .order_by(AgentRunModel.createdAt.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        run = self.session.scalar(statement)

        if run is None:
            return None

        run.status = "RUNNING"
        run.stage = "PLANNING"
        run.progressPercent = 12
        run.message = "A Lia está entendendo o pedido."
        run.startedAt = datetime.now(timezone.utc)
        self.session.flush()
        return run

    def requeueRunning(self) -> int:
        statement = select(AgentRunModel).where(
            AgentRunModel.status == "RUNNING"
        )
        runs = list(self.session.scalars(statement))

        for run in runs:
            run.status = "QUEUED"
            run.stage = "QUEUED"
            run.progressPercent = 5
            run.message = "Retomando conversa após reinício."
            run.startedAt = None

        self.session.flush()
        return len(runs)

    def createToolCall(
        self,
        model: AgentToolCallModel,
    ) -> AgentToolCallModel:
        self.session.add(model)
        self.session.flush()
        return model

    def listToolCalls(
        self,
        runId: UUID,
    ) -> list[AgentToolCallModel]:
        statement = (
            select(AgentToolCallModel)
            .where(
                AgentToolCallModel.agentRunId == runId
            )
            .order_by(
                AgentToolCallModel.startedAt.asc()
            )
        )
        return list(self.session.scalars(statement))

    def completeRun(
        self,
        run: AgentRunModel,
        *,
        assistantMessageId: UUID,
    ) -> None:
        run.status = "READY"
        run.stage = "READY"
        run.progressPercent = 100
        run.message = "Resposta pronta."
        run.assistantMessageId = assistantMessageId
        run.finishedAt = datetime.now(timezone.utc)
        self.session.flush()

    def failRun(
        self,
        run: AgentRunModel,
        *,
        code: str,
        message: str,
    ) -> None:
        run.status = "FAILED"
        run.stage = "FAILED"
        run.progressPercent = min(
            max(run.progressPercent, 1),
            99,
        )
        run.message = "A Lia não conseguiu concluir esta resposta."
        run.errorCode = code
        run.errorMessage = message
        run.finishedAt = datetime.now(timezone.utc)
        self.session.flush()
