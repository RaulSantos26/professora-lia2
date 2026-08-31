import os
from pathlib import Path
from uuid import UUID

from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.contracts.imageGenerationContract import ImageGenerationTaskContract
from app.domain.common.domainError import DomainError
from app.persistence.models.imageGenerationTaskModel import ImageGenerationTaskModel
from app.persistence.models.pedagogicalArtifactModel import PedagogicalArtifactModel
from app.repositories.imageGenerationRepository import ImageGenerationRepository
from app.repositories.studentRepository import StudentRepository
from app.services.contentGuardService import ContentGuardService
from app.services.pedagogicalContextService import PedagogicalContextService
from app.services.studentContentOwnershipService import StudentContentOwnershipService


class ImageGenerationService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = ImageGenerationRepository(session)
        self.studentRepository = StudentRepository(session)
        self.context = PedagogicalContextService(session)
        self.contentGuard = ContentGuardService()
        self.ownership = StudentContentOwnershipService(session)
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
        learningContext = self._learningContext(
            studentId,
            studentLearningUnitId,
        )
        title = self._title(instruction, imageMode)
        labels = self._labels(instruction, learningContext)
        model = ImageGenerationTaskModel(
            studentId=studentId, agentThreadId=agentThreadId, agentRunId=agentRunId,
            relatedVisualTaskId=relatedVisualTaskId, imageMode=imageMode,
            title=title, prompt=self._prompt(instruction, imageMode, evidence, learningContext),
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
    def createForPedagogicalMindMap(
        self,
        *,
        artifact: PedagogicalArtifactModel,
        evidence: list[dict],
    ) -> ImageGenerationTaskModel:
        """Queue exactly one Z-Image companion for a saved interactive map."""
        existing = self.repository.findByPedagogicalArtifactId(
            artifact.pedagogicalArtifactId
        )
        if existing is not None:
            artifact.imageTaskId = existing.imageTaskId
            return existing

        instruction = artifact.instruction or artifact.title
        learningContext = self._learningContext(
            artifact.studentId,
            artifact.studentLearningUnitId,
        )
        model = ImageGenerationTaskModel(
            studentId=artifact.studentId,
            agentThreadId=None,
            agentRunId=None,
            relatedVisualTaskId=None,
            relatedPedagogicalArtifactId=artifact.pedagogicalArtifactId,
            imageMode="MIND_MAP_COMPANION",
            title=self._title(instruction, "MIND_MAP_COMPANION"),
            prompt=self._prompt(instruction, "MIND_MAP_COMPANION", evidence, learningContext),
            labelsJson=self._labels(instruction, learningContext),
            evidenceJson=evidence,
            sourceMaterialIds=list(artifact.sourceMaterialIds or []),
        )
        self.repository.create(model)
        artifact.imageTaskId = model.imageTaskId
        return model

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

    def _learningContext(
        self,
        studentId: UUID,
        studentLearningUnitId: UUID,
    ) -> dict[str, str]:
        unit, subject, _ = self.ownership.assertUnitBelongsToStudent(
            studentLearningUnitId,
            studentId,
        )
        return {
            "subject": " ".join(subject.name.split())[:120],
            "lesson": " ".join(unit.title.split())[:180],
        }

    def _labels(
        self,
        instruction: str,
        learningContext: dict[str, str],
    ) -> list[str]:
        topic = " ".join(instruction.split()).rstrip(".?!")[:180]
        labels = [
            f"Matéria: {learningContext['subject']}",
            f"Lição: {learningContext['lesson']}",
        ]
        if topic:
            labels.append(f"Explicação visual: {topic}")
        return labels

    def _prompt(
        self,
        instruction: str,
        imageMode: str,
        evidence: list[dict],
        learningContext: dict[str, str],
    ) -> str:
        safeEvidence = []
        for item in evidence[:4]:
            protected = self.contentGuard.protect(str(item.get("excerpt") or ""))
            if protected.classification == "UNTRUSTED_CONTENT":
                safeEvidence.append(
                    " ".join(str(item.get("excerpt") or "").split())[:450]
                )
        mode = (
            "a single concrete visual companion for an interactive mind map"
            if imageMode == "MIND_MAP_COMPANION"
            else "a single concrete and accurate educational illustration"
        )
        return (
            f"Create {mode}. Brazilian school subject: {learningContext['subject']}. "
            f"Current lesson: {learningContext['lesson']}. "
            f"Required topic: {' '.join(instruction.split())[:1200]}. "
            "Use recognizable subject-specific objects and a clean classroom composition. "
            "CRITICAL: render absolutely no text of any kind inside the image: "
            "no letters, words, labels, captions, titles, legends, numbers, maps with names, "
            "diagrams with annotations, watermark or logo. The LIA interface renders the "
            "Portuguese-Brazil explanation outside the image. "
            f"Reference facts: {' | '.join(safeEvidence)[:1600]}"
        )

    def _toContract(self, model: ImageGenerationTaskModel) -> ImageGenerationTaskContract:
        return ImageGenerationTaskContract(
            imageTaskId=model.imageTaskId, studentId=model.studentId,
            agentThreadId=model.agentThreadId, agentRunId=model.agentRunId,
            relatedVisualTaskId=model.relatedVisualTaskId,
            relatedPedagogicalArtifactId=model.relatedPedagogicalArtifactId,
            imageMode=model.imageMode,
            status=model.status, progressPercent=model.progressPercent,
            message=model.message, title=model.title, labels=model.labelsJson or [],
            assetUrl=(f"/api/students/{model.studentId}/image-tasks/{model.imageTaskId}/asset" if model.assetFilename else None),
            sourceMaterialIds=[UUID(value) for value in (model.sourceMaterialIds or [])],
            seed=model.seed, elapsedSeconds=model.elapsedSeconds,
            errorCode=model.errorCode, errorMessage=model.errorMessage,
            createdAt=model.createdAt, finishedAt=model.finishedAt,
        )
