from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.contracts.ragContract import (
    RagQueryRequestContract,
    RagQueryResponseContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.ragService import RagService


router = APIRouter(
    prefix="/students",
    tags=["rag"],
)


@router.post(
    "/{studentId}/rag/query",
    response_model=RagQueryResponseContract,
)
def queryStudentRag(
    studentId: UUID,
    request: RagQueryRequestContract,
    session: Session = Depends(getDatabaseSession),
) -> RagQueryResponseContract:
    return RagService(session).query(
        studentId,
        request,
    )
