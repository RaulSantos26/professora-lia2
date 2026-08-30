from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


VisualTaskType = Literal[
    "MIND_MAP",
    "DIAGRAM",
    "CHART",
    "ANIMATION_2D",
    "SCENE_3D",
]


class VisualTaskCreateContract(BaseModel):
    contractName: Literal[
        "VisualTaskCreate.v1"
    ] = "VisualTaskCreate.v1"

    visualType: VisualTaskType
    studentLearningContextId: UUID
    studentSubjectId: UUID
    studentLearningUnitId: UUID
    title: str | None = Field(default=None, max_length=250)
    instruction: str | None = Field(default=None, max_length=2000)
    materialIds: list[UUID] = Field(default_factory=list)
    requestedTextModelId: str | None = None
    thinkingMode: Literal["AUTO", "ON", "OFF"] = "AUTO"
    pedagogicalArtifactId: UUID | None = None


class VisualTaskContract(BaseModel):
    contractName: Literal[
        "VisualTask.v1"
    ] = "VisualTask.v1"

    visualTaskId: UUID
    studentId: UUID
    agentThreadId: UUID | None
    agentRunId: UUID | None
    pedagogicalArtifactId: UUID | None
    visualType: VisualTaskType
    status: Literal["READY", "ARCHIVED"]
    title: str
    renderer: Literal["SVG", "CANVAS", "THREE"]
    spec: dict
    evidence: list[dict]
    sourceMaterialIds: list[UUID]
    effectiveModelId: str | None
    thinkingEnabled: bool | None
    createdAt: datetime
