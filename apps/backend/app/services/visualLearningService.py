from uuid import UUID

from sqlalchemy.orm import Session

from app.contracts.visualTaskContract import (
    VisualTaskContract,
    VisualTaskCreateContract,
)
from app.domain.common.domainError import DomainError
from app.persistence.models.visualTaskModel import VisualTaskModel
from app.repositories.pedagogicalArtifactRepository import PedagogicalArtifactRepository
from app.repositories.studentRepository import StudentRepository
from app.repositories.visualTaskRepository import VisualTaskRepository
from app.services.capabilityRouterService import CapabilityRouterService
from app.services.pedagogicalContextService import PedagogicalContextService
from app.services.thinkingPolicyService import ThinkingPolicyService
from app.services.visualGenerationService import VisualGenerationService
from app.skills.visualLayoutSkill import VisualLayoutSkill
from app.tools.wikimediaVisualReferenceTool import WikimediaVisualReferenceTool


class VisualLearningService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = VisualTaskRepository(session)
        self.studentRepository = StudentRepository(session)
        self.artifactRepository = PedagogicalArtifactRepository(session)
        self.context = PedagogicalContextService(session)
        self.router = CapabilityRouterService()
        self.thinking = ThinkingPolicyService()
        self.generator = VisualGenerationService()
        self.layout = VisualLayoutSkill()
        self.referenceResearch = WikimediaVisualReferenceTool()

    def create(
        self,
        *,
        studentId: UUID,
        request: VisualTaskCreateContract,
        agentThreadId: UUID | None = None,
        agentRunId: UUID | None = None,
    ) -> VisualTaskContract:
        if self.studentRepository.findById(studentId) is None:
            raise DomainError(
                code="STUDENT_NOT_FOUND",
                message="Aluno não encontrado.",
                httpStatus=404,
            )

        requestedMaterialIds = list(
            request.materialIds
        )

        if (
            not requestedMaterialIds
            and request.pedagogicalArtifactId is not None
        ):
            sourceArtifact = self.artifactRepository.findById(
                request.pedagogicalArtifactId
            )

            if (
                sourceArtifact is not None
                and sourceArtifact.studentId == studentId
            ):
                requestedMaterialIds = [
                    UUID(value)
                    for value in (
                        sourceArtifact.sourceMaterialIds
                        or []
                    )
                ]

        contextText, evidence, materialIds = self.context.build(
            studentId=studentId,
            materialIds=requestedMaterialIds,
            focusQuery=request.instruction,
        )

        modelId = request.requestedTextModelId
        allowFallback = modelId is None

        decision = self.router.route(
            "TEXT",
            modelId,
            allowFallback=allowFallback,
            additionalCapabilities=(
                self.thinking.additionalCapabilities(
                    request.thinkingMode
                )
            ),
        )

        thinkingEnabled = self.thinking.resolve(
            modelId=decision.effectiveModelId,
            thinkingMode=request.thinkingMode,
        )

        references = (
            self.referenceResearch.research(
                evidenceContext=contextText,
                instruction=request.instruction or "",
            )
            if request.visualType in {"ANIMATION_2D", "SCENE_3D"}
            else []
        )

        semanticSpec = self._fromArtifact(
            studentId=studentId,
            request=request,
        )

        if semanticSpec is None:
            semanticSpec = self.generator.generate(
                visualType=request.visualType,
                evidenceContext=contextText,
                instruction=(
                    request.instruction
                    or self._defaultInstruction(
                        request.visualType
                    )
                ),
                modelId=decision.effectiveModelId,
                thinkingEnabled=thinkingEnabled,
                researchReferences=references,
            )

        renderer, spec = self._prepare(
            request.visualType,
            semanticSpec,
        )
        if references:
            spec = {**spec, "referenceSources": references}

        model = VisualTaskModel(
            studentId=studentId,
            agentThreadId=agentThreadId,
            agentRunId=agentRunId,
            pedagogicalArtifactId=(
                request.pedagogicalArtifactId
            ),
            visualType=request.visualType,
            status="READY",
            title=(
                request.title
                or str(
                    spec.get("title")
                    or self._defaultTitle(
                        request.visualType
                    )
                )
            ),
            renderer=renderer,
            specJson=spec,
            evidenceJson=evidence,
            sourceMaterialIds=[str(value) for value in materialIds],
            effectiveModelId=decision.effectiveModelId,
            thinkingEnabled=thinkingEnabled,
        )

        self.repository.create(model)
        self.session.commit()
        self.session.refresh(model)

        return self._toContract(model)

    def get(
        self,
        *,
        studentId: UUID,
        visualTaskId: UUID,
    ) -> VisualTaskContract:
        model = self.repository.findById(visualTaskId)

        if model is None or model.studentId != studentId:
            raise DomainError(
                code="VISUAL_TASK_NOT_FOUND",
                message="Visualização não encontrada.",
                httpStatus=404,
            )

        return self._toContract(model)

    def list(
        self,
        studentId: UUID,
    ) -> list[VisualTaskContract]:
        return [
            self._toContract(model)
            for model in self.repository.listByStudent(
                studentId
            )
        ]

    def _fromArtifact(
        self,
        *,
        studentId: UUID,
        request: VisualTaskCreateContract,
    ) -> dict | None:
        if (
            request.visualType != "MIND_MAP"
            or request.pedagogicalArtifactId is None
        ):
            return None

        artifact = self.artifactRepository.findById(
            request.pedagogicalArtifactId
        )

        if (
            artifact is None
            or artifact.studentId != studentId
            or artifact.artifactType != "MIND_MAP"
            or artifact.status != "READY"
        ):
            raise DomainError(
                code="MIND_MAP_ARTIFACT_INVALID",
                message=(
                    "O mapa mental de origem não está disponível "
                    "para este aluno."
                ),
                httpStatus=409,
            )

        return artifact.contentJson or None

    def _prepare(
        self,
        visualType: str,
        spec: dict,
    ) -> tuple[str, dict]:
        if visualType == "MIND_MAP":
            return "SVG", self.layout.layoutMindMap(spec)

        if visualType == "DIAGRAM":
            return "SVG", self.layout.layoutDiagram(spec)

        if visualType == "CHART":
            return "CANVAS", spec

        if visualType == "ANIMATION_2D":
            return (
                "CANVAS",
                self.layout.normalizeAnimation(spec),
            )

        return (
            "THREE",
            self.layout.normalizeScene3d(spec),
        )

    def _defaultInstruction(
        self,
        visualType: str,
    ) -> str:
        return {
            "MIND_MAP": (
                "Organize os conceitos centrais em um mapa mental."
            ),
            "DIAGRAM": (
                "Mostre as relações entre os conceitos em um diagrama."
            ),
            "CHART": (
                "Crie um gráfico somente se as evidências contiverem "
                "valores quantitativos comparáveis."
            ),
            "ANIMATION_2D": (
                "Represente dinamicamente o processo em duas dimensões."
            ),
            "SCENE_3D": (
                "Crie uma cena 3D somente quando a estrutura espacial "
                "ajudar a compreender o conteúdo."
            ),
        }[visualType]

    def _defaultTitle(
        self,
        visualType: str,
    ) -> str:
        return {
            "MIND_MAP": "Mapa mental",
            "DIAGRAM": "Diagrama",
            "CHART": "Gráfico",
            "ANIMATION_2D": "Animação",
            "SCENE_3D": "Cena 3D",
        }[visualType]

    def _toContract(
        self,
        model: VisualTaskModel,
    ) -> VisualTaskContract:
        return VisualTaskContract(
            visualTaskId=model.visualTaskId,
            studentId=model.studentId,
            agentThreadId=model.agentThreadId,
            agentRunId=model.agentRunId,
            pedagogicalArtifactId=(
                model.pedagogicalArtifactId
            ),
            visualType=model.visualType,
            status=model.status,
            title=model.title,
            renderer=model.renderer,
            spec=model.specJson,
            evidence=model.evidenceJson,
            sourceMaterialIds=[UUID(value) for value in (model.sourceMaterialIds or [])],
            effectiveModelId=model.effectiveModelId,
            thinkingEnabled=model.thinkingEnabled,
            createdAt=model.createdAt,
        )
