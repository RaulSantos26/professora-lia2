from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.contracts.learningUnitContract import (
    LearningUnitContract,
    LearningUnitCreateContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.learningUnitService import LearningUnitService


router = APIRouter(
    prefix="/context-subjects",
    tags=["learning-units"],
)


@router.get(
    "/{learningContextSubjectId}/units",
    response_model=list[LearningUnitContract],
)
def listLearningUnits(
    learningContextSubjectId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> list[LearningUnitContract]:
    return LearningUnitService(session).listLearningUnits(
        learningContextSubjectId
    )


@router.post(
    "/{learningContextSubjectId}/units",
    response_model=LearningUnitContract,
    status_code=status.HTTP_201_CREATED,
)
def createLearningUnit(
    learningContextSubjectId: UUID,
    request: LearningUnitCreateContract,
    session: Session = Depends(getDatabaseSession),
) -> LearningUnitContract:
    return LearningUnitService(session).createLearningUnit(
        learningContextSubjectId,
        request,
    )
