from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AgentThreadCreateContract(BaseModel):
    contractName: Literal[
        "AgentThreadCreate.v1"
    ] = "AgentThreadCreate.v1"

    title: str | None = Field(default=None, max_length=250)
    studentLearningContextId: UUID | None = None
    studentSubjectId: UUID | None = None
    studentLearningUnitId: UUID | None = None


class AgentThreadContract(BaseModel):
    contractName: Literal[
        "AgentThread.v1"
    ] = "AgentThread.v1"

    agentThreadId: UUID
    studentId: UUID
    studentLearningContextId: UUID | None
    studentSubjectId: UUID | None
    studentLearningUnitId: UUID | None
    title: str
    status: Literal["ACTIVE", "ARCHIVED"]
    memory: dict
    createdAt: datetime
    updatedAt: datetime
    lastMessageAt: datetime | None


class AgentMessageContract(BaseModel):
    contractName: Literal[
        "AgentMessage.v1"
    ] = "AgentMessage.v1"

    agentMessageId: UUID
    agentThreadId: UUID
    role: Literal["USER", "ASSISTANT"]
    content: str
    citations: list[dict]
    visualTaskIds: list[UUID]
    imageTaskIds: list[UUID] = Field(default_factory=list)
    actions: list[dict]
    createdAt: datetime


class AgentMessageCreateContract(BaseModel):
    contractName: Literal[
        "AgentMessageCreate.v1"
    ] = "AgentMessageCreate.v1"

    content: str = Field(min_length=1, max_length=8000)
    requestedTextModelId: str | None = None
    thinkingMode: Literal["AUTO", "ON", "OFF"] = "AUTO"
    materialIds: list[UUID] = Field(default_factory=list)


class AgentRunContract(BaseModel):
    contractName: Literal[
        "AgentRun.v1"
    ] = "AgentRun.v1"

    agentRunId: UUID
    agentThreadId: UUID
    userMessageId: UUID
    assistantMessageId: UUID | None
    status: Literal[
        "QUEUED",
        "RUNNING",
        "READY",
        "FAILED",
        "CANCELLED",
    ]
    stage: str
    progressPercent: int
    message: str
    requestedTextModelId: str | None
    effectiveTextModelId: str | None
    thinkingMode: Literal["AUTO", "ON", "OFF"]
    effectiveThinkingEnabled: bool | None
    plan: dict | None
    errorCode: str | None
    errorMessage: str | None
    createdAt: datetime
    startedAt: datetime | None
    finishedAt: datetime | None


class AgentConversationContract(BaseModel):
    contractName: Literal[
        "AgentConversation.v1"
    ] = "AgentConversation.v1"

    thread: AgentThreadContract
    messages: list[AgentMessageContract]
    activeRun: AgentRunContract | None
    lastRun: AgentRunContract | None
