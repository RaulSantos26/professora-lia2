from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.contracts.pedagogicalContract import (
    LearningAttemptContract,
    LearningAttemptSubmitContract,
    PedagogicalArtifactContract,
    PedagogicalArtifactCreateContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.pedagogicalService import PedagogicalService


router = APIRouter(
    prefix="/students",
    tags=["pedagogical"],
)


@router.post(
    "/{studentId}/pedagogical/artifacts",
    response_model=PedagogicalArtifactContract,
    status_code=status.HTTP_202_ACCEPTED,
)
def createPedagogicalArtifact(
    studentId: UUID,
    request: PedagogicalArtifactCreateContract,
    session: Session = Depends(getDatabaseSession),
) -> PedagogicalArtifactContract:
    return PedagogicalService(session).createArtifact(
        studentId=studentId,
        request=request,
    )


@router.get(
    "/{studentId}/pedagogical/artifacts",
    response_model=list[PedagogicalArtifactContract],
)
def listPedagogicalArtifacts(
    studentId: UUID,
    studentLearningContextId: UUID = Query(...),
    studentSubjectId: UUID = Query(...),
    studentLearningUnitId: UUID = Query(...),
    session: Session = Depends(getDatabaseSession),
) -> list[PedagogicalArtifactContract]:
    return PedagogicalService(session).listArtifacts(
        studentId=studentId,
        studentLearningContextId=studentLearningContextId,
        studentSubjectId=studentSubjectId,
        studentLearningUnitId=studentLearningUnitId,
    )


@router.get(
    "/{studentId}/pedagogical/artifacts/{artifactId}",
    response_model=PedagogicalArtifactContract,
)
def getPedagogicalArtifact(
    studentId: UUID,
    artifactId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> PedagogicalArtifactContract:
    return PedagogicalService(session).getArtifact(
        studentId=studentId,
        artifactId=artifactId,
    )


@router.post(
    "/{studentId}/pedagogical/artifacts/{artifactId}/attempts",
    response_model=LearningAttemptContract,
)
def submitPedagogicalAttempt(
    studentId: UUID,
    artifactId: UUID,
    request: LearningAttemptSubmitContract,
    session: Session = Depends(getDatabaseSession),
) -> LearningAttemptContract:
    return PedagogicalService(session).submitAttempt(
        studentId=studentId,
        artifactId=artifactId,
        request=request,
    )


@router.delete(
    "/{studentId}/pedagogical/artifacts/{artifactId}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def archivePedagogicalArtifact(
    studentId: UUID,
    artifactId: UUID,
    session: Session = Depends(getDatabaseSession),
) -> Response:
    PedagogicalService(session).archiveArtifact(
        studentId=studentId,
        artifactId=artifactId,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
