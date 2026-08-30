from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.contracts.materialProcessingContract import (
    MaterialAsyncBatchUploadResultContract,
    MaterialAsyncUploadItemContract,
    MaterialProcessingJobContract,
)
from app.contracts.aiExecutionPreferenceContract import AiExecutionPreferenceContract
from app.services.aiExecutionPreferenceService import AiExecutionPreferenceService
from app.domain.common.domainError import DomainError
from app.persistence.models.materialFileModel import MaterialFileModel
from app.persistence.models.materialModel import MaterialModel
from app.persistence.models.materialProcessingJobModel import (
    MaterialProcessingJobModel,
)
from app.repositories.materialProcessingJobRepository import (
    MaterialProcessingJobRepository,
)
from app.repositories.materialRepository import MaterialRepository
from app.services.aiModelRegistryService import AiModelRegistryService
from app.services.materialOwnershipService import MaterialOwnershipService
from app.services.materialStorageService import MaterialStorageService


class MaterialAsyncService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = MaterialRepository(session)
        self.jobRepository = MaterialProcessingJobRepository(session)
        self.ownership = MaterialOwnershipService(session)
        self.storage = MaterialStorageService()
        self.modelRegistry = AiModelRegistryService()
        self.aiPreference = AiExecutionPreferenceService()

    async def uploadBatch(
        self,
        *,
        studentId: UUID,
        title: str | None,
        description: str | None,
        studentLearningContextId: UUID | None,
        studentSubjectId: UUID | None,
        studentLearningUnitId: UUID | None,
        analysisRequested: bool,
        studyEnabled: bool,
        requestedModelId: str | None,
        aiMode: str,
        fixedModelId: str | None,
        textModelId: str | None,
        visionModelId: str | None,
        embeddingModelId: str | None,
        thinkingMode: str,
        files: list[UploadFile],
    ) -> MaterialAsyncBatchUploadResultContract:
        if not files:
            raise DomainError(
                code="MATERIAL_BATCH_EMPTY",
                message="Selecione ao menos um arquivo.",
                httpStatus=422,
            )

        self.ownership.validate(
            studentId,
            studentLearningContextId,
            studentSubjectId,
            studentLearningUnitId,
        )

        preference = AiExecutionPreferenceContract(
            mode=aiMode,
            fixedModelId=fixedModelId,
            textModelId=textModelId,
            visionModelId=visionModelId,
            embeddingModelId=embeddingModelId,
            thinkingMode=thinkingMode,
        )
        self.aiPreference.validate(preference)

        items = []
        sourceGroupId = uuid4() if len(files) > 1 else None

        for sourceSequence, upload in enumerate(files, start=1):
            fileName = upload.filename or "material"

            try:
                result = await self._storeOne(
                    studentId=studentId,
                    title=title,
                    description=description,
                    studentLearningContextId=studentLearningContextId,
                    studentSubjectId=studentSubjectId,
                    studentLearningUnitId=studentLearningUnitId,
                    analysisRequested=analysisRequested,
                    studyEnabled=studyEnabled,
                    requestedModelId=requestedModelId,
                    preference=preference,
                    sourceGroupId=sourceGroupId,
                    sourceSequence=(
                        sourceSequence
                        if sourceGroupId is not None
                        else None
                    ),
                    upload=upload,
                    multiFile=len(files) > 1,
                )

                items.append(result)

            except DomainError as error:
                self.session.rollback()

                items.append(
                    MaterialAsyncUploadItemContract(
                        fileName=fileName,
                        success=False,
                        errorCode=error.code,
                        errorMessage=error.message,
                    )
                )

            except Exception:
                self.session.rollback()

                items.append(
                    MaterialAsyncUploadItemContract(
                        fileName=fileName,
                        success=False,
                        errorCode="MATERIAL_UPLOAD_ERROR",
                        errorMessage=(
                            "Falha inesperada ao armazenar o arquivo."
                        ),
                    )
                )

        successCount = sum(
            1
            for item in items
            if item.success
        )

        return MaterialAsyncBatchUploadResultContract(
            totalFiles=len(items),
            successCount=successCount,
            errorCount=len(items) - successCount,
            items=items,
        )

    def queueAnalyze(
        self,
        *,
        studentId: UUID,
        materialId: UUID,
    ) -> MaterialProcessingJobContract:
        material = self._ownedMaterial(
            studentId,
            materialId,
        )

        material.analysisRequested = True
        material.status = "PROCESSING"

        job = self._createJob(
            material=material,
            jobType="ANALYZE",
        )

        self.session.commit()

        return self._toJobContract(job)

    def queueIndex(
        self,
        *,
        studentId: UUID,
        materialId: UUID,
    ) -> MaterialProcessingJobContract:
        material = self._ownedMaterial(
            studentId,
            materialId,
        )

        job = self._createJob(
            material=material,
            jobType="INDEX_RAG",
        )

        self.session.commit()

        return self._toJobContract(job)

    def getJob(
        self,
        jobId: UUID,
    ) -> MaterialProcessingJobContract:
        job = self.jobRepository.findById(jobId)

        if job is None:
            raise DomainError(
                code="PROCESSING_JOB_NOT_FOUND",
                message="Processamento não encontrado.",
                httpStatus=404,
            )

        return self._toJobContract(job)

    def listJobs(
        self,
        *,
        studentId: UUID,
        activeOnly: bool,
    ) -> list[MaterialProcessingJobContract]:
        jobs = (
            self.jobRepository.listActiveByStudentId(studentId)
            if activeOnly
            else self.jobRepository.listByStudentId(studentId)
        )

        return [
            self._toJobContract(job)
            for job in jobs
        ]

    async def _storeOne(
        self,
        *,
        studentId: UUID,
        title: str | None,
        description: str | None,
        studentLearningContextId: UUID | None,
        studentSubjectId: UUID | None,
        studentLearningUnitId: UUID | None,
        analysisRequested: bool,
        studyEnabled: bool,
        requestedModelId: str | None,
        preference: AiExecutionPreferenceContract,
        sourceGroupId: UUID | None,
        sourceSequence: int | None,
        upload: UploadFile,
        multiFile: bool,
    ) -> MaterialAsyncUploadItemContract:
        fileName = upload.filename or "material"

        materialTitle = (
            Path(fileName).stem
            if multiFile or not title
            else " ".join(title.split())
        )

        if len(materialTitle.strip()) < 2:
            materialTitle = fileName

        mimeType = (
            upload.content_type
            or "application/octet-stream"
        )
        materialType = self._resolveMaterialType(
            fileName,
            mimeType,
        )

        self.aiPreference.validateForMaterial(
            preference,
            materialType=materialType,
            analysisRequested=analysisRequested,
        )

        material = MaterialModel(
            studentId=studentId,
            studentLearningContextId=studentLearningContextId,
            studentSubjectId=studentSubjectId,
            studentLearningUnitId=studentLearningUnitId,
            title=materialTitle.strip(),
            materialType=materialType,
            sourceType="UPLOAD",
            description=(
                " ".join(description.split())
                if description
                else None
            ),
            status=(
                "PROCESSING"
                if analysisRequested
                else "UPLOADED"
            ),
            analysisRequested=analysisRequested,
            studyEnabled=studyEnabled,
            sourceFileRetained=True,
            discardSourceAfterExtraction=(
                materialType == "IMAGE"
            ),
            requestedModelId=requestedModelId,
            aiMode=preference.mode,
            fixedModelId=preference.fixedModelId,
            textModelId=preference.textModelId,
            visionModelId=preference.visionModelId,
            embeddingModelId=preference.embeddingModelId,
            thinkingMode=preference.thinkingMode,
            sourceGroupId=sourceGroupId,
            sourceSequence=sourceSequence,
            lastProcessingErrorCode=None,
            lastProcessingErrorMessage=None,
        )
        self.repository.create(material)

        materialFileId = uuid4()
        storageKey = None

        try:
            storageKey, sizeBytes, sha256 = await self.storage.save(
                studentId,
                material.materialId,
                materialFileId,
                upload,
            )

            fileModel = MaterialFileModel(
                materialFileId=materialFileId,
                materialId=material.materialId,
                originalFileName=fileName,
                storageKey=storageKey,
                mimeType=mimeType,
                sizeBytes=sizeBytes,
                sha256=sha256,
                status="ACTIVE",
            )
            self.repository.createFile(fileModel)

            job = None

            if analysisRequested:
                job = self._createJob(
                    material=material,
                    jobType="ANALYZE",
                )

            self.session.commit()

            return MaterialAsyncUploadItemContract(
                fileName=fileName,
                success=True,
                materialId=material.materialId,
                materialTitle=material.title,
                materialStatus=material.status,
                job=(
                    self._toJobContract(job)
                    if job is not None
                    else None
                ),
            )

        except ValueError as error:
            self.session.rollback()

            if storageKey:
                self.storage.remove(storageKey)

            if str(error) == "FILE_TOO_LARGE":
                raise DomainError(
                    code="MATERIAL_FILE_TOO_LARGE",
                    message=(
                        f"O arquivo {fileName} excede o limite "
                        f"de 50 MB."
                    ),
                    httpStatus=413,
                ) from error

            raise

        except Exception:
            self.session.rollback()

            if storageKey:
                self.storage.remove(storageKey)

            raise

    def _createJob(
        self,
        *,
        material: MaterialModel,
        jobType: str,
    ) -> MaterialProcessingJobModel:
        activeJobs = self.jobRepository.listActiveByStudentId(
            material.studentId
        )

        duplicate = next(
            (
                job
                for job in activeJobs
                if job.materialId == material.materialId
                and job.jobType == jobType
            ),
            None,
        )

        if duplicate is not None:
            return duplicate

        job = MaterialProcessingJobModel(
            materialId=material.materialId,
            studentId=material.studentId,
            jobType=jobType,
            status="QUEUED",
            stage="QUEUED",
            progressPercent=8,
            message=(
                "Arquivo recebido. Aguardando processamento."
            ),
            requestedModelId=material.requestedModelId,
        )

        return self.jobRepository.create(job)

    def _ownedMaterial(
        self,
        studentId: UUID,
        materialId: UUID,
    ) -> MaterialModel:
        material = self.repository.findById(materialId)

        if material is None or material.studentId != studentId:
            raise DomainError(
                code="MATERIAL_NOT_FOUND",
                message="Material não encontrado para este aluno.",
                httpStatus=404,
            )

        return material

    def _toJobContract(
        self,
        job: MaterialProcessingJobModel,
    ) -> MaterialProcessingJobContract:
        material = self.repository.findById(job.materialId)

        return MaterialProcessingJobContract(
            materialProcessingJobId=job.materialProcessingJobId,
            materialId=job.materialId,
            materialTitle=(material.title if material else None),
            studentId=job.studentId,
            jobType=job.jobType,
            status=job.status,
            stage=job.stage,
            progressPercent=job.progressPercent,
            message=job.message,
            requestedModelId=job.requestedModelId,
            effectiveVisionModelId=job.effectiveVisionModelId,
            effectiveEmbeddingModelId=job.effectiveEmbeddingModelId,
            fallbackReason=job.fallbackReason,
            errorCode=job.errorCode,
            errorMessage=job.errorMessage,
            createdAt=job.createdAt,
            startedAt=job.startedAt,
            finishedAt=job.finishedAt,
        )

    def _resolveMaterialType(
        self,
        fileName: str,
        mimeType: str,
    ) -> str:
        extension = Path(fileName).suffix.lower()

        if mimeType == "application/pdf" or extension == ".pdf":
            return "PDF"

        if mimeType.startswith("image/") or extension in {
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
            ".gif",
            ".bmp",
        }:
            return "IMAGE"

        if mimeType.startswith("text/") or extension in {
            ".txt",
            ".md",
            ".csv",
        }:
            return "TEXT"

        if extension in {
            ".doc",
            ".docx",
            ".odt",
            ".rtf",
        }:
            return "DOCUMENT"

        return "OTHER"
