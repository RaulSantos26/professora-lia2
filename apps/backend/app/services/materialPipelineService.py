import logging
from uuid import UUID

from app.domain.common.domainError import DomainError
from app.persistence.models.documentBlockModel import DocumentBlockModel
from app.persistence.models.documentPageModel import DocumentPageModel
from app.persistence.models.documentChunkModel import DocumentChunkModel
from app.persistence.models.evidenceModel import EvidenceModel
from app.persistence.models.materialProcessingJobModel import (
    MaterialProcessingJobModel,
)
from app.repositories.documentRepository import DocumentRepository
from app.repositories.materialProcessingJobRepository import (
    MaterialProcessingJobRepository,
)
from app.repositories.materialRepository import MaterialRepository
from app.services.aiExecutionPreferenceService import AiExecutionPreferenceService
from app.services.capabilityRouterService import CapabilityRouterService
from app.services.documentIngestionService import (
    DocumentIngestionService,
)
from app.services.embeddingService import EmbeddingService
from app.services.materialStorageService import MaterialStorageService
from app.services.ocrAnalysisService import OcrAnalysisService
from app.services.visionAnalysisService import VisionAnalysisService
from app.services.thinkingPolicyService import ThinkingPolicyService


logger = logging.getLogger(__name__)


class MaterialPipelineService:
    def __init__(self, session):
        self.session = session
        self.materialRepository = MaterialRepository(session)
        self.documentRepository = DocumentRepository(session)
        self.jobRepository = MaterialProcessingJobRepository(session)
        self.storage = MaterialStorageService()
        self.ocr = OcrAnalysisService()
        self.ingestion = DocumentIngestionService(session)
        self.router = CapabilityRouterService()
        self.aiPreference = AiExecutionPreferenceService()
        self.vision = VisionAnalysisService()
        self.thinking = ThinkingPolicyService()
        self.embedding = EmbeddingService()

    def run(
        self,
        job: MaterialProcessingJobModel,
    ) -> None:
        if job.jobType == "INDEX_RAG":
            self._indexExisting(job)
            return

        self._analyze(job)

    def _analyze(
        self,
        job: MaterialProcessingJobModel,
    ) -> None:
        material = self.materialRepository.findById(
            job.materialId
        )

        if material is None:
            raise DomainError(
                code="MATERIAL_NOT_FOUND",
                message="Material não encontrado para processamento.",
                httpStatus=404,
            )

        fileModel = self.materialRepository.findActiveFile(
            material.materialId
        )

        if fileModel is None:
            raise DomainError(
                code="MATERIAL_FILE_NOT_FOUND",
                message="Arquivo original do material não encontrado.",
                httpStatus=404,
            )

        self.jobRepository.updateProgress(
            job,
            stage="PREPARING",
            progressPercent=18,
            message="Preparando documento.",
        )
        self.session.commit()

        self.documentRepository.deleteByMaterialId(
            material.materialId
        )
        self.session.flush()

        self.storage.removeDerivedTree(
            material.studentId,
            material.materialId,
        )

        material.status = "PROCESSING"
        material.lastProcessingErrorCode = None
        material.lastProcessingErrorMessage = None

        document, version, textBlocks, visualPending, _ = (
            self.ingestion.ingest(
                studentId=material.studentId,
                materialId=material.materialId,
                materialFileId=fileModel.materialFileId,
                materialType=material.materialType,
                filePath=self.storage.absolutePath(
                    fileModel.storageKey
                ),
            )
        )

        self.jobRepository.updateProgress(
            job,
            stage="DOCUMENT_EXTRACTED",
            progressPercent=38,
            message=(
                f"Documento estruturado: {document.pageCount or 0} "
                f"página(s), {textBlocks} bloco(s) de texto."
            ),
        )
        self.session.commit()

        visionWarnings = False

        if visualPending:
            pendingBlocks = (
                self.documentRepository.listBlocksByProcessingStatus(
                    version.documentVersionId,
                    "PENDING_VISION",
                )
            )

            total = len(pendingBlocks)

            for index, block in enumerate(
                pendingBlocks,
                start=1,
            ):
                percent = 40 + int(
                    (index - 1)
                    / max(total, 1)
                    * 12
                )

                self.jobRepository.updateProgress(
                    job,
                    stage="OCR",
                    progressPercent=percent,
                    message=(
                        f"Lendo texto visual "
                        f"{index}/{total}."
                    ),
                )
                self.session.commit()

                self._processOcrBlock(
                    material=material,
                    versionId=version.documentVersionId,
                    block=block,
                )
                self.session.commit()

            try:
                visionModelId, visionAllowFallback = (
                    self.aiPreference.requestedModelFor(
                        material,
                        "VISION",
                    )
                )
                decision = self.router.route(
                    "VISION",
                    visionModelId,
                    allowFallback=visionAllowFallback,
                    additionalCapabilities=(
                        self.thinking.additionalCapabilities(
                            material.thinkingMode
                        )
                    ),
                )
                visionThinkingEnabled = self.thinking.resolve(
                    modelId=decision.effectiveModelId,
                    thinkingMode=material.thinkingMode,
                )
                job.effectiveVisionModelId = (
                    decision.effectiveModelId
                )
                job.fallbackReason = decision.fallbackReason

                for index, block in enumerate(
                    pendingBlocks,
                    start=1,
                ):
                    percent = 54 + int(
                        (index - 1)
                        / max(total, 1)
                        * 18
                    )

                    self.jobRepository.updateProgress(
                        job,
                        stage="VISION",
                        progressPercent=percent,
                        message=(
                            (
                                "Interpretando imagens e diagramas "
                                "com raciocínio "
                                if visionThinkingEnabled
                                else "Interpretando imagens e diagramas "
                            )
                            + f"{index}/{total}."
                        ),
                    )
                    self.session.commit()

                    self._processVisualBlock(
                        material=material,
                        versionId=version.documentVersionId,
                        block=block,
                        modelId=decision.effectiveModelId,
                        thinkingEnabled=visionThinkingEnabled,
                    )
                    self.session.commit()

            except DomainError as error:
                if (
                    error.code != "AI_CAPABILITY_MODEL_NOT_AVAILABLE"
                    or material.thinkingMode == "ON"
                ):
                    raise

                visionWarnings = True
                job.fallbackReason = error.message

        self._refreshDocumentStatus(
            document=document,
            version=version,
        )

        self.jobRepository.updateProgress(
            job,
            stage="EMBEDDING",
            progressPercent=78,
            message="Gerando embeddings para busca semântica.",
        )
        self.session.commit()

        embeddingWarnings = False

        chunks = self.documentRepository.listChunks(
            version.documentVersionId
        )

        if chunks:
            try:
                embeddingModelId, embeddingAllowFallback = (
                    self.aiPreference.requestedModelFor(
                        material,
                        "EMBEDDINGS",
                    )
                )
                decision, embedded = self.embedding.embedChunks(
                    chunks,
                    requestedModelId=embeddingModelId,
                    allowFallback=embeddingAllowFallback,
                )
                job.effectiveEmbeddingModelId = (
                    decision.effectiveModelId
                )

                logger.info(
                    "Embedded chunks materialId=%s count=%s model=%s",
                    material.materialId,
                    embedded,
                    decision.effectiveModelId,
                )

            except DomainError as error:
                if error.code != "AI_CAPABILITY_MODEL_NOT_AVAILABLE":
                    raise

                embeddingWarnings = True

                if job.fallbackReason:
                    job.fallbackReason += " " + error.message
                else:
                    job.fallbackReason = error.message

        self.jobRepository.updateProgress(
            job,
            stage="FINALIZING",
            progressPercent=94,
            message="Finalizando material e índice de evidências.",
        )

        pendingVision = self.documentRepository.visualPendingCount(
            version.documentVersionId
        )

        material.status = (
            "READY"
            if pendingVision == 0
            else "PARTIAL"
        )

        material.lastProcessingErrorCode = None
        material.lastProcessingErrorMessage = None

        warnings = visionWarnings or embeddingWarnings

        self.jobRepository.complete(
            job,
            warnings=warnings,
            message=(
                "Material processado com avisos."
                if warnings
                else "Material analisado e indexado com sucesso."
            ),
        )
        self.session.commit()

    def _indexExisting(
        self,
        job: MaterialProcessingJobModel,
    ) -> None:
        material = self.materialRepository.findById(
            job.materialId
        )

        if material is None:
            raise DomainError(
                code="MATERIAL_NOT_FOUND",
                message="Material não encontrado.",
                httpStatus=404,
            )

        document = self.documentRepository.findByMaterialId(
            material.materialId
        )

        if document is None:
            raise DomainError(
                code="MATERIAL_NOT_ANALYZED",
                message=(
                    "O material precisa ser analisado antes da indexação."
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

        self.jobRepository.updateProgress(
            job,
            stage="EMBEDDING",
            progressPercent=45,
            message="Gerando embeddings dos chunks existentes.",
        )
        self.session.commit()

        chunks = self.documentRepository.listChunks(
            version.documentVersionId
        )

        embeddingModelId, embeddingAllowFallback = (
            self.aiPreference.requestedModelFor(
                material,
                "EMBEDDINGS",
            )
        )
        decision, _ = self.embedding.embedChunks(
            chunks,
            requestedModelId=embeddingModelId,
            allowFallback=embeddingAllowFallback,
        )
        job.effectiveEmbeddingModelId = decision.effectiveModelId

        self.jobRepository.complete(
            job,
            warnings=False,
            message="Material indexado para RAG.",
        )
        self.session.commit()

    def _processOcrBlock(
        self,
        *,
        material,
        versionId: UUID,
        block: DocumentBlockModel,
    ) -> None:
        if not block.assetStorageKey:
            return

        page = self.session.get(
            DocumentPageModel,
            block.documentPageId,
        )

        # Native text already provides a deterministic text channel.
        # OCR is most valuable for scans/photos without native text.
        if page is not None and page.nativeText:
            return

        assetPath = self.storage.absolutePath(
            block.assetStorageKey
        )

        try:
            result = self.ocr.analyzeAndNormalize(
                assetPath
            )
        except Exception:
            logger.exception(
                "OCR failed materialId=%s blockId=%s",
                material.materialId,
                block.documentBlockId,
            )
            return

        block.orientationDegrees = (
            result.orientationDegrees
            if result.orientationDegrees
            else block.orientationDegrees
        )

        currentStructured = (
            block.structuredData
            if isinstance(block.structuredData, dict)
            else {}
        )
        block.structuredData = {
            **currentStructured,
            "ocr": {
                "orientationDegrees": result.orientationDegrees,
                "text": result.text,
            },
        }

        if not result.text.strip():
            return

        sequence = self.documentRepository.nextSequenceNumber(
            block.documentPageId
        )

        textBlock = DocumentBlockModel(
            documentPageId=block.documentPageId,
            sequenceNumber=sequence,
            blockType="TEXT",
            textContent=result.text,
            processingStatus="READY",
            orientationDegrees=result.orientationDegrees or None,
        )
        self.documentRepository.createBlock(textBlock)

        evidence = EvidenceModel(
            studentId=material.studentId,
            materialId=material.materialId,
            documentVersionId=versionId,
            documentPageId=block.documentPageId,
            documentBlockId=textBlock.documentBlockId,
            evidenceType="TEXT",
            locator="OCR local · texto extraído",
            excerpt=result.text[:1000],
            status="ACTIVE",
        )
        self.documentRepository.createEvidence(evidence)

        chunkIndex = self.documentRepository.nextChunkIndex(
            versionId
        )

        for chunkText in self.ingestion._chunks(
            result.text
        ):
            self.documentRepository.createChunk(
                DocumentChunkModel(
                    documentVersionId=versionId,
                    documentPageId=block.documentPageId,
                    documentBlockId=textBlock.documentBlockId,
                    evidenceId=evidence.evidenceId,
                    chunkIndex=chunkIndex,
                    content=chunkText,
                    tokenEstimate=max(
                        1,
                        len(chunkText) // 4,
                    ),
                    status="PENDING_EMBEDDING",
                )
            )
            chunkIndex += 1

    def _processVisualBlock(
        self,
        *,
        material,
        versionId: UUID,
        block: DocumentBlockModel,
        modelId: str,
        thinkingEnabled: bool,
    ) -> None:
        if not block.assetStorageKey:
            block.processingStatus = "ERROR"
            block.structuredData = {
                "error": "ASSET_STORAGE_KEY_MISSING"
            }
            return

        assetPath = self.storage.absolutePath(
            block.assetStorageKey
        )

        existingStructured = (
            block.structuredData
            if isinstance(block.structuredData, dict)
            else {}
        )
        ocrText = str(
            (
                existingStructured.get("ocr")
                or {}
            ).get("text")
            or ""
        ).strip()

        result = self.vision.analyze(
            imagePath=assetPath,
            modelId=modelId,
            thinkingEnabled=thinkingEnabled,
            ocrHint=ocrText,
        )

        previousOrientation = int(
            block.orientationDegrees or 0
        )

        block.processingStatus = "READY"
        block.orientationDegrees = (
            (previousOrientation + result.orientationDegrees) % 360
            or None
        )
        block.visionModelId = modelId
        block.textContent = (
            result.summary.strip()
            or result.extractedText.strip()
            or ocrText
            or None
        )
        block.structuredData = {
            **existingStructured,
            "vision": result.model_dump(),
            "visionMeta": {
                "modelId": modelId,
                "thinkingEnabled": thinkingEnabled,
            },
        }

        imageEvidence = self.documentRepository.findEvidenceByBlock(
            block.documentBlockId,
            "IMAGE",
        )

        if imageEvidence is not None:
            imageEvidence.excerpt = (
                result.summary[:1000]
                if result.summary
                else None
            )

        chunkIndex = self.documentRepository.nextChunkIndex(
            versionId
        )

        if result.extractedText.strip():
            textEvidence = EvidenceModel(
                studentId=material.studentId,
                materialId=material.materialId,
                documentVersionId=versionId,
                documentPageId=block.documentPageId,
                documentBlockId=block.documentBlockId,
                evidenceType="TEXT",
                locator="Vision/OCR · texto extraído",
                excerpt=result.extractedText[:1000],
                status="ACTIVE",
            )
            self.documentRepository.createEvidence(
                textEvidence
            )

            for chunkText in self.ingestion._chunks(
                result.extractedText
            ):
                self.documentRepository.createChunk(
                    DocumentChunkModel(
                        documentVersionId=versionId,
                        documentPageId=block.documentPageId,
                        documentBlockId=block.documentBlockId,
                        evidenceId=textEvidence.evidenceId,
                        chunkIndex=chunkIndex,
                        content=chunkText,
                        tokenEstimate=max(
                            1,
                            len(chunkText) // 4,
                        ),
                        status="PENDING_EMBEDDING",
                    )
                )
                chunkIndex += 1

        for element in result.visualElements:
            semanticType = {
                "FIGURE": "FIGURE",
                "DIAGRAM": "FIGURE",
                "TABLE": "TABLE",
                "PHOTO": "FIGURE",
                "CAPTION": "CAPTION",
                "OTHER": "OTHER",
            }.get(element.elementType, "OTHER")

            semanticText = (
                (
                    f"{element.title}. "
                    if element.title
                    else ""
                )
                + element.description
                + (
                    f" Rótulos: {', '.join(element.labels)}."
                    if element.labels
                    else ""
                )
            ).strip()

            semanticBlock = DocumentBlockModel(
                documentPageId=block.documentPageId,
                sequenceNumber=(
                    self.documentRepository.nextSequenceNumber(
                        block.documentPageId
                    )
                ),
                blockType=semanticType,
                textContent=semanticText,
                structuredData=element.model_dump(),
                processingStatus="READY",
                visionModelId=modelId,
            )
            self.documentRepository.createBlock(
                semanticBlock
            )

            evidenceType = (
                "TABLE"
                if semanticType == "TABLE"
                else "FIGURE"
            )

            semanticEvidence = EvidenceModel(
                studentId=material.studentId,
                materialId=material.materialId,
                documentVersionId=versionId,
                documentPageId=block.documentPageId,
                documentBlockId=semanticBlock.documentBlockId,
                evidenceType=evidenceType,
                locator=(
                    f"Vision · {element.elementType.lower()}"
                ),
                excerpt=semanticText[:1000],
                status="ACTIVE",
            )
            self.documentRepository.createEvidence(
                semanticEvidence
            )

            if semanticText:
                self.documentRepository.createChunk(
                    DocumentChunkModel(
                        documentVersionId=versionId,
                        documentPageId=block.documentPageId,
                        documentBlockId=semanticBlock.documentBlockId,
                        evidenceId=semanticEvidence.evidenceId,
                        chunkIndex=chunkIndex,
                        content=semanticText,
                        tokenEstimate=max(
                            1,
                            len(semanticText) // 4,
                        ),
                        status="PENDING_EMBEDDING",
                    )
                )
                chunkIndex += 1

    def _refreshDocumentStatus(
        self,
        *,
        document,
        version,
    ) -> None:
        pendingVision = self.documentRepository.visualPendingCount(
            version.documentVersionId
        )

        if pendingVision:
            document.status = "PARTIAL"
            version.extractionStatus = "PARTIAL"
            return

        pages = self.documentRepository.listPages(
            version.documentVersionId
        )

        hasPendingStructure = False

        for page in pages:
            blocks = self.documentRepository.listBlocks(
                page.documentPageId
            )

            hasPendingVision = any(
                block.processingStatus == "PENDING_VISION"
                for block in blocks
            )
            pagePendingStructure = any(
                block.processingStatus == "PENDING_STRUCTURE"
                for block in blocks
            )

            if pagePendingStructure:
                hasPendingStructure = True

            if not hasPendingVision:
                page.status = (
                    "READY"
                    if blocks
                    else "EMPTY"
                )

        if hasPendingStructure:
            document.status = "PARTIAL"
            version.extractionStatus = "PARTIAL"
        else:
            document.status = "READY"
            version.extractionStatus = "READY"
