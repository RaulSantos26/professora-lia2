from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.contracts.subjectContract import SubjectContract, SubjectCreateContract
from app.database.databaseDependency import getDatabaseSession
from app.services.subjectService import SubjectService


router = APIRouter(
    prefix="/subjects",
    tags=["subjects"],
)


@router.get("", response_model=list[SubjectContract])
def listSubjects(
    session: Session = Depends(getDatabaseSession),
) -> list[SubjectContract]:
    return SubjectService(session).listSubjects()


@router.post(
    "",
    response_model=SubjectContract,
    status_code=status.HTTP_201_CREATED,
)
def createSubject(
    request: SubjectCreateContract,
    session: Session = Depends(getDatabaseSession),
) -> SubjectContract:
    return SubjectService(session).createSubject(request)
