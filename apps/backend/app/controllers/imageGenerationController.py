from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.contracts.imageGenerationContract import ImageGenerationTaskContract
from app.database.databaseDependency import getDatabaseSession
from app.services.imageGenerationService import ImageGenerationService


router = APIRouter(prefix="/students", tags=["image-generation"])


@router.get("/{studentId}/image-tasks", response_model=list[ImageGenerationTaskContract])
def listImageTasks(studentId: UUID, session: Session = Depends(getDatabaseSession)) -> list[ImageGenerationTaskContract]:
    return ImageGenerationService(session).list(studentId=studentId)


@router.get("/{studentId}/image-tasks/{imageTaskId}", response_model=ImageGenerationTaskContract)
def getImageTask(studentId: UUID, imageTaskId: UUID, session: Session = Depends(getDatabaseSession)) -> ImageGenerationTaskContract:
    return ImageGenerationService(session).get(studentId=studentId, imageTaskId=imageTaskId)


@router.get("/{studentId}/image-tasks/{imageTaskId}/asset")
def getImageAsset(studentId: UUID, imageTaskId: UUID, session: Session = Depends(getDatabaseSession)) -> FileResponse:
    return ImageGenerationService(session).asset(studentId=studentId, imageTaskId=imageTaskId)
