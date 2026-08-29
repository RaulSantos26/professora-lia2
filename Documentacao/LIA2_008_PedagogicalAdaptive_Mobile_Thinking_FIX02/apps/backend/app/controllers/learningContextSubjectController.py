from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.contracts.learningContextSubjectContract import (
    LearningContextSubjectCreateContract,
    LearningContextSubjectViewContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.learningContextSubjectService import (
    LearningContextSubjectService,
)


router = APIRouter(
    prefix="/learning-contexts",
    tags=["learning-context-subjects"],
)


@router.get(
    "/{learningContextId}/subjects",
    response_model=list[LearningContextSubjectViewContract],
)
def listContextSubjects(
    learningContextId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> list[LearningContextSubjectViewContract]:
    return LearningContextSubjectService(session).listSubjectsForContext(
        learningContextId
    )


@router.post(
    "/{learningContextId}/subjects/{subjectId}",
    response_model=LearningContextSubjectViewContract,
    status_code=status.HTTP_201_CREATED,
)
def assignSubject(
    learningContextId: UUID,
    subjectId: UUID,
    request: LearningContextSubjectCreateContract,
    session: Session = Depends(getDatabaseSession),
) -> LearningContextSubjectViewContract:
    return LearningContextSubjectService(session).assignSubject(
        learningContextId,
        subjectId,
        request,
    )
