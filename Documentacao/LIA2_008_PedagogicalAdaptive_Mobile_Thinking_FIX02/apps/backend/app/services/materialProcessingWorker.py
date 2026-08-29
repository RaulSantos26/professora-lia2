import logging
import os
import threading
import time
from uuid import UUID

from app.database.databaseSessionFactory import DatabaseSessionFactory
from app.domain.common.domainError import DomainError
from app.repositories.materialProcessingJobRepository import (
    MaterialProcessingJobRepository,
)
from app.repositories.materialRepository import MaterialRepository
from app.services.documentIngestionService import DocumentProcessingError
from app.services.materialPipelineService import MaterialPipelineService


logger = logging.getLogger(__name__)


class MaterialProcessingWorker:
    def __init__(self):
        self.enabled = (
            os.getenv(
                "LIA2_PROCESSING_WORKER_ENABLED",
                "false",
            ).strip().lower()
            == "true"
        )
        self.pollSeconds = float(
            os.getenv(
                "LIA2_PROCESSING_POLL_SECONDS",
                "1.0",
            )
        )
        self._stopEvent = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if not self.enabled:
            logger.info(
                "MaterialProcessingWorker disabled."
            )
            return

        if self._thread and self._thread.is_alive():
            return

        self._stopEvent.clear()
        self._recoverStaleJobs()

        self._thread = threading.Thread(
            target=self._loop,
            name="lia2-material-processing-worker",
            daemon=True,
        )
        self._thread.start()

        logger.info(
            "MaterialProcessingWorker started pollSeconds=%s",
            self.pollSeconds,
        )

    def stop(self) -> None:
        self._stopEvent.set()

        if self._thread:
            self._thread.join(timeout=5)

        logger.info("MaterialProcessingWorker stopped.")

    def _recoverStaleJobs(self) -> None:
        session = DatabaseSessionFactory()

        try:
            count = MaterialProcessingJobRepository(
                session
            ).requeueStale(olderThanMinutes=0)

            session.commit()

            if count:
                logger.warning(
                    "Requeued stale material processing jobs count=%s",
                    count,
                )
        finally:
            session.close()

    def _loop(self) -> None:
        while not self._stopEvent.is_set():
            processed = self._processOne()

            if not processed:
                self._stopEvent.wait(self.pollSeconds)

    def _processOne(self) -> bool:
        session = DatabaseSessionFactory()
        jobId: UUID | None = None
        materialId: UUID | None = None

        try:
            repository = MaterialProcessingJobRepository(
                session
            )

            job = repository.claimNext()

            if job is None:
                session.rollback()
                return False

            jobId = job.materialProcessingJobId
            materialId = job.materialId
            session.commit()

            job = repository.findById(jobId)

            if job is None:
                return False

            MaterialPipelineService(session).run(job)

            return True

        except DomainError as error:
            session.rollback()
            self._markFailed(
                jobId=jobId,
                materialId=materialId,
                errorCode=error.code,
                errorMessage=error.message,
            )
            logger.exception(
                "Material pipeline domain failure "
                "jobId=%s materialId=%s code=%s",
                jobId,
                materialId,
                error.code,
            )
            return True

        except DocumentProcessingError as error:
            session.rollback()
            self._markFailed(
                jobId=jobId,
                materialId=materialId,
                errorCode=error.code,
                errorMessage=error.safeMessage,
            )
            logger.exception(
                "Material document failure "
                "jobId=%s materialId=%s code=%s",
                jobId,
                materialId,
                error.code,
            )
            return True

        except Exception as error:
            session.rollback()
            self._markFailed(
                jobId=jobId,
                materialId=materialId,
                errorCode="MATERIAL_PIPELINE_INTERNAL_ERROR",
                errorMessage=(
                    "Falha inesperada no pipeline de material."
                ),
            )
            logger.exception(
                "Material pipeline unexpected failure "
                "jobId=%s materialId=%s",
                jobId,
                materialId,
            )
            return True

        finally:
            session.close()

    def _markFailed(
        self,
        *,
        jobId: UUID | None,
        materialId: UUID | None,
        errorCode: str,
        errorMessage: str,
    ) -> None:
        if jobId is None:
            return

        session = DatabaseSessionFactory()

        try:
            jobRepository = MaterialProcessingJobRepository(
                session
            )
            job = jobRepository.findById(jobId)

            if job is not None:
                jobRepository.fail(
                    job,
                    errorCode=errorCode,
                    errorMessage=errorMessage,
                )

            if materialId is not None:
                material = MaterialRepository(
                    session
                ).findById(materialId)

                if material is not None:
                    material.status = "ERROR"
                    material.lastProcessingErrorCode = errorCode
                    material.lastProcessingErrorMessage = (
                        errorMessage
                    )

            session.commit()

        finally:
            session.close()


materialProcessingWorker = MaterialProcessingWorker()
