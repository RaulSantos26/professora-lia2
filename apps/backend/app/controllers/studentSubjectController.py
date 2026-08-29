from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.contracts.studentSubjectContract import (
    StudentSubjectContract,
    StudentSubjectCreateContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.studentSubjectService import StudentSubjectService


router = APIRouter(
    prefix="/student-learning-contexts",
    tags=["student-subjects"],
)


@router.get(
    "/{studentLearningContextId}/subjects",
    response_model=list[StudentSubjectContract],
)
def listStudentSubjects(
    studentLearningContextId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> list[StudentSubjectContract]:
    return StudentSubjectService(session).listStudentSubjects(
        studentLearningContextId
    )


@router.post(
    "/{studentLearningContextId}/subjects",
    response_model=StudentSubjectContract,
    status_code=status.HTTP_201_CREATED,
)
def createStudentSubject(
    studentLearningContextId: UUID,
    request: StudentSubjectCreateContract,
    session: Session = Depends(getDatabaseSession),
) -> StudentSubjectContract:
    return StudentSubjectService(session).createStudentSubject(
        studentLearningContextId,
        request,
    )
