from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class DocumentBlockViewContract(BaseModel):
    contractName: Literal["DocumentBlockView.v1"] = "DocumentBlockView.v1"
    documentBlockId: UUID
    sequenceNumber: int
    blockType: str
    textContent: str | None
    processingStatus: str
    orientationDegrees: int | None = None
    visionModelId: str | None = None
    visionThinkingEnabled: bool | None = None


class DocumentPageViewContract(BaseModel):
    contractName: Literal["DocumentPageView.v1"] = "DocumentPageView.v1"
    documentPageId: UUID
    pageNumber: int
    nativeText: str | None
    status: str
    blocks: list[DocumentBlockViewContract]


class DocumentStructureContract(BaseModel):
    contractName: Literal["DocumentStructure.v2"] = "DocumentStructure.v2"
    documentId: UUID
    documentVersionId: UUID
    extractionStatus: str
    pageCount: int
    pages: list[DocumentPageViewContract]
    evidenceCount: int
    chunkCount: int
    embeddedChunkCount: int
    visualPendingCount: int
