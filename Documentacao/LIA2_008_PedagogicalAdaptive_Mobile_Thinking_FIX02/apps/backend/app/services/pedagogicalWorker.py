import logging
import os
import threading

from app.database.databaseSessionFactory import DatabaseSessionFactory
from app.domain.common.domainError import DomainError
from app.repositories.pedagogicalArtifactRepository import PedagogicalArtifactRepository
from app.services.pedagogicalService import PedagogicalService


logger = logging.getLogger(__name__)


class PedagogicalWorker:
    def __init__(self):
        self.enabled = (
            os.getenv(
                "LIA2_PEDAGOGICAL_WORKER_ENABLED",
                "false",
            ).strip().lower()
            == "true"
        )
        self.pollSeconds = float(
            os.getenv(
                "LIA2_PEDAGOGICAL_POLL_SECONDS",
                "1.0",
            )
        )
        self._stopEvent = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if not self.enabled:
            logger.info("PedagogicalWorker disabled.")
            return

        if self._thread and self._thread.is_alive():
            return

        self._stopEvent.clear()
        self._recoverRunning()
        self._thread = threading.Thread(
            target=self._loop,
            name="lia2-pedagogical-worker",
            daemon=True,
        )
        self._thread.start()
        logger.info("PedagogicalWorker started.")

    def stop(self) -> None:
        self._stopEvent.set()

        if self._thread:
            self._thread.join(timeout=5)

    def _recoverRunning(self) -> None:
        session = DatabaseSessionFactory()

        try:
            count = PedagogicalArtifactRepository(
                session
            ).requeueRunning()
            session.commit()

            if count:
                logger.warning(
                    "Requeued pedagogical artifacts count=%s",
                    count,
                )
        finally:
            session.close()

    def _loop(self) -> None:
        while not self._stopEvent.is_set():
            if not self._processOne():
                self._stopEvent.wait(self.pollSeconds)

    def _processOne(self) -> bool:
        session = DatabaseSessionFactory()

        try:
            repository = PedagogicalArtifactRepository(session)
            artifact = repository.claimNext()

            if artifact is None:
                session.rollback()
                return False

            artifactId = artifact.pedagogicalArtifactId
            session.commit()

            artifact = repository.findById(artifactId)

            if artifact is None:
                return False

            PedagogicalService(session).process(artifact)
            return True

        except DomainError as error:
            session.rollback()
            self._fail(
                artifactId if "artifactId" in locals() else None,
                error.code,
                error.message,
            )
            logger.exception(
                "Pedagogical generation failed code=%s",
                error.code,
            )
            return True

        except Exception:
            session.rollback()
            self._fail(
                artifactId if "artifactId" in locals() else None,
                "PEDAGOGICAL_INTERNAL_ERROR",
                "Falha inesperada ao gerar a atividade.",
            )
            logger.exception("Pedagogical generation unexpected failure.")
            return True

        finally:
            session.close()

    def _fail(
        self,
        artifactId,
        code: str,
        message: str,
    ) -> None:
        if artifactId is None:
            return

        session = DatabaseSessionFactory()

        try:
            repository = PedagogicalArtifactRepository(session)
            artifact = repository.findById(artifactId)

            if artifact is not None:
                repository.fail(
                    artifact,
                    code,
                    message,
                )
                session.commit()
        finally:
            session.close()


pedagogicalWorker = PedagogicalWorker()
