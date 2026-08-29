from typing import Literal

from pydantic import BaseModel


class ContentMetricsContract(BaseModel):
    contractName: Literal["ContentMetrics.v4"] = "ContentMetrics.v4"
    available: bool
    students: int = 0
    materials: int = 0
    documentPages: int = 0
    textBlocks: int = 0
    visualPendingBlocks: int = 0
    embeddedChunks: int = 0
    chunksPendingEmbedding: int = 0
    processingJobs: int = 0
    failedJobs: int = 0
    learningGoals: int = 0
    studySessions: int = 0
    pedagogicalArtifacts: int = 0
    pedagogicalJobsActive: int = 0
    pedagogicalJobsFailed: int = 0
    learningAttempts: int = 0
    agentThreads: int = 0
    agentRunsActive: int = 0
    agentRunsFailed: int = 0
    agentToolCalls: int = 0
    visualTasks: int = 0
    errorType: str | None = None
