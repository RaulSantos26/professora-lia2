from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.contracts.academicStageContract import (
    AcademicStageContract,
    AcademicStageCreateContract,
)
from app.contracts.studentContract import StudentContract, StudentCreateContract
from app.database.databaseDependency import getDatabaseSession
from app.services.academicStageService import AcademicStageService
from app.services.studentService import StudentService


router = APIRouter(
    prefix="/students",
    tags=["students"],
)


@router.get("", response_model=list[StudentContract])
def listStudents(
    session: Session = Depends(getDatabaseSession),
) -> list[StudentContract]:
    return StudentService(session).listStudents()


@router.post(
    "",
    response_model=StudentContract,
    status_code=status.HTTP_201_CREATED,
)
def createStudent(
    request: StudentCreateContract,
    session: Session = Depends(getDatabaseSession),
) -> StudentContract:
    return StudentService(session).createStudent(request)


@router.get(
    "/{studentId}",
    response_model=StudentContract,
)
def getStudent(
    studentId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> StudentContract:
    return StudentService(session).getStudent(studentId)


@router.get(
    "/{studentId}/academic-stages",
    response_model=list[AcademicStageContract],
)
def listAcademicStages(
    studentId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> list[AcademicStageContract]:
    return AcademicStageService(session).listAcademicStages(studentId)


@router.post(
    "/{studentId}/academic-stages",
    response_model=AcademicStageContract,
    status_code=status.HTTP_201_CREATED,
)
def createAcademicStage(
    studentId: UUID,
    request: AcademicStageCreateContract,
    session: Session = Depends(getDatabaseSession),
) -> AcademicStageContract:
    return AcademicStageService(session).createAcademicStage(
        studentId,
        request,
    )
