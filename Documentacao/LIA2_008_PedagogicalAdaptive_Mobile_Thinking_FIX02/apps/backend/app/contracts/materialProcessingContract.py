from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class MaterialProcessingJobContract(BaseModel):
    contractName: Literal[
        "MaterialProcessingJob.v1"
    ] = "MaterialProcessingJob.v1"

    materialProcessingJobId: UUID
    materialId: UUID
    materialTitle: str | None = None
    studentId: UUID
    jobType: Literal["ANALYZE", "INDEX_RAG"]
    status: Literal[
        "QUEUED",
        "RUNNING",
        "COMPLETED",
        "COMPLETED_WITH_WARNINGS",
        "FAILED",
        "CANCELLED",
    ]
    stage: str
    progressPercent: int
    message: str
    requestedModelId: str | None
    effectiveVisionModelId: str | None
    effectiveEmbeddingModelId: str | None
    fallbackReason: str | None
    errorCode: str | None
    errorMessage: str | None
    createdAt: datetime
    startedAt: datetime | None
    finishedAt: datetime | None


class MaterialAsyncUploadItemContract(BaseModel):
    contractName: Literal[
        "MaterialAsyncUploadItem.v1"
    ] = "MaterialAsyncUploadItem.v1"

    fileName: str
    success: bool
    materialId: UUID | None = None
    materialTitle: str | None = None
    materialStatus: str | None = None
    job: MaterialProcessingJobContract | None = None
    errorCode: str | None = None
    errorMessage: str | None = None


class MaterialAsyncBatchUploadResultContract(BaseModel):
    contractName: Literal[
        "MaterialAsyncBatchUploadResult.v1"
    ] = "MaterialAsyncBatchUploadResult.v1"

    totalFiles: int
    successCount: int
    errorCount: int
    items: list[MaterialAsyncUploadItemContract]
