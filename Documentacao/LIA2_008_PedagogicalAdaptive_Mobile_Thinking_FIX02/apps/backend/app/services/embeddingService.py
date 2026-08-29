from datetime import datetime, timezone

from app.contracts.capabilityRoutingContract import (
    CapabilityRoutingDecisionContract,
)
from app.persistence.models.documentChunkModel import DocumentChunkModel
from app.services.capabilityRouterService import CapabilityRouterService
from app.services.ollamaClientService import OllamaClientService


class EmbeddingService:
    BATCH_SIZE = 16

    def __init__(self):
        self.router = CapabilityRouterService()
        self.ollama = OllamaClientService()

    def embedChunks(
        self,
        chunks: list[DocumentChunkModel],
        requestedModelId: str | None = None,
        allowFallback: bool = True,
    ) -> tuple[
        CapabilityRoutingDecisionContract,
        int,
    ]:
        pending = [
            chunk
            for chunk in chunks
            if chunk.content.strip()
        ]

        decision = self.router.route(
            "EMBEDDINGS",
            requestedModelId,
            allowFallback=allowFallback,
        )
        embedded = 0

        for offset in range(0, len(pending), self.BATCH_SIZE):
            batch = pending[offset:offset + self.BATCH_SIZE]

            vectors = self.ollama.embed(
                modelId=decision.effectiveModelId,
                inputs=[chunk.content for chunk in batch],
            )

            for chunk, vector in zip(batch, vectors):
                chunk.embedding = vector
                chunk.embeddingModelId = decision.effectiveModelId
                chunk.embeddedAt = datetime.now(timezone.utc)
                chunk.status = "EMBEDDED"
                embedded += 1

        return decision, embedded
