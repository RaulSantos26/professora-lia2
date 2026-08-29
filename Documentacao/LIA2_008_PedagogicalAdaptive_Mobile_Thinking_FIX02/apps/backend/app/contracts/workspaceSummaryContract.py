from typing import Literal

from pydantic import BaseModel


class WorkspaceSummaryContract(BaseModel):
    contractName: Literal["WorkspaceSummary.v2"] = "WorkspaceSummary.v2"
    academicStageCount: int
    learningContextCount: int
    subjectCount: int
    learningUnitCount: int
    materialCount: int
    pedagogicalArtifactCount: int
    learningGoalCount: int
    studyScopeCount: int
    studySessionCount: int
    learningProgressCount: int
