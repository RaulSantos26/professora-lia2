from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.contracts.learningContextContract import (
    LearningContextContract,
    LearningContextCreateContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.learningContextService import LearningContextService


router = APIRouter(
    prefix="/learning-contexts",
    tags=["learning-contexts"],
)


@router.get(
    "",
    response_model=list[LearningContextContract],
)
def listLearningContexts(
    session: Session = Depends(getDatabaseSession),
) -> list[LearningContextContract]:
    return LearningContextService(session).listLearningContexts()


@router.post(
    "",
    response_model=LearningContextContract,
    status_code=status.HTTP_201_CREATED,
)
def createLearningContext(
    request: LearningContextCreateContract,
    session: Session = Depends(getDatabaseSession),
) -> LearningContextContract:
    return LearningContextService(session).createLearningContext(request)
