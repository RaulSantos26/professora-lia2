from uuid import UUID
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from app.contracts.studyScopeContract import StudyScopeContract, StudyScopeCreateContract
from app.contracts.studyScopeItemContract import StudyScopeCandidateContract, StudyScopeItemContract, StudyScopeItemCreateContract
from app.database.databaseDependency import getDatabaseSession
from app.services.studyScopeService import StudyScopeService

router = APIRouter(tags=["study-scopes"])

@router.get("/learning-goals/{learningGoalId}/study-scopes", response_model=list[StudyScopeContract])
def listScopes(learningGoalId: UUID, session: Session = Depends(getDatabaseSession)):
    return StudyScopeService(session).listScopes(learningGoalId)

@router.post("/learning-goals/{learningGoalId}/study-scopes", response_model=StudyScopeContract, status_code=status.HTTP_201_CREATED)
def createScope(learningGoalId: UUID, request: StudyScopeCreateContract, session: Session = Depends(getDatabaseSession)):
    return StudyScopeService(session).createScope(learningGoalId, request)

@router.get("/learning-goals/{learningGoalId}/scope-candidates", response_model=list[StudyScopeCandidateContract])
def listCandidates(
    learningGoalId: UUID,
    studyScopeId: UUID | None = Query(default=None),
    session: Session = Depends(getDatabaseSession),
):
    return StudyScopeService(session).listCandidates(learningGoalId, studyScopeId)

@router.get("/study-scopes/{studyScopeId}/items", response_model=list[StudyScopeItemContract])
def listItems(studyScopeId: UUID, session: Session = Depends(getDatabaseSession)):
    return StudyScopeService(session).listItems(studyScopeId)

@router.post("/study-scopes/{studyScopeId}/items", response_model=StudyScopeItemContract, status_code=status.HTTP_201_CREATED)
def addItem(studyScopeId: UUID, request: StudyScopeItemCreateContract, session: Session = Depends(getDatabaseSession)):
    return StudyScopeService(session).addItem(studyScopeId, request)

@router.delete("/study-scopes/{studyScopeId}/items/{studyScopeItemId}", status_code=status.HTTP_204_NO_CONTENT)
def removeItem(studyScopeId: UUID, studyScopeItemId: UUID, session: Session = Depends(getDatabaseSession)):
    StudyScopeService(session).removeItem(studyScopeId, studyScopeItemId)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
