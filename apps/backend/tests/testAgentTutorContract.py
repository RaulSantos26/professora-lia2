from datetime import datetime, timezone
from uuid import uuid4

from app.contracts.agentTutorContract import (
    AgentMessageContract,
    AgentThreadContract,
)


def testAgentThreadPersistsStudentContext():
    studentId = uuid4()
    contextId = uuid4()
    subjectId = uuid4()
    unitId = uuid4()

    thread = AgentThreadContract(
        agentThreadId=uuid4(),
        studentId=studentId,
        studentLearningContextId=contextId,
        studentSubjectId=subjectId,
        studentLearningUnitId=unitId,
        title="Lia · Biologia · Tecidos",
        status="ACTIVE",
        memory={"lastIntent": "EXPLAIN"},
        createdAt=datetime.now(timezone.utc),
        updatedAt=datetime.now(timezone.utc),
        lastMessageAt=None,
    )

    assert thread.studentId == studentId
    assert thread.studentLearningUnitId == unitId
    assert thread.memory["lastIntent"] == "EXPLAIN"


def testAssistantMessageCanLinkVisualAndPedagogicalActions():
    message = AgentMessageContract(
        agentMessageId=uuid4(),
        agentThreadId=uuid4(),
        role="ASSISTANT",
        content="Criei o recurso.",
        citations=[],
        visualTaskIds=[uuid4()],
        actions=[
            {
                "type": "PEDAGOGICAL_ARTIFACT",
                "pedagogicalArtifactId": str(uuid4()),
            }
        ],
        createdAt=datetime.now(timezone.utc),
    )

    assert message.role == "ASSISTANT"
    assert len(message.visualTaskIds) == 1
    assert message.actions[0]["type"] == "PEDAGOGICAL_ARTIFACT"
