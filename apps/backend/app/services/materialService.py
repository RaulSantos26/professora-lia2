import logging
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.contracts.aiExecutionPreferenceContract import MaterialAiPreferenceUpdateContract
from app.contracts.documentStructureContract import (
    DocumentBlockViewContract,
    DocumentPageViewContract,
    DocumentStructureContract,
)
from app.contracts.materialContract import (
    MaterialBatchItemContract,
    MaterialBatchUploadResultContract,
    MaterialContract,
    MaterialModelPreferenceUpdateContract,
    MaterialStudyUsageUpdateContract,
    MaterialUploadResultContract,
)
from app.domain.common.domainError import DomainError
from app.mappers.materialMapper import MaterialMapper
from app.persistence.models.materialFileModel import MaterialFileModel
from app.persistence.models.materialModel import MaterialModel
from app.repositories.documentRepository import DocumentRepository
from app.repositories.learningAttemptRepository import LearningAttemptRepository
from app.repositories.pedagogicalArtifactRepository import PedagogicalArtifactRepository
from app.repositories.visualTaskRepository import VisualTaskRepository
from app.repositories.materialProcessingJobRepository import MaterialProcessingJobRepository
from app.repositories.materialRepository import MaterialRepository
from app.services.aiExecutionPreferenceService import AiExecutionPreferenceService
from app.services.aiModelRegistryService import AiModelRegistryService
from app.services.documentIngestionService import (
    DocumentIngestionService,
    DocumentProcessingError,
)
from app.services.materialOwnershipService import MaterialOwnershipService
from app.services.materialStorageService import MaterialStorageService


logger = logging.getLogger(__name__)


class MaterialService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = MaterialRepository(session)
        self.pedagogicalRepository = PedagogicalArtifactRepository(session)
        self.attemptRepository = LearningAttemptRepository(session)
        self.visualTaskRepository = VisualTaskRepository(session)
        self.jobRepository = MaterialProcessingJobRepository(session)
        self.documentRepository = DocumentRepository(session)
        self.ownershipService = MaterialOwnershipService(session)
        self.storageService = MaterialStorageService()
        self.ingestionService = DocumentIngestionService(session)
        self.modelRegistryService = AiModelRegistryService()
        self.aiPreferenceService = AiExecutionPreferenceService()

    async def upload(
        self,
        studentId: UUID,
        title: str,
        description: str | None,
        studentLearningContextId: UUID | None,
        studentSubjectId: UUID | None,
        studentLearningUnitId: UUID | None,
        analysisRequested: bool,
        studyEnabled: bool,
        requestedModelId: str | None,
        upload: UploadFile,
    ) -> MaterialUploadResultContract:
        self.ownershipService.validate(
            studentId,
            studentLearningContextId,
            studentSubjectId,
            studentLearningUnitId,
        )

        self.modelRegistryService.validateModel(requestedModelId)

        normalizedTitle = " ".join(title.split())

        if len(normalizedTitle) < 2:
            raise DomainError(
                code="MATERIAL_TITLE_INVALID",
                message="Informe um título válido para o material.",
                httpStatus=422,
            )

        fileName = upload.filename or "material"
        mimeType = upload.content_type or "application/octet-stream"
        materialType = self._resolveMaterialType(fileName, mimeType)

        if materialType == "IMAGE":
            raise DomainError(
                code="IMAGE_UPLOAD_REQUIRES_ASYNC_TEXT_PIPELINE",
                message=(
                    "Envie fotos pelo processamento assíncrono da Lia "
                    "para preservar somente o texto extraído."
                ),
                httpStatus=409,
            )

        material = MaterialModel(
            studentId=studentId,
            studentLearningContextId=studentLearningContextId,
            studentSubjectId=studentSubjectId,
            studentLearningUnitId=studentLearningUnitId,
            title=normalizedTitle,
            materialType=materialType,
            sourceType="UPLOAD",
            description=(
                " ".join(description.split())
                if description
                else None
            ),
            status="UPLOADED",
            analysisRequested=analysisRequested,
            studyEnabled=studyEnabled,
            requestedModelId=requestedModelId,
            lastProcessingErrorCode=None,
            lastProcessingErrorMessage=None,
        )

        self.repository.create(material)
        materialFileId = uuid4()
        storageKey = None

        try:
            storageKey, sizeBytes, sha256 = await self.storageService.save(
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

            # Persist the original before any parser is invoked.
            self.session.commit()
            self.session.refresh(material)
            self.session.refresh(fileModel)

        except ValueError as error:
            self.session.rollback()

            if storageKey:
                self.storageService.remove(storageKey)

            if str(error) == "FILE_TOO_LARGE":
                raise DomainError(
                    code="MATERIAL_FILE_TOO_LARGE",
                    message="O arquivo excede o limite de 50 MB.",
                    httpStatus=413,
                ) from error

            raise

        except Exception:
            self.session.rollback()

            if storageKey:
                self.storageService.remove(storageKey)

            raise

        if not analysisRequested:
            return MaterialUploadResultContract(
                material=MaterialMapper.toContract(material),
                file=MaterialMapper.fileToContract(fileModel),
                documentId=None,
                documentVersionId=None,
                pageCount=0,
                textBlockCount=0,
                visualPendingCount=0,
                chunkCount=0,
                analysisPerformed=False,
            )

        return self._analyzePersisted(
            studentId=studentId,
            material=material,
            fileModel=fileModel,
        )

    async def uploadBatch(
        self,
        studentId: UUID,
        title: str | None,
        description: str | None,
        studentLearningContextId: UUID | None,
        studentSubjectId: UUID | None,
        studentLearningUnitId: UUID | None,
        analysisRequested: bool,
        studyEnabled: bool,
        requestedModelId: str | None,
        files: list[UploadFile],
    ) -> MaterialBatchUploadResultContract:
        if not files:
            raise DomainError(
                code="MATERIAL_BATCH_EMPTY",
                message="Selecione ao menos um arquivo.",
                httpStatus=422,
            )

        items = []

        for upload in files:
            fileName = upload.filename or "material"

            try:
                singleTitle = (
                    " ".join(title.split())
                    if title and len(files) == 1
                    else Path(fileName).stem or "Material"
                )

                result = await self.upload(
                    studentId=studentId,
                    title=singleTitle,
                    description=description,
                    studentLearningContextId=studentLearningContextId,
                    studentSubjectId=studentSubjectId,
                    studentLearningUnitId=studentLearningUnitId,
                    analysisRequested=analysisRequested,
                    studyEnabled=studyEnabled,
                    requestedModelId=requestedModelId,
                    upload=upload,
                )

                items.append(
                    MaterialBatchItemContract(
                        fileName=fileName,
                        success=True,
                        result=result,
                    )
                )

            except DomainError as error:
                items.append(
                    MaterialBatchItemContract(
                        fileName=fileName,
                        success=False,
                        errorCode=error.code,
                        errorMessage=error.message,
                    )
                )

            except Exception:
                logger.exception(
                    "Unexpected batch upload error for %s",
                    fileName,
                )

                items.append(
                    MaterialBatchItemContract(
                        fileName=fileName,
                        success=False,
                        errorCode="INTERNAL_ERROR",
                        errorMessage=(
                            "Falha inesperada ao processar este arquivo."
                        ),
                    )
                )

        successCount = sum(1 for item in items if item.success)

        return MaterialBatchUploadResultContract(
            totalFiles=len(items),
            successCount=successCount,
            errorCount=len(items) - successCount,
            items=items,
        )

    def analyze(
        self,
        studentId: UUID,
        materialId: UUID,
    ) -> MaterialUploadResultContract:
        material = self._requireOwnedMaterial(studentId, materialId)
        fileModel = self.repository.findActiveFile(materialId)

        if fileModel is None:
            raise DomainError(
                code="MATERIAL_FILE_NOT_FOUND",
                message="Arquivo original do material não encontrado.",
                httpStatus=404,
            )

        self.modelRegistryService.validateModel(
            material.requestedModelId
        )

        material.analysisRequested = True
        self.session.commit()
        self.session.refresh(material)

        return self._analyzePersisted(
            studentId=studentId,
            material=material,
            fileModel=fileModel,
        )

    def updateModelPreference(
        self,
        studentId: UUID,
        materialId: UUID,
        request: MaterialModelPreferenceUpdateContract,
    ) -> MaterialContract:
        material = self._requireOwnedMaterial(
            studentId,
            materialId,
        )

        self.modelRegistryService.validateModel(
            request.requestedModelId
        )

        material.requestedModelId = request.requestedModelId

        self.session.commit()
        self.session.refresh(material)

        return MaterialMapper.toContract(material)

    def updateAiPreference(
        self,
        studentId: UUID,
        materialId: UUID,
        request: MaterialAiPreferenceUpdateContract,
    ) -> MaterialContract:
        material = self._requireOwnedMaterial(
            studentId,
            materialId,
        )

        self.aiPreferenceService.validateForMaterial(
            request,
            materialType=material.materialType,
            analysisRequested=True,
        )

        material.aiMode = request.mode
        material.fixedModelId = request.fixedModelId
        material.textModelId = request.textModelId
        material.visionModelId = request.visionModelId
        material.embeddingModelId = request.embeddingModelId
        material.thinkingMode = request.thinkingMode

        # Legacy compatibility field remains readable but new execution
        # logic uses the explicit preference fields.
        material.requestedModelId = (
            request.fixedModelId
            if request.mode == "FIXED"
            else request.textModelId
        )

        self.session.commit()
        self.session.refresh(material)

        return MaterialMapper.toContract(material)

    def updateStudyUsage(
        self,
        studentId: UUID,
        materialId: UUID,
        request: MaterialStudyUsageUpdateContract,
    ) -> MaterialContract:
        material = self._requireOwnedMaterial(studentId, materialId)
        material.studyEnabled = request.studyEnabled

        self.session.commit()
        self.session.refresh(material)

        return MaterialMapper.toContract(material)

    def deleteMaterial(
        self,
        studentId: UUID,
        materialId: UUID,
    ) -> None:
        material = self._requireOwnedMaterial(studentId, materialId)

        activeJobs = self.jobRepository.listActiveByStudentId(studentId)
        if any(job.materialId == materialId for job in activeJobs):
            raise DomainError(
                code="MATERIAL_PROCESSING_ACTIVE",
                message=(
                    "Aguarde o processamento do material terminar "
                    "antes de excluí-lo."
                ),
                httpStatus=409,
            )

        activePedagogical = [
            artifact
            for artifact in self.pedagogicalRepository.listAllByStudent(studentId)
            if (
                str(materialId) in (artifact.sourceMaterialIds or [])
                and artifact.status in {"QUEUED", "RUNNING"}
            )
        ]
        if activePedagogical:
            raise DomainError(
                code="PEDAGOGICAL_PROCESSING_ACTIVE",
                message=(
                    "Aguarde a atividade da Lia terminar antes "
                    "de excluir este material."
                ),
                httpStatus=409,
            )

        try:
            material.status = "ARCHIVED"
            material.studyEnabled = False
            self.session.commit()
            logger.info(
                "Material archived without deleting learning artifacts "
                "studentId=%s materialId=%s",
                studentId,
                materialId,
            )
        except IntegrityError as error:
            self.session.rollback()
            raise DomainError(
                code="MATERIAL_ARCHIVE_CONSTRAINT_ERROR",
                message="O material não pôde ser arquivado.",
                httpStatus=409,
            ) from error

    def listMaterials(
        self,
        studentId: UUID,
    ) -> list[MaterialContract]:
        self.ownershipService.validate(
            studentId,
            None,
            None,
            None,
        )

        return [
            MaterialMapper.toContract(model)
            for model in self.repository.listByStudentId(studentId)
        ]

    def getStructure(
        self,
        materialId: UUID,
    ) -> DocumentStructureContract:
        material = self.repository.findById(materialId)

        if material is None:
            raise DomainError(
                code="MATERIAL_NOT_FOUND",
                message="Material não encontrado.",
                httpStatus=404,
            )

        document = self.documentRepository.findByMaterialId(materialId)

        if document is None:
            raise DomainError(
                code="MATERIAL_NOT_ANALYZED",
                message=(
                    "Este material foi armazenado sem análise. "
                    "Use a ação Analisar quando quiser processá-lo."
                ),
                httpStatus=409,
            )

        version = self.documentRepository.findLatestVersion(
            document.documentId
        )

        if version is None:
            raise DomainError(
                code="DOCUMENT_VERSION_NOT_FOUND",
                message="Versão do documento não encontrada.",
                httpStatus=404,
            )

        pageContracts = []

        for page in self.documentRepository.listPages(
            version.documentVersionId
        ):
            blocks = [
                DocumentBlockViewContract(
                    documentBlockId=block.documentBlockId,
                    sequenceNumber=block.sequenceNumber,
                    blockType=block.blockType,
                    textContent=block.textContent,
                    processingStatus=block.processingStatus,
                    orientationDegrees=block.orientationDegrees,
                    visionModelId=block.visionModelId,
                    visionThinkingEnabled=(
                        (
                            block.structuredData.get("visionMeta")
                            or {}
                        ).get("thinkingEnabled")
                        if isinstance(block.structuredData, dict)
                        else None
                    ),
                )
                for block in self.documentRepository.listBlocks(
                    page.documentPageId
                )
            ]

            pageContracts.append(
                DocumentPageViewContract(
                    documentPageId=page.documentPageId,
                    pageNumber=page.pageNumber,
                    nativeText=page.nativeText,
                    status=page.status,
                    blocks=blocks,
                )
            )

        return DocumentStructureContract(
            documentId=document.documentId,
            documentVersionId=version.documentVersionId,
            extractionStatus=version.extractionStatus,
            pageCount=document.pageCount or len(pageContracts),
            pages=pageContracts,
            evidenceCount=self.documentRepository.evidenceCount(
                version.documentVersionId
            ),
            chunkCount=self.documentRepository.chunkCount(
                version.documentVersionId
            ),
            embeddedChunkCount=self.documentRepository.embeddedChunkCount(
                version.documentVersionId
            ),
            visualPendingCount=self.documentRepository.visualPendingCount(
                version.documentVersionId
            ),
        )

    def getFilePath(
        self,
        materialId: UUID,
    ) -> tuple[Path, str, str]:
        material = self.repository.findById(materialId)

        if material is None:
            raise DomainError(
                code="MATERIAL_NOT_FOUND",
                message="Material não encontrado.",
                httpStatus=404,
            )

        fileModel = self.repository.findActiveFile(materialId)

        if fileModel is None:
            raise DomainError(
                code="MATERIAL_FILE_NOT_FOUND",
                message="Arquivo do material não encontrado.",
                httpStatus=404,
            )

        return (
            self.storageService.absolutePath(fileModel.storageKey),
            fileModel.originalFileName,
            fileModel.mimeType,
        )

    def _analyzePersisted(
        self,
        studentId: UUID,
        material: MaterialModel,
        fileModel: MaterialFileModel,
    ) -> MaterialUploadResultContract:
        try:
            # Re-analysis is deterministic: old derived structure is removed,
            # original file remains the source of truth.
            self.documentRepository.deleteByMaterialId(
                material.materialId
            )
            self.session.flush()

            material.status = "PROCESSING"
            material.lastProcessingErrorCode = None
            material.lastProcessingErrorMessage = None

            document, version, textBlocks, visualPending, chunkCount = (
                self.ingestionService.ingest(
                    studentId=studentId,
                    materialId=material.materialId,
                    materialFileId=fileModel.materialFileId,
                    materialType=material.materialType,
                    filePath=self.storageService.absolutePath(
                        fileModel.storageKey
                    ),
                )
            )

            material.status = (
                "READY"
                if document.status == "READY"
                else "PROCESSING"
            )

            self.session.commit()
            self.session.refresh(material)

            return MaterialUploadResultContract(
                material=MaterialMapper.toContract(material),
                file=MaterialMapper.fileToContract(fileModel),
                documentId=document.documentId,
                documentVersionId=version.documentVersionId,
                pageCount=document.pageCount or 0,
                textBlockCount=textBlocks,
                visualPendingCount=visualPending,
                chunkCount=chunkCount,
                analysisPerformed=True,
            )

        except DocumentProcessingError as error:
            self.session.rollback()

            persisted = self.repository.findById(material.materialId)

            if persisted is not None:
                persisted.status = "ERROR"
                persisted.lastProcessingErrorCode = error.code
                persisted.lastProcessingErrorMessage = error.safeMessage
                self.session.commit()

            raise DomainError(
                code=error.code,
                message=error.safeMessage,
                httpStatus=422,
            ) from error

        except DomainError:
            self.session.rollback()
            raise

        except Exception as error:
            self.session.rollback()

            persisted = self.repository.findById(material.materialId)

            if persisted is not None:
                persisted.status = "ERROR"
                persisted.lastProcessingErrorCode = "MATERIAL_PROCESSING_ERROR"
                persisted.lastProcessingErrorMessage = (
                    "Falha inesperada durante o processamento."
                )
                self.session.commit()

            logger.exception(
                "Unexpected material processing error materialId=%s",
                material.materialId,
            )

            raise DomainError(
                code="MATERIAL_PROCESSING_ERROR",
                message=(
                    "O arquivo foi armazenado, mas ocorreu uma falha "
                    "durante a análise. Você pode tentar novamente ou "
                    "excluir o material."
                ),
                httpStatus=500,
            ) from error

    def _requireOwnedMaterial(
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
