from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RagQueryRequestContract(BaseModel):
    contractName: Literal["RagQueryRequest.v1"] = "RagQueryRequest.v1"
    query: str
    topK: int = Field(default=6, ge=1, le=12)
    requestedModelId: str | None = None
    thinkingMode: Literal["AUTO", "ON", "OFF"] = "AUTO"
    studentLearningContextId: UUID | None = None
    studentSubjectId: UUID | None = None
    studentLearningUnitId: UUID | None = None
    materialIds: list[UUID] = Field(default_factory=list)


class RagEvidenceHitContract(BaseModel):
    contractName: Literal["RagEvidenceHit.v1"] = "RagEvidenceHit.v1"
    evidenceId: UUID | None
    materialId: UUID
    materialTitle: str
    locator: str
    excerpt: str
    score: float


class RagQueryResponseContract(BaseModel):
    contractName: Literal[
        "RagQueryResponse.v1"
    ] = "RagQueryResponse.v1"

    answer: str
    citations: list[int]
    textModelId: str
    embeddingModelId: str
    thinkingMode: Literal["AUTO", "ON", "OFF"]
    thinkingEnabled: bool
    evidence: list[RagEvidenceHitContract]
