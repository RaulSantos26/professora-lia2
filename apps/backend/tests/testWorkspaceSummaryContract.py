from app.contracts.workspaceSummaryContract import (
    WorkspaceSummaryContract,
)


def testWorkspaceSummaryKeepsAgenticAndVisualCounts():
    summary = WorkspaceSummaryContract(
        academicStageCount=1,
        learningContextCount=2,
        subjectCount=3,
        learningUnitCount=4,
        materialCount=5,
        pedagogicalArtifactCount=2,
        agentThreadCount=3,
        visualTaskCount=4,
        learningGoalCount=6,
        studyScopeCount=7,
        studySessionCount=8,
        learningProgressCount=9,
    )

    assert summary.contractName == "WorkspaceSummary.v3"
    assert summary.agentThreadCount == 3
    assert summary.visualTaskCount == 4
    assert summary.materialCount == 5
