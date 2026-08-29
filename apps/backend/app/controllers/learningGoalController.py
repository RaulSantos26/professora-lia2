from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.contracts.learningGoalContract import LearningGoalContract, LearningGoalCreateContract
from app.database.databaseDependency import getDatabaseSession
from app.services.learningGoalService import LearningGoalService

router = APIRouter(prefix="/students", tags=["learning-goals"])

@router.get("/{studentId}/learning-goals", response_model=list[LearningGoalContract])
def listGoals(studentId: UUID, session: Session = Depends(getDatabaseSession)):
    return LearningGoalService(session).listGoals(studentId)

@router.post("/{studentId}/learning-goals", response_model=LearningGoalContract, status_code=status.HTTP_201_CREATED)
def createGoal(studentId: UUID, request: LearningGoalCreateContract, session: Session = Depends(getDatabaseSession)):
    return LearningGoalService(session).createGoal(studentId, request)
