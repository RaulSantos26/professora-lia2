from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.contracts.studentLearningStateContract import (
    StudentLearningStateContract,
    StudentLearningStateUpdateContract,
    StudentLearningStateViewContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.studentLearningStateService import StudentLearningStateService

router = APIRouter(prefix="/students", tags=["student-learning-state"])

@router.get("/{studentId}/learning-states", response_model=list[StudentLearningStateViewContract])
def listStates(studentId: UUID, session: Session = Depends(getDatabaseSession)):
    return StudentLearningStateService(session).listStates(studentId)

@router.put("/{studentId}/learning-units/{studentLearningUnitId}/state", response_model=StudentLearningStateContract)
def updateState(
    studentId: UUID,
    studentLearningUnitId: UUID,
    request: StudentLearningStateUpdateContract,
    session: Session = Depends(getDatabaseSession),
):
    return StudentLearningStateService(session).updateState(
        studentId,
        studentLearningUnitId,
        request,
    )
