from datetime import datetime, timezone
from uuid import uuid4

from app.contracts.visualTaskContract import VisualTaskContract


def testVisualTaskCanRepresentThreeScene():
    contract = VisualTaskContract(
        visualTaskId=uuid4(),
        studentId=uuid4(),
        agentThreadId=None,
        agentRunId=None,
        pedagogicalArtifactId=None,
        visualType="SCENE_3D",
        status="READY",
        title="Sistema Solar",
        renderer="THREE",
        spec={"objects": []},
        evidence=[],
        sourceMaterialIds=[],
        effectiveModelId="modelo",
        thinkingEnabled=True,
        createdAt=datetime.now(timezone.utc),
    )

    assert contract.contractName == "VisualTask.v1"
    assert contract.renderer == "THREE"
    assert contract.thinkingEnabled is True
