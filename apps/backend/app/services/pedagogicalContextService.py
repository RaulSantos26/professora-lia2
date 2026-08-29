import math
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.common.domainError import DomainError
from app.repositories.materialRepository import MaterialRepository
from app.repositories.ragRepository import RagCandidate, RagRepository
from app.services.ollamaClientService import OllamaClientService


class PedagogicalContextService:
    MAX_EVIDENCE = 24
    MAX_CONTEXT_CHARS = 28000

    def __init__(self, session: Session):
        self.materialRepository = MaterialRepository(session)
        self.ragRepository = RagRepository(session)
        self.ollama = OllamaClientService()

    def build(
        self,
        *,
        studentId: UUID,
        materialIds: list[UUID],
        focusQuery: str | None = None,
    ) -> tuple[str, list[dict], list[UUID]]:
        materials = self.materialRepository.listByStudentId(studentId)

        selected = (
            [item for item in materials if item.materialId in materialIds]
            if materialIds
            else [item for item in materials if item.studyEnabled]
        )

        if materialIds and len(selected) != len(set(materialIds)):
            raise DomainError(
                code="PEDAGOGICAL_MATERIAL_NOT_OWNED",
                message="Um dos materiais não pertence ao aluno.",
                httpStatus=409,
            )

        selected = [item for item in selected if item.studyEnabled]

        if not selected:
            raise DomainError(
                code="PEDAGOGICAL_MATERIAL_EMPTY",
                message="Selecione ao menos um material habilitado para estudo.",
                httpStatus=422,
            )

        selectedIds = [item.materialId for item in selected]

        candidates = self.ragRepository.listCandidates(
            studentId=studentId,
            studentLearningContextId=None,
            studentSubjectId=None,
            studentLearningUnitId=None,
            materialIds=selectedIds,
        )

        if not candidates:
            raise DomainError(
                code="RAG_INDEX_EMPTY",
                message=(
                    "Os materiais selecionados ainda não possuem "
                    "trechos indexados."
                ),
                httpStatus=409,
            )

        if focusQuery and focusQuery.strip():
            candidates = self._semanticOrder(
                candidates,
                focusQuery.strip(),
            )
        else:
            candidates = sorted(
                candidates,
                key=lambda item: (
                    str(item.sourceGroupId or item.materialId),
                    item.sourceSequence or 0,
                    item.materialTitle.lower(),
                    item.locator.lower(),
                    str(item.documentChunkId),
                ),
            )

        evidence = []
        pieces = []
        totalChars = 0

        for index, candidate in enumerate(
            candidates[: self.MAX_EVIDENCE],
            start=1,
        ):
            excerpt = candidate.content[:2200]
            piece = (
                f"[{index}] Material: {candidate.materialTitle}\n"
                f"Local: {candidate.locator}\n"
                f"Trecho: {excerpt}"
            )

            if totalChars + len(piece) > self.MAX_CONTEXT_CHARS:
                break

            totalChars += len(piece)
            pieces.append(piece)
            evidence.append(
                {
                    "evidenceId": (
                        str(candidate.evidenceId)
                        if candidate.evidenceId
                        else None
                    ),
                    "materialId": str(candidate.materialId),
                    "materialTitle": candidate.materialTitle,
                    "locator": candidate.locator,
                    "excerpt": excerpt,
                }
            )

        return "\n\n".join(pieces), evidence, selectedIds

    def _semanticOrder(
        self,
        candidates: list[RagCandidate],
        query: str,
    ) -> list[RagCandidate]:
        groups: dict[str, list[RagCandidate]] = {}

        for candidate in candidates:
            groups.setdefault(
                candidate.embeddingModelId,
                [],
            ).append(candidate)

        modelId, compatible = max(
            groups.items(),
            key=lambda item: len(item[1]),
        )

        queryVector = self.ollama.embed(
            modelId=modelId,
            inputs=[query],
        )[0]

        ranked = []

        for candidate in compatible:
            if len(candidate.embedding) != len(queryVector):
                continue

            ranked.append(
                (
                    self._cosine(
                        queryVector,
                        candidate.embedding,
                    ),
                    candidate,
                )
            )

        ranked.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            candidate
            for _, candidate in ranked
        ]

    def _cosine(
        self,
        left: list[float],
        right: list[float],
    ) -> float:
        if len(left) != len(right) or not left:
            return -1.0

        dot = sum(
            a * b
            for a, b in zip(left, right)
        )
        leftNorm = math.sqrt(
            sum(value * value for value in left)
        )
        rightNorm = math.sqrt(
            sum(value * value for value in right)
        )

        if leftNorm == 0 or rightNorm == 0:
            return -1.0

        return dot / (leftNorm * rightNorm)
