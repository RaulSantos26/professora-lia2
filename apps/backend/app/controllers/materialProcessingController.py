from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.contracts.materialProcessingContract import (
    MaterialAsyncBatchUploadResultContract,
    MaterialProcessingJobContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.materialAsyncService import MaterialAsyncService


router = APIRouter(tags=["material-processing"])


@router.post(
    "/students/{studentId}/materials/upload-batch-async",
    response_model=MaterialAsyncBatchUploadResultContract,
)
async def uploadMaterialBatchAsync(
    studentId: UUID,
    title: str | None = Form(default=None),
    description: str | None = Form(default=None),
    studentLearningContextId: UUID | None = Form(default=None),
    studentSubjectId: UUID | None = Form(default=None),
    studentLearningUnitId: UUID | None = Form(default=None),
    analysisRequested: bool = Form(default=True),
    studyEnabled: bool = Form(default=True),
    requestedModelId: str | None = Form(default=None),
    aiMode: str = Form(default="AUTO"),
    fixedModelId: str | None = Form(default=None),
    textModelId: str | None = Form(default=None),
    visionModelId: str | None = Form(default=None),
    embeddingModelId: str | None = Form(default=None),
    thinkingMode: str = Form(default="AUTO"),
    files: list[UploadFile] = File(...),
    session: Session = Depends(getDatabaseSession),
) -> MaterialAsyncBatchUploadResultContract:
    return await MaterialAsyncService(session).uploadBatch(
        studentId=studentId,
        title=title,
        description=description,
        studentLearningContextId=studentLearningContextId,
        studentSubjectId=studentSubjectId,
        studentLearningUnitId=studentLearningUnitId,
        analysisRequested=analysisRequested,
        studyEnabled=studyEnabled,
        requestedModelId=requestedModelId,
        aiMode=aiMode,
        fixedModelId=fixedModelId,
        textModelId=textModelId,
        visionModelId=visionModelId,
        embeddingModelId=embeddingModelId,
        thinkingMode=thinkingMode,
        files=files,
    )


@router.post(
    "/students/{studentId}/materials/{materialId}/analyze-async",
    response_model=MaterialProcessingJobContract,
)
def analyzeMaterialAsync(
    studentId: UUID,
    materialId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> MaterialProcessingJobContract:
    return MaterialAsyncService(session).queueAnalyze(
        studentId=studentId,
        materialId=materialId,
    )


@router.post(
    "/students/{studentId}/materials/{materialId}/index-rag",
    response_model=MaterialProcessingJobContract,
)
def indexMaterialRag(
    studentId: UUID,
    materialId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> MaterialProcessingJobContract:
    return MaterialAsyncService(session).queueIndex(
        studentId=studentId,
        materialId=materialId,
    )


@router.get(
    "/material-processing-jobs/{jobId}",
    response_model=MaterialProcessingJobContract,
)
def getMaterialProcessingJob(
    jobId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> MaterialProcessingJobContract:
    return MaterialAsyncService(session).getJob(jobId)


@router.get(
    "/students/{studentId}/material-processing-jobs",
    response_model=list[MaterialProcessingJobContract],
)
def listMaterialProcessingJobs(
    studentId: UUID,
    activeOnly: bool = Query(default=False),
    session: Session = Depends(getDatabaseSession),
) -> list[MaterialProcessingJobContract]:
    return MaterialAsyncService(session).listJobs(
        studentId=studentId,
        activeOnly=activeOnly,
    )
