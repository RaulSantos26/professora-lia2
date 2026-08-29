from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.contracts.documentStructureContract import DocumentStructureContract
from app.contracts.aiExecutionPreferenceContract import MaterialAiPreferenceUpdateContract
from app.contracts.materialContract import (
    MaterialBatchUploadResultContract,
    MaterialContract,
    MaterialModelPreferenceUpdateContract,
    MaterialStudyUsageUpdateContract,
    MaterialUploadResultContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.materialService import MaterialService


router = APIRouter(tags=["materials"])


@router.get(
    "/students/{studentId}/materials",
    response_model=list[MaterialContract],
)
def listMaterials(
    studentId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> list[MaterialContract]:
    return MaterialService(session).listMaterials(studentId)


@router.post(
    "/students/{studentId}/materials/upload",
    response_model=MaterialUploadResultContract,
    status_code=status.HTTP_201_CREATED,
)
async def uploadMaterial(
    studentId: UUID,
    title: str = Form(...),
    description: str | None = Form(default=None),
    studentLearningContextId: UUID | None = Form(default=None),
    studentSubjectId: UUID | None = Form(default=None),
    studentLearningUnitId: UUID | None = Form(default=None),
    analysisRequested: bool = Form(default=True),
    studyEnabled: bool = Form(default=True),
    requestedModelId: str | None = Form(default=None),
    file: UploadFile = File(...),
    session: Session = Depends(getDatabaseSession),
) -> MaterialUploadResultContract:
    return await MaterialService(session).upload(
        studentId=studentId,
        title=title,
        description=description,
        studentLearningContextId=studentLearningContextId,
        studentSubjectId=studentSubjectId,
        studentLearningUnitId=studentLearningUnitId,
        analysisRequested=analysisRequested,
        studyEnabled=studyEnabled,
        requestedModelId=requestedModelId,
        upload=file,
    )


@router.post(
    "/students/{studentId}/materials/upload-batch",
    response_model=MaterialBatchUploadResultContract,
)
async def uploadMaterialBatch(
    studentId: UUID,
    title: str | None = Form(default=None),
    description: str | None = Form(default=None),
    studentLearningContextId: UUID | None = Form(default=None),
    studentSubjectId: UUID | None = Form(default=None),
    studentLearningUnitId: UUID | None = Form(default=None),
    analysisRequested: bool = Form(default=True),
    studyEnabled: bool = Form(default=True),
    requestedModelId: str | None = Form(default=None),
    files: list[UploadFile] = File(...),
    session: Session = Depends(getDatabaseSession),
) -> MaterialBatchUploadResultContract:
    return await MaterialService(session).uploadBatch(
        studentId=studentId,
        title=title,
        description=description,
        studentLearningContextId=studentLearningContextId,
        studentSubjectId=studentSubjectId,
        studentLearningUnitId=studentLearningUnitId,
        analysisRequested=analysisRequested,
        studyEnabled=studyEnabled,
        requestedModelId=requestedModelId,
        files=files,
    )


@router.post(
    "/students/{studentId}/materials/{materialId}/analyze",
    response_model=MaterialUploadResultContract,
)
def analyzeMaterial(
    studentId: UUID,
    materialId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> MaterialUploadResultContract:
    return MaterialService(session).analyze(
        studentId,
        materialId,
    )


@router.patch(
    "/students/{studentId}/materials/{materialId}/model-preference",
    response_model=MaterialContract,
)
def updateMaterialModelPreference(
    studentId: UUID,
    materialId: UUID,
    request: MaterialModelPreferenceUpdateContract,
    session: Session = Depends(getDatabaseSession),
) -> MaterialContract:
    return MaterialService(session).updateModelPreference(
        studentId,
        materialId,
        request,
    )



@router.patch(
    "/students/{studentId}/materials/{materialId}/ai-preference",
    response_model=MaterialContract,
)
def updateMaterialAiPreference(
    studentId: UUID,
    materialId: UUID,
    request: MaterialAiPreferenceUpdateContract,
    session: Session = Depends(getDatabaseSession),
) -> MaterialContract:
    return MaterialService(session).updateAiPreference(
        studentId,
        materialId,
        request,
    )


@router.patch(
    "/students/{studentId}/materials/{materialId}/study-usage",
    response_model=MaterialContract,
)
def updateMaterialStudyUsage(
    studentId: UUID,
    materialId: UUID,
    request: MaterialStudyUsageUpdateContract,
    session: Session = Depends(getDatabaseSession),
) -> MaterialContract:
    return MaterialService(session).updateStudyUsage(
        studentId,
        materialId,
        request,
    )


@router.delete(
    "/students/{studentId}/materials/{materialId}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deleteMaterial(
    studentId: UUID,
    materialId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> Response:
    MaterialService(session).deleteMaterial(
        studentId,
        materialId,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/materials/{materialId}/structure",
    response_model=DocumentStructureContract,
)
def getMaterialStructure(
    materialId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> DocumentStructureContract:
    return MaterialService(session).getStructure(materialId)


@router.get("/materials/{materialId}/file")
def getMaterialFile(
    materialId: UUID,
    session: Session = Depends(getDatabaseSession),
):
    path, fileName, mimeType = MaterialService(session).getFilePath(
        materialId
    )

    return FileResponse(
        path=path,
        filename=fileName,
        media_type=mimeType,
    )
