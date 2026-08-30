import logging
import os
import threading
from datetime import datetime, timezone

from app.database.databaseSessionFactory import DatabaseSessionFactory
from app.domain.common.domainError import DomainError
from app.repositories.imageGenerationRepository import ImageGenerationRepository
from app.services.imageServiceClient import ImageServiceClient


logger = logging.getLogger(__name__)


class ImageGenerationWorker:
    def __init__(self):
        self.enabled = os.getenv("LIA2_IMAGE_WORKER_ENABLED", "false").lower() == "true"
        self.pollSeconds = float(os.getenv("LIA2_IMAGE_WORKER_POLL_SECONDS", "1.0"))
        self._stopEvent = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if not self.enabled or (self._thread and self._thread.is_alive()):
            return
        session = DatabaseSessionFactory()
        try:
            count = ImageGenerationRepository(session).requeueActive()
            session.commit()
            if count:
                logger.warning("Requeued image tasks count=%s", count)
        finally:
            session.close()
        self._thread = threading.Thread(target=self._loop, name="lia2-image-worker", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stopEvent.set()
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self) -> None:
        while not self._stopEvent.is_set():
            if not self._processOne():
                self._stopEvent.wait(self.pollSeconds)

    def _processOne(self) -> bool:
        session = DatabaseSessionFactory()
        task = None
        try:
            repository = ImageGenerationRepository(session)
            task = repository.claimNext()
            if task is None:
                session.rollback()
                return False
            taskId = task.imageTaskId
            session.commit()
            task = repository.findById(taskId)
            client = ImageServiceClient()
            payload = {"requestId": str(task.imageTaskId), "prompt": task.prompt, "title": task.title, "imageMode": task.imageMode, "labels": task.labelsJson or [], "width": 768, "height": 576, "steps": 9}
            remote = client.submit(payload)
            while remote.get("status") not in {"READY", "ERROR", "CANCELLED"} and not self._stopEvent.wait(self.pollSeconds):
                remote = client.get(str(task.imageTaskId))
            self._apply(task, remote)
            session.commit()
            return True
        except Exception as error:
            session.rollback()
            if task is not None:
                task = ImageGenerationRepository(session).findById(task.imageTaskId)
                if task is not None:
                    task.status = "ERROR"
                    task.progressPercent = 100
                    task.message = "Não foi possível gerar a imagem didática."
                    task.errorCode = getattr(error, "code", type(error).__name__)
                    task.errorMessage = str(error)[:1000]
                    task.finishedAt = datetime.now(timezone.utc)
                    session.commit()
            logger.exception("Image task failed")
            return True
        finally:
            session.close()

    def _apply(self, task, remote: dict) -> None:
        task.status = remote.get("status", "ERROR")
        task.progressPercent = int(remote.get("progressPercent", 100))
        task.message = str(remote.get("message") or task.message)[:500]
        task.assetFilename = remote.get("assetFilename")
        task.seed = remote.get("seed")
        task.elapsedSeconds = remote.get("elapsedSeconds")
        task.errorCode = remote.get("errorCode")
        task.errorMessage = remote.get("errorMessage")
        if task.status in {"READY", "ERROR", "CANCELLED"}:
            task.finishedAt = datetime.now(timezone.utc)


imageGenerationWorker = ImageGenerationWorker()
