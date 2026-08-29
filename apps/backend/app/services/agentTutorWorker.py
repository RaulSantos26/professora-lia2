import logging
import os
import threading
from uuid import UUID

from app.agents.tutorAgentHarness import TutorAgentHarness
from app.database.databaseSessionFactory import DatabaseSessionFactory
from app.domain.common.domainError import DomainError
from app.repositories.agentTutorRepository import AgentTutorRepository


logger = logging.getLogger(__name__)


class AgentTutorWorker:
    def __init__(self):
        self.enabled = (
            os.getenv(
                "LIA2_AGENT_TUTOR_WORKER_ENABLED",
                "false",
            ).strip().lower()
            == "true"
        )
        self.pollSeconds = float(
            os.getenv(
                "LIA2_AGENT_TUTOR_POLL_SECONDS",
                "1.0",
            )
        )
        self._stopEvent = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if not self.enabled:
            logger.info("AgentTutorWorker disabled.")
            return

        if self._thread and self._thread.is_alive():
            return

        self._recover()
        self._stopEvent.clear()
        self._thread = threading.Thread(
            target=self._loop,
            name="lia2-agent-tutor-worker",
            daemon=True,
        )
        self._thread.start()
        logger.info("AgentTutorWorker started.")

    def stop(self) -> None:
        self._stopEvent.set()

        if self._thread:
            self._thread.join(timeout=5)

    def _recover(self) -> None:
        session = DatabaseSessionFactory()

        try:
            count = AgentTutorRepository(
                session
            ).requeueRunning()
            session.commit()

            if count:
                logger.warning(
                    "Requeued agent runs count=%s",
                    count,
                )
        finally:
            session.close()

    def _loop(self) -> None:
        while not self._stopEvent.is_set():
            if not self._processOne():
                self._stopEvent.wait(
                    self.pollSeconds
                )

    def _processOne(self) -> bool:
        session = DatabaseSessionFactory()
        runId: UUID | None = None

        try:
            repository = AgentTutorRepository(
                session
            )
            run = repository.claimNextRun()

            if run is None:
                session.rollback()
                return False

            runId = run.agentRunId
            threadId = run.agentThreadId
            userMessageId = run.userMessageId
            session.commit()

            run = repository.findRun(runId)
            thread = repository.findThread(threadId)
            userMessage = repository.findMessage(
                userMessageId
            )

            if (
                run is None
                or thread is None
                or userMessage is None
            ):
                raise RuntimeError(
                    "Agent run graph incomplete."
                )

            materialIds = self._materialScope(
                userMessage.actionsJson
            )

            TutorAgentHarness(session).process(
                run=run,
                thread=thread,
                userMessage=userMessage,
                materialIds=materialIds,
            )
            return True

        except DomainError as error:
            session.rollback()
            self._fail(
                runId,
                error.code,
                error.message,
            )
            logger.exception(
                "Agent run failed code=%s",
                error.code,
            )
            return True

        except Exception as error:
            session.rollback()
            self._fail(
                runId,
                "AGENT_INTERNAL_ERROR",
                str(error)[:1000],
            )
            logger.exception(
                "Agent run unexpected failure."
            )
            return True

        finally:
            session.close()

    def _materialScope(
        self,
        actions: list,
    ) -> list[UUID]:
        for action in actions or []:
            if action.get("type") != "MATERIAL_SCOPE":
                continue

            return [
                UUID(value)
                for value in (
                    action.get("materialIds")
                    or []
                )
            ]

        return []

    def _fail(
        self,
        runId: UUID | None,
        code: str,
        message: str,
    ) -> None:
        if runId is None:
            return

        session = DatabaseSessionFactory()

        try:
            repository = AgentTutorRepository(
                session
            )
            run = repository.findRun(runId)

            if run is not None:
                repository.failRun(
                    run,
                    code=code,
                    message=message,
                )
                session.commit()
        finally:
            session.close()


agentTutorWorker = AgentTutorWorker()
