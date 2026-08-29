from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.contracts.visualTaskContract import (
    VisualTaskContract,
    VisualTaskCreateContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.visualLearningService import VisualLearningService


router = APIRouter(
    prefix="/students",
    tags=["visual-learning"],
)


@router.post(
    "/{studentId}/visual-tasks",
    response_model=VisualTaskContract,
    status_code=status.HTTP_201_CREATED,
)
def createVisualTask(
    studentId: UUID,
    request: VisualTaskCreateContract,
    session: Session = Depends(
        getDatabaseSession
    ),
) -> VisualTaskContract:
    return VisualLearningService(
        session
    ).create(
        studentId=studentId,
        request=request,
    )


@router.get(
    "/{studentId}/visual-tasks",
    response_model=list[VisualTaskContract],
)
def listVisualTasks(
    studentId: UUID,
    session: Session = Depends(
        getDatabaseSession
    ),
) -> list[VisualTaskContract]:
    return VisualLearningService(
        session
    ).list(studentId)


@router.get(
    "/{studentId}/visual-tasks/{visualTaskId}",
    response_model=VisualTaskContract,
)
def getVisualTask(
    studentId: UUID,
    visualTaskId: UUID,
    session: Session = Depends(
        getDatabaseSession
    ),
) -> VisualTaskContract:
    return VisualLearningService(
        session
    ).get(
        studentId=studentId,
        visualTaskId=visualTaskId,
    )
