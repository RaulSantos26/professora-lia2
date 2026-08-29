from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.contracts.learningGuideContract import LearningGuideContract
from app.database.databaseDependency import getDatabaseSession
from app.services.learningGuideService import LearningGuideService


router = APIRouter(
    prefix="/students",
    tags=["learning-guide"],
)


@router.get(
    "/{studentId}/learning-guide",
    response_model=LearningGuideContract,
)
def getLearningGuide(
    studentId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> LearningGuideContract:
    return LearningGuideService(session).build(studentId)
