from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.contracts.agentTutorContract import (
    AgentConversationContract,
    AgentMessageCreateContract,
    AgentRunContract,
    AgentThreadContract,
    AgentThreadCreateContract,
)
from app.database.databaseDependency import getDatabaseSession
from app.services.agentTutorService import AgentTutorService


router = APIRouter(
    prefix="/students",
    tags=["agent-tutor"],
)


@router.post(
    "/{studentId}/lia/threads",
    response_model=AgentThreadContract,
    status_code=status.HTTP_201_CREATED,
)
def createThread(
    studentId: UUID,
    request: AgentThreadCreateContract,
    session: Session = Depends(
        getDatabaseSession
    ),
) -> AgentThreadContract:
    return AgentTutorService(
        session
    ).createThread(
        studentId=studentId,
        request=request,
    )


@router.get(
    "/{studentId}/lia/threads",
    response_model=list[AgentThreadContract],
)
def listThreads(
    studentId: UUID,
    session: Session = Depends(
        getDatabaseSession
    ),
) -> list[AgentThreadContract]:
    return AgentTutorService(
        session
    ).listThreads(studentId)


@router.get(
    "/{studentId}/lia/threads/{threadId}",
    response_model=AgentConversationContract,
)
def getConversation(
    studentId: UUID,
    threadId: UUID,
    session: Session = Depends(
        getDatabaseSession
    ),
) -> AgentConversationContract:
    return AgentTutorService(
        session
    ).conversation(
        studentId=studentId,
        threadId=threadId,
    )


@router.post(
    "/{studentId}/lia/threads/{threadId}/messages",
    response_model=AgentRunContract,
    status_code=status.HTTP_202_ACCEPTED,
)
def sendMessage(
    studentId: UUID,
    threadId: UUID,
    request: AgentMessageCreateContract,
    session: Session = Depends(
        getDatabaseSession
    ),
) -> AgentRunContract:
    return AgentTutorService(
        session
    ).send(
        studentId=studentId,
        threadId=threadId,
        request=request,
    )


@router.get(
    "/{studentId}/lia/threads/{threadId}/runs/{runId}",
    response_model=AgentRunContract,
)
def getRun(
    studentId: UUID,
    threadId: UUID,
    runId: UUID,
    session: Session = Depends(
        getDatabaseSession
    ),
) -> AgentRunContract:
    return AgentTutorService(
        session
    ).getRun(
        studentId=studentId,
        threadId=threadId,
        runId=runId,
    )


@router.post(
    "/{studentId}/lia/threads/{threadId}/runs/{runId}/retry",
    response_model=AgentRunContract,
    status_code=status.HTTP_202_ACCEPTED,
)
def retryRun(
    studentId: UUID,
    threadId: UUID,
    runId: UUID,
    session: Session = Depends(
        getDatabaseSession
    ),
) -> AgentRunContract:
    return AgentTutorService(
        session
    ).retryRun(
        studentId=studentId,
        threadId=threadId,
        runId=runId,
    )


@router.delete(
    "/{studentId}/lia/threads/{threadId}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def archiveThread(
    studentId: UUID,
    threadId: UUID,
    session: Session = Depends(
        getDatabaseSession
    ),
) -> Response:
    AgentTutorService(
        session
    ).archiveThread(
        studentId=studentId,
        threadId=threadId,
    )
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
