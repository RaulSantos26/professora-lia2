from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.contracts.workspaceSummaryContract import WorkspaceSummaryContract
from app.database.databaseDependency import getDatabaseSession
from app.services.workspaceSummaryService import WorkspaceSummaryService


router = APIRouter(
    prefix="/students",
    tags=["workspace-summary"],
)


@router.get(
    "/{studentId}/workspace-summary",
    response_model=WorkspaceSummaryContract,
)
def getWorkspaceSummary(
    studentId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> WorkspaceSummaryContract:
    return WorkspaceSummaryService(session).get(studentId)
