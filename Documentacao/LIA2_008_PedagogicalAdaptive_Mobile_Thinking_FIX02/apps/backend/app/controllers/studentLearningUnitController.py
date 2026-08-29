from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.contracts.studentLearningUnitContract import (
    StudentLearningUnitContract,
    StudentLearningUnitCreateContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.studentLearningUnitService import StudentLearningUnitService


router = APIRouter(
    prefix="/student-subjects",
    tags=["student-learning-units"],
)


@router.get(
    "/{studentSubjectId}/units",
    response_model=list[StudentLearningUnitContract],
)
def listLearningUnits(
    studentSubjectId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> list[StudentLearningUnitContract]:
    return StudentLearningUnitService(session).listLearningUnits(
        studentSubjectId
    )


@router.post(
    "/{studentSubjectId}/units",
    response_model=StudentLearningUnitContract,
    status_code=status.HTTP_201_CREATED,
)
def createLearningUnit(
    studentSubjectId: UUID,
    request: StudentLearningUnitCreateContract,
    session: Session = Depends(getDatabaseSession),
) -> StudentLearningUnitContract:
    return StudentLearningUnitService(session).createLearningUnit(
        studentSubjectId,
        request,
    )
