import math
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.common.domainError import DomainError
from app.repositories.ragRepository import RagCandidate, RagRepository
from app.services.contentGuardService import ContentGuardService
from app.services.evidenceCurationService import EvidenceCurationService
from app.services.ollamaClientService import OllamaClientService


class EvidenceSearchTool:
    toolName = "EVIDENCE_SEARCH"

    def __init__(self, session: Session):
        self.repository = RagRepository(session)
        self.contentGuard = ContentGuardService()
        self.evidenceCuration = EvidenceCurationService()
        self.ollama = OllamaClientService()

    def execute(
        self,
        *,
        studentId: UUID,
        query: str,
        studentLearningContextId: UUID | None,
        studentSubjectId: UUID | None,
        studentLearningUnitId: UUID | None,
        materialIds: list[UUID],
        topK: int = 8,
    ) -> dict:
        candidates = self.repository.listCandidates(
            studentId=studentId,
            studentLearningContextId=studentLearningContextId,
            studentSubjectId=studentSubjectId,
            studentLearningUnitId=studentLearningUnitId,
            materialIds=materialIds,
        )

        candidates = self.evidenceCuration.curateCandidates(candidates)

        if not candidates:
            raise DomainError(
                code="AGENT_EVIDENCE_EMPTY",
                message=(
                    "A Lia ainda não encontrou evidências indexadas "
                    "para este conteúdo."
                ),
                httpStatus=409,
            )

        groups: dict[str, list[RagCandidate]] = {}

        for candidate in candidates:
            groups.setdefault(
                candidate.embeddingModelId,
                [],
            ).append(candidate)

        embeddingModelId, compatible = max(
            groups.items(),
            key=lambda item: len(item[1]),
        )

        queryVector = self.ollama.embed(
            modelId=embeddingModelId,
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

        hits = []

        for index, (score, candidate) in enumerate(
            ranked[:topK],
            start=1,
        ):
            hits.append(
                {
                    "index": index,
                    "score": round(score, 6),
                    "evidenceId": (
                        str(candidate.evidenceId)
                        if candidate.evidenceId
                        else None
                    ),
                    "materialId": str(
                        candidate.materialId
                    ),
                    "materialTitle": (
                        candidate.materialTitle
                    ),
                    "locator": candidate.locator,
                    "excerpt": self.evidenceCuration.cleanText(candidate.content)[:2400],
                }
            )

        if not hits:
            raise DomainError(
                code="AGENT_EVIDENCE_EMPTY",
                message=(
                    "Os trechos indexados não são compatíveis "
                    "com o modelo de embeddings atual."
                ),
                httpStatus=409,
            )

        context = "\n\n".join(
            (
                f"[{hit['index']}] "
                f"{hit['materialTitle']} · {hit['locator']}\n"
                f"{self.contentGuard.protect(hit['excerpt']).content}"
            )
            for hit in hits
        )

        return {
            "embeddingModelId": embeddingModelId,
            "hits": hits,
            "context": context,
        }

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
