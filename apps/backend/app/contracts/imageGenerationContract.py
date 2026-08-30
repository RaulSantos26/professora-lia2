from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


ImageMode = Literal["ILLUSTRATION", "MIND_MAP_COMPANION"]
ImageStatus = Literal["QUEUED", "PREPARING", "GENERATING", "LABELING", "READY", "ERROR", "CANCELLED"]


class ImageGenerationTaskContract(BaseModel):
    contractName: Literal["ImageGenerationTask.v1"] = "ImageGenerationTask.v1"
    imageTaskId: UUID
    studentId: UUID
    agentThreadId: UUID | None
    agentRunId: UUID | None
    relatedVisualTaskId: UUID | None
    relatedPedagogicalArtifactId: UUID | None
    imageMode: ImageMode
    status: ImageStatus
    progressPercent: int
    message: str
    title: str
    labels: list[str]
    assetUrl: str | None
    sourceMaterialIds: list[UUID]
    seed: int | None
    elapsedSeconds: float | None
    errorCode: str | None
    errorMessage: str | None
    createdAt: datetime
    finishedAt: datetime | None
