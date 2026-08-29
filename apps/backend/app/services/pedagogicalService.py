import re
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.contracts.pedagogicalContract import (
    LearningAttemptContract,
    LearningAttemptSubmitContract,
    LearningQuestionResultContract,
    PedagogicalArtifactContract,
    PedagogicalArtifactCreateContract,
    PedagogicalEvidenceContract,
)
from app.domain.common.domainError import DomainError
from app.persistence.models.learningAttemptModel import LearningAttemptModel
from app.persistence.models.pedagogicalArtifactModel import PedagogicalArtifactModel
from app.repositories.learningAttemptRepository import LearningAttemptRepository
from app.repositories.materialRepository import MaterialRepository
from app.repositories.pedagogicalArtifactRepository import PedagogicalArtifactRepository
from app.repositories.studentRepository import StudentRepository
from app.services.adaptiveLearningService import AdaptiveLearningService
from app.services.aiExecutionPreferenceService import AiExecutionPreferenceService
from app.services.aiModelRegistryService import AiModelRegistryService
from app.services.capabilityRouterService import CapabilityRouterService
from app.services.pedagogicalContextService import PedagogicalContextService
from app.services.pedagogicalGenerationService import PedagogicalGenerationService
from app.services.thinkingPolicyService import ThinkingPolicyService


class PedagogicalService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = PedagogicalArtifactRepository(session)
        self.attemptRepository = LearningAttemptRepository(session)
        self.studentRepository = StudentRepository(session)
        self.materialRepository = MaterialRepository(session)
        self.contextService = PedagogicalContextService(session)
        self.generator = PedagogicalGenerationService()
        self.adaptive = AdaptiveLearningService(session)
        self.router = CapabilityRouterService()
        self.aiPreference = AiExecutionPreferenceService()
        self.modelRegistry = AiModelRegistryService()
        self.thinking = ThinkingPolicyService()

    def createArtifact(
        self,
        *,
        studentId: UUID,
        request: PedagogicalArtifactCreateContract,
    ) -> PedagogicalArtifactContract:
        self._requireStudent(studentId)
        self.modelRegistry.validateModel(request.requestedTextModelId)

        if request.requestedTextModelId:
            self.router.route(
                "TEXT",
                request.requestedTextModelId,
                allowFallback=False,
                additionalCapabilities=(
                    self.thinking.additionalCapabilities(
                        request.thinkingMode
                    )
                ),
            )

        materials = self.materialRepository.listByStudentId(studentId)

        if request.materialIds:
            owned = {
                material.materialId
                for material in materials
                if material.studyEnabled
            }
            missing = [
                materialId
                for materialId in request.materialIds
                if materialId not in owned
            ]

            if missing:
                raise DomainError(
                    code="PEDAGOGICAL_MATERIAL_NOT_OWNED",
                    message=(
                        "Um material selecionado não pertence ao aluno "
                        "ou está fora do estudo."
                    ),
                    httpStatus=409,
                )

        artifact = PedagogicalArtifactModel(
            studentId=studentId,
            artifactType=request.artifactType,
            status="QUEUED",
            progressPercent=5,
            message="Na fila para geração.",
            title=(
                request.title.strip()
                if request.title and request.title.strip()
                else self._defaultTitle(request.artifactType)
            ),
            instruction=(
                request.instruction.strip()
                if request.instruction and request.instruction.strip()
                else None
            ),
            difficulty=request.difficulty,
            questionCount=(
                request.questionCount
                if request.artifactType in {"EXERCISES", "QUIZ"}
                else None
            ),
            requestedTextModelId=request.requestedTextModelId,
            thinkingMode=request.thinkingMode,
            effectiveThinkingEnabled=None,
            sourceMaterialIds=[
                str(value)
                for value in request.materialIds
            ],
            sourceEvidenceJson=[],
            contentJson=None,
        )

        self.repository.create(artifact)
        self.session.commit()
        self.session.refresh(artifact)

        return self._toContract(artifact)

    def listArtifacts(
        self,
        studentId: UUID,
    ) -> list[PedagogicalArtifactContract]:
        self._requireStudent(studentId)

        return [
            self._toContract(model)
            for model in self.repository.listByStudent(studentId)
        ]

    def getArtifact(
        self,
        *,
        studentId: UUID,
        artifactId: UUID,
    ) -> PedagogicalArtifactContract:
        model = self._ownedArtifact(studentId, artifactId)
        return self._toContract(model)

    def archiveArtifact(
        self,
        *,
        studentId: UUID,
        artifactId: UUID,
    ) -> None:
        model = self._ownedArtifact(studentId, artifactId)

        if model.status == "RUNNING":
            raise DomainError(
                code="PEDAGOGICAL_ARTIFACT_RUNNING",
                message="Aguarde a geração terminar antes de remover.",
                httpStatus=409,
            )

        self.repository.archive(model)
        self.session.commit()

    def process(
        self,
        artifact: PedagogicalArtifactModel,
    ) -> None:
        artifact.progressPercent = 25
        artifact.message = "Selecionando evidências."
        self.session.commit()

        materialIds = [
            UUID(value)
            for value in (artifact.sourceMaterialIds or [])
        ]

        context, evidence, selectedIds = self.contextService.build(
            studentId=artifact.studentId,
            materialIds=materialIds,
            focusQuery=artifact.instruction,
        )

        artifact.sourceMaterialIds = [
            str(value)
            for value in selectedIds
        ]
        artifact.sourceEvidenceJson = evidence
        artifact.progressPercent = 45
        artifact.message = "Preparando atividade pedagógica."
        self.session.commit()

        difficulty = self.adaptive.resolveDifficulty(
            studentId=artifact.studentId,
            materialIds=selectedIds,
            requestedDifficulty=artifact.difficulty or "AUTO",
        )

        modelId, allowFallback = self._resolveTextModel(
            artifact,
            selectedIds,
        )
        thinkingMode = self._resolveThinkingMode(
            artifact,
            selectedIds,
        )
        decision = self.router.route(
            "TEXT",
            modelId,
            allowFallback=allowFallback,
            additionalCapabilities=(
                self.thinking.additionalCapabilities(
                    thinkingMode
                )
            ),
        )
        thinkingEnabled = self.thinking.resolve(
            modelId=decision.effectiveModelId,
            thinkingMode=thinkingMode,
        )

        artifact.effectiveTextModelId = decision.effectiveModelId
        artifact.effectiveThinkingEnabled = thinkingEnabled
        artifact.progressPercent = 65
        artifact.message = "A Lia está preparando o conteúdo."
        self.session.commit()

        content = self.generator.generate(
            artifactType=artifact.artifactType,
            context=context,
            instruction=artifact.instruction,
            difficulty=difficulty,
            questionCount=artifact.questionCount or 8,
            modelId=decision.effectiveModelId,
            thinkingEnabled=thinkingEnabled,
        )

        content["resolvedDifficulty"] = difficulty

        self.repository.complete(
            artifact,
            content=content,
            effectiveTextModelId=decision.effectiveModelId,
            sourceEvidence=evidence,
        )
        self.session.commit()

    def submitAttempt(
        self,
        *,
        studentId: UUID,
        artifactId: UUID,
        request: LearningAttemptSubmitContract,
    ) -> LearningAttemptContract:
        artifact = self._ownedArtifact(studentId, artifactId)

        if artifact.status != "READY":
            raise DomainError(
                code="PEDAGOGICAL_ARTIFACT_NOT_READY",
                message="A atividade ainda não está pronta.",
                httpStatus=409,
            )

        if artifact.artifactType not in {"EXERCISES", "QUIZ"}:
            raise DomainError(
                code="PEDAGOGICAL_ARTIFACT_NOT_ASSESSABLE",
                message="Este tipo de conteúdo não aceita respostas.",
                httpStatus=409,
            )

        content = artifact.contentJson or {}
        questions = content.get("questions") or []

        if not questions:
            raise DomainError(
                code="PEDAGOGICAL_QUESTIONS_EMPTY",
                message="A atividade não possui questões válidas.",
                httpStatus=409,
            )

        results = []
        correctCount = 0

        for question in questions:
            questionId = str(question.get("questionId") or "")
            submitted = str(request.answers.get(questionId) or "").strip()
            correctAnswer = str(
                question.get("correctAnswer") or ""
            ).strip()

            correct = (
                self._normalize(submitted)
                == self._normalize(correctAnswer)
            )

            if correct:
                correctCount += 1

            results.append(
                LearningQuestionResultContract(
                    questionId=questionId,
                    correct=correct,
                    submittedAnswer=submitted,
                    correctAnswer=correctAnswer,
                    explanation=str(
                        question.get("explanation") or ""
                    ),
                )
            )

        total = len(questions)
        score = round((correctCount / total) * 100)

        materialIds = [
            UUID(value)
            for value in (artifact.sourceMaterialIds or [])
        ]

        updatedUnitIds, adaptiveMessage = (
            self.adaptive.applyAttempt(
                studentId=studentId,
                materialIds=materialIds,
                scorePercent=score,
            )
        )

        attempt = LearningAttemptModel(
            studentId=studentId,
            pedagogicalArtifactId=artifact.pedagogicalArtifactId,
            attemptType=artifact.artifactType,
            scorePercent=score,
            correctCount=correctCount,
            totalCount=total,
            submittedAnswers=request.answers,
            resultJson={
                "results": [
                    result.model_dump(mode="json")
                    for result in results
                ],
                "adaptiveMessage": adaptiveMessage,
                "updatedUnitIds": [
                    str(value)
                    for value in updatedUnitIds
                ],
            },
        )
        self.attemptRepository.create(attempt)
        self.session.commit()
        self.session.refresh(attempt)

        return LearningAttemptContract(
            learningAttemptId=attempt.learningAttemptId,
            studentId=attempt.studentId,
            pedagogicalArtifactId=attempt.pedagogicalArtifactId,
            attemptType=attempt.attemptType,
            scorePercent=attempt.scorePercent,
            correctCount=attempt.correctCount,
            totalCount=attempt.totalCount,
            results=results,
            adaptiveMessage=adaptiveMessage,
            updatedUnitIds=updatedUnitIds,
            createdAt=attempt.createdAt,
            completedAt=attempt.completedAt,
        )

    def _resolveTextModel(
        self,
        artifact: PedagogicalArtifactModel,
        materialIds: list[UUID],
    ) -> tuple[str | None, bool]:
        if artifact.requestedTextModelId:
            return artifact.requestedTextModelId, False

        if len(materialIds) == 1:
            material = self.materialRepository.findById(materialIds[0])

            if material is not None:
                return self.aiPreference.requestedModelFor(
                    material,
                    "TEXT",
                )

        return None, True

    def _resolveThinkingMode(
        self,
        artifact: PedagogicalArtifactModel,
        materialIds: list[UUID],
    ) -> str:
        if artifact.thinkingMode != "AUTO":
            return artifact.thinkingMode

        if len(materialIds) == 1:
            material = self.materialRepository.findById(
                materialIds[0]
            )

            if (
                material is not None
                and material.thinkingMode != "AUTO"
            ):
                return material.thinkingMode

        return "AUTO"

    def _toContract(
        self,
        model: PedagogicalArtifactModel,
    ) -> PedagogicalArtifactContract:
        content = self._publicContent(
            model.artifactType,
            model.contentJson,
        )

        evidence = [
            PedagogicalEvidenceContract.model_validate(item)
            for item in (model.sourceEvidenceJson or [])
        ]

        return PedagogicalArtifactContract(
            pedagogicalArtifactId=model.pedagogicalArtifactId,
            studentId=model.studentId,
            artifactType=model.artifactType,
            status=model.status,
            progressPercent=model.progressPercent,
            message=model.message,
            title=model.title,
            instruction=model.instruction,
            difficulty=model.difficulty,
            questionCount=model.questionCount,
            requestedTextModelId=model.requestedTextModelId,
            effectiveTextModelId=model.effectiveTextModelId,
            thinkingMode=model.thinkingMode,
            effectiveThinkingEnabled=model.effectiveThinkingEnabled,
            sourceMaterialIds=[
                UUID(value)
                for value in (model.sourceMaterialIds or [])
            ],
            sourceEvidence=evidence,
            content=content,
            errorCode=model.errorCode,
            errorMessage=model.errorMessage,
            createdAt=model.createdAt,
            startedAt=model.startedAt,
            finishedAt=model.finishedAt,
        )

    def _publicContent(
        self,
        artifactType: str,
        content: dict | None,
    ) -> dict | None:
        if content is None:
            return None

        if artifactType not in {"EXERCISES", "QUIZ"}:
            return content

        public = dict(content)
        publicQuestions = []

        for question in content.get("questions", []):
            publicQuestions.append(
                {
                    key: value
                    for key, value in question.items()
                    if key not in {
                        "correctAnswer",
                        "explanation",
                    }
                }
            )

        public["questions"] = publicQuestions
        return public

    def _ownedArtifact(
        self,
        studentId: UUID,
        artifactId: UUID,
    ) -> PedagogicalArtifactModel:
        model = self.repository.findById(artifactId)

        if model is None or model.studentId != studentId:
            raise DomainError(
                code="PEDAGOGICAL_ARTIFACT_NOT_FOUND",
                message="Conteúdo pedagógico não encontrado.",
                httpStatus=404,
            )

        return model

    def _requireStudent(self, studentId: UUID) -> None:
        if self.studentRepository.findById(studentId) is None:
            raise DomainError(
                code="STUDENT_NOT_FOUND",
                message="Aluno não encontrado.",
                httpStatus=404,
            )

    def _normalize(self, value: str) -> str:
        return re.sub(
            r"\s+",
            " ",
            value.strip().casefold(),
        )

    def _defaultTitle(self, artifactType: str) -> str:
        return {
            "TEACH": "Aula da Lia",
            "EXPLAIN": "Explicação da Lia",
            "SUMMARY": "Resumo",
            "MIND_MAP": "Mapa mental",
            "FLASHCARDS": "Flashcards",
            "EXERCISES": "Exercícios",
            "QUIZ": "Quiz",
        }[artifactType]
