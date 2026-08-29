from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.contracts.studySessionContract import StudySessionStartContract, StudySessionViewContract
from app.database.databaseDependency import getDatabaseSession
from app.services.studySessionService import StudySessionService

router = APIRouter(tags=["study-sessions"])

@router.get("/study-scopes/{studyScopeId}/sessions", response_model=list[StudySessionViewContract])
def listSessions(studyScopeId: UUID, session: Session = Depends(getDatabaseSession)):
    return StudySessionService(session).listSessions(studyScopeId)

@router.post("/study-scopes/{studyScopeId}/sessions", response_model=StudySessionViewContract, status_code=status.HTTP_201_CREATED)
def startSession(studyScopeId: UUID, request: StudySessionStartContract, session: Session = Depends(getDatabaseSession)):
    return StudySessionService(session).startSession(studyScopeId, request)

@router.post("/study-sessions/{studySessionId}/complete", response_model=StudySessionViewContract)
def completeSession(studySessionId: UUID, session: Session = Depends(getDatabaseSession)):
    return StudySessionService(session).completeSession(studySessionId)
