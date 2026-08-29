from app.contracts.workspaceSummaryContract import (
    WorkspaceSummaryContract,
)


def testWorkspaceSummaryKeepsPersistedCounts():
    summary = WorkspaceSummaryContract(
        academicStageCount=1,
        learningContextCount=2,
        subjectCount=3,
        learningUnitCount=4,
        materialCount=5,
        pedagogicalArtifactCount=2,
        learningGoalCount=6,
        studyScopeCount=7,
        studySessionCount=8,
        learningProgressCount=9,
    )

    assert summary.contractName == "WorkspaceSummary.v2"
    assert summary.studyScopeCount == 7
    assert summary.studySessionCount == 8
    assert summary.materialCount == 5
    assert summary.pedagogicalArtifactCount == 2
