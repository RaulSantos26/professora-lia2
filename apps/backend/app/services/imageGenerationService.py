import os
from pathlib import Path
from uuid import UUID

from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.contracts.imageGenerationContract import ImageGenerationTaskContract
from app.domain.common.domainError import DomainError
from app.persistence.models.imageGenerationTaskModel import ImageGenerationTaskModel
from app.repositories.imageGenerationRepository import ImageGenerationRepository
from app.repositories.studentRepository import StudentRepository
from app.services.contentGuardService import ContentGuardService
from app.services.pedagogicalContextService import PedagogicalContextService


class ImageGenerationService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = ImageGenerationRepository(session)
        self.studentRepository = StudentRepository(session)
        self.context = PedagogicalContextService(session)
        self.contentGuard = ContentGuardService()
        self.assetPath = Path(os.getenv("LIA2_IMAGE_ASSET_PATH", "/var/lib/lia2-generated-images"))

    def create(
        self, *, studentId: UUID, imageMode: str, instruction: str,
        materialIds: list[UUID], studentLearningContextId: UUID,
        studentSubjectId: UUID, studentLearningUnitId: UUID,
        agentThreadId: UUID | None, agentRunId: UUID | None,
        relatedVisualTaskId: UUID | None = None,
    ) -> ImageGenerationTaskContract:
        if self.studentRepository.findById(studentId) is None:
            raise DomainError(code="STUDENT_NOT_FOUND", message="Aluno não encontrado.", httpStatus=404)
        _, evidence, selectedIds = self.context.build(
            studentId=studentId, materialIds=materialIds,
            studentLearningContextId=studentLearningContextId,
            studentSubjectId=studentSubjectId,
            studentLearningUnitId=studentLearningUnitId,
            focusQuery=instruction,
        )
        title = self._title(instruction, imageMode)
        labels = self._labels(evidence, imageMode)
        model = ImageGenerationTaskModel(
            studentId=studentId, agentThreadId=agentThreadId, agentRunId=agentRunId,
            relatedVisualTaskId=relatedVisualTaskId, imageMode=imageMode,
            title=title, prompt=self._prompt(instruction, imageMode, evidence),
            labelsJson=labels, evidenceJson=evidence,
            sourceMaterialIds=[str(value) for value in selectedIds],
        )
        self.repository.create(model)
        self.session.commit()
        self.session.refresh(model)
        return self._toContract(model)

    def get(self, *, studentId: UUID, imageTaskId: UUID) -> ImageGenerationTaskContract:
        model = self.repository.findById(imageTaskId)
        if model is None or model.studentId != studentId:
            raise DomainError(code="IMAGE_TASK_NOT_FOUND", message="Imagem didática não encontrada.", httpStatus=404)
        return self._toContract(model)

    def list(self, *, studentId: UUID, taskIds: list[UUID] | None = None) -> list[ImageGenerationTaskContract]:
        return [self._toContract(model) for model in self.repository.listByStudent(studentId, taskIds)]

    def asset(self, *, studentId: UUID, imageTaskId: UUID) -> FileResponse:
        model = self.repository.findById(imageTaskId)
        if model is None or model.studentId != studentId or model.status != "READY" or not model.assetFilename:
            raise DomainError(code="IMAGE_ASSET_NOT_READY", message="A imagem ainda não está disponível.", httpStatus=404)
        path = (self.assetPath / model.assetFilename).resolve()
        if self.assetPath.resolve() not in path.parents or not path.is_file():
            raise DomainError(code="IMAGE_ASSET_NOT_FOUND", message="Arquivo de imagem não encontrado.", httpStatus=404)
        return FileResponse(path, media_type="image/png", filename=f"lia-{imageTaskId}.png")

    def _title(self, instruction: str, imageMode: str) -> str:
        prefix = "Mapa mental ilustrado" if imageMode == "MIND_MAP_COMPANION" else "Ilustração didática"
        cleaned = " ".join(instruction.split()).rstrip(".?!")
        return f"{prefix}: {cleaned[:180]}" if cleaned else prefix

    def _labels(self, evidence: list[dict], imageMode: str) -> list[str]:
        if imageMode == "MIND_MAP_COMPANION":
            return ["Ideia central", "Relações principais", "Conceitos da lição"]
        labels: list[str] = []
        for item in evidence[:3]:
            text = " ".join(str(item.get("excerpt") or "").split())
            if text:
                labels.append(text[:58].rstrip(".,;:"))
        return labels

    def _prompt(self, instruction: str, imageMode: str, evidence: list[dict]) -> str:
        safeEvidence = []
        for item in evidence[:4]:
            protected = self.contentGuard.protect(str(item.get("excerpt") or ""))
            if protected.classification == "UNTRUSTED_CONTENT":
                safeEvidence.append(" ".join(str(item.get("excerpt") or "").split())[:450])
        mode = (
            "an illustrated companion for an interactive mind map, with clear visual groups and no written words"
            if imageMode == "MIND_MAP_COMPANION"
            else "a concrete, accurate educational illustration"
        )
        return (
            f"Create {mode} about: {' '.join(instruction.split())[:1200]}. "
            "Use recognizable real objects and subject-specific elements, clean composition, "
            "Brazilian classroom visual quality, no letters, no labels, no watermark, no logo. "
            f"Reference facts: {' | '.join(safeEvidence)[:1600]}"
        )

    def _toContract(self, model: ImageGenerationTaskModel) -> ImageGenerationTaskContract:
        return ImageGenerationTaskContract(
            imageTaskId=model.imageTaskId, studentId=model.studentId,
            agentThreadId=model.agentThreadId, agentRunId=model.agentRunId,
            relatedVisualTaskId=model.relatedVisualTaskId, imageMode=model.imageMode,
            status=model.status, progressPercent=model.progressPercent,
            message=model.message, title=model.title, labels=model.labelsJson or [],
            assetUrl=(f"/api/students/{model.studentId}/image-tasks/{model.imageTaskId}/asset" if model.assetFilename else None),
            sourceMaterialIds=[UUID(value) for value in (model.sourceMaterialIds or [])],
            seed=model.seed, elapsedSeconds=model.elapsedSeconds,
            errorCode=model.errorCode, errorMessage=model.errorMessage,
            createdAt=model.createdAt, finishedAt=model.finishedAt,
        )
