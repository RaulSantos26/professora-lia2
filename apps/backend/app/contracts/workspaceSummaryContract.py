from typing import Literal

from pydantic import BaseModel


class WorkspaceSummaryContract(BaseModel):
    contractName: Literal["WorkspaceSummary.v3"] = "WorkspaceSummary.v3"
    academicStageCount: int
    learningContextCount: int
    subjectCount: int
    learningUnitCount: int
    materialCount: int
    pedagogicalArtifactCount: int
    agentThreadCount: int
    visualTaskCount: int
    learningGoalCount: int
    studyScopeCount: int
    studySessionCount: int
    learningProgressCount: int
