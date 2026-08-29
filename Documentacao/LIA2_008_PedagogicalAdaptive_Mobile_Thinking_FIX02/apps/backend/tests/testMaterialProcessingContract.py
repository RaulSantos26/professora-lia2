from datetime import datetime, timezone
from uuid import uuid4

from app.contracts.materialProcessingContract import (
    MaterialProcessingJobContract,
)


def testProcessingJobCarriesProgressAndModels():
    job = MaterialProcessingJobContract(
        materialProcessingJobId=uuid4(),
        materialId=uuid4(),
        materialTitle="Apostila",
        studentId=uuid4(),
        jobType="ANALYZE",
        status="RUNNING",
        stage="VISION",
        progressPercent=55,
        message="Analisando imagem.",
        requestedModelId=None,
        effectiveVisionModelId="vision:model",
        effectiveEmbeddingModelId=None,
        fallbackReason=None,
        errorCode=None,
        errorMessage=None,
        createdAt=datetime.now(timezone.utc),
        startedAt=datetime.now(timezone.utc),
        finishedAt=None,
    )

    assert job.progressPercent == 55
    assert job.stage == "VISION"
    assert job.effectiveVisionModelId == "vision:model"
