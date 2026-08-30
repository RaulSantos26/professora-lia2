from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


PedagogicalArtifactType = Literal[
    "TEACH",
    "EXPLAIN",
    "SUMMARY",
    "MIND_MAP",
    "FLASHCARDS",
    "EXERCISES",
    "QUIZ",
]


class PedagogicalArtifactCreateContract(BaseModel):
    contractName: Literal[
        "PedagogicalArtifactCreate.v1"
    ] = "PedagogicalArtifactCreate.v1"

    artifactType: PedagogicalArtifactType
    studentLearningContextId: UUID | None = None
    studentSubjectId: UUID | None = None
    studentLearningUnitId: UUID | None = None
    title: str | None = Field(default=None, max_length=250)
    instruction: str | None = Field(default=None, max_length=2000)
    materialIds: list[UUID] = Field(default_factory=list)
    difficulty: Literal[
        "AUTO",
        "EASY",
        "MEDIUM",
        "HARD",
    ] = "AUTO"
    questionCount: int = Field(default=8, ge=1, le=30)
    requestedTextModelId: str | None = None
    thinkingMode: Literal["AUTO", "ON", "OFF"] = "AUTO"


class PedagogicalEvidenceContract(BaseModel):
    evidenceId: UUID | None
    materialId: UUID
    materialTitle: str
    locator: str
    excerpt: str


class PedagogicalArtifactContract(BaseModel):
    contractName: Literal[
        "PedagogicalArtifact.v1"
    ] = "PedagogicalArtifact.v1"

    pedagogicalArtifactId: UUID
    studentId: UUID
    studentLearningContextId: UUID | None
    studentSubjectId: UUID | None
    studentLearningUnitId: UUID | None
    artifactType: PedagogicalArtifactType
    status: Literal[
        "QUEUED",
        "RUNNING",
        "READY",
        "FAILED",
        "ARCHIVED",
    ]
    progressPercent: int
    message: str
    title: str
    instruction: str | None
    difficulty: str | None
    questionCount: int | None
    requestedTextModelId: str | None
    effectiveTextModelId: str | None
    thinkingMode: Literal["AUTO", "ON", "OFF"]
    effectiveThinkingEnabled: bool | None
    sourceMaterialIds: list[UUID]
    sourceEvidence: list[PedagogicalEvidenceContract]
    content: dict | None
    errorCode: str | None
    errorMessage: str | None
    createdAt: datetime
    startedAt: datetime | None
    finishedAt: datetime | None


class LearningAttemptSubmitContract(BaseModel):
    contractName: Literal[
        "LearningAttemptSubmit.v1"
    ] = "LearningAttemptSubmit.v1"

    answers: dict[str, str]


class LearningQuestionResultContract(BaseModel):
    questionId: str
    correct: bool
    submittedAnswer: str
    correctAnswer: str
    explanation: str


class LearningAttemptContract(BaseModel):
    contractName: Literal[
        "LearningAttempt.v1"
    ] = "LearningAttempt.v1"

    learningAttemptId: UUID
    studentId: UUID
    pedagogicalArtifactId: UUID
    attemptType: Literal["EXERCISES", "QUIZ"]
    scorePercent: int
    correctCount: int
    totalCount: int
    results: list[LearningQuestionResultContract]
    adaptiveMessage: str
    updatedUnitIds: list[UUID]
    createdAt: datetime
    completedAt: datetime
