from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.contracts.studentLearningContextContract import (
    StudentLearningContextCreateContract,
    StudentLearningContextViewContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.studentLearningContextService import (
    StudentLearningContextService,
)


router = APIRouter(
    prefix="/students",
    tags=["student-learning-contexts"],
)


@router.get(
    "/{studentId}/learning-contexts",
    response_model=list[StudentLearningContextViewContract],
)
def listStudentLearningContexts(
    studentId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> list[StudentLearningContextViewContract]:
    return StudentLearningContextService(session).listStudentLearningContexts(
        studentId
    )


@router.post(
    "/{studentId}/learning-contexts/{learningContextId}",
    response_model=StudentLearningContextViewContract,
    status_code=status.HTTP_201_CREATED,
)
def assignLearningContext(
    studentId: UUID,
    learningContextId: UUID,
    request: StudentLearningContextCreateContract,
    session: Session = Depends(getDatabaseSession),
) -> StudentLearningContextViewContract:
    return StudentLearningContextService(session).assignLearningContext(
        studentId,
        learningContextId,
        request,
    )
