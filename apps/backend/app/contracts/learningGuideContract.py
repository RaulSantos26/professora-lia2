from typing import Literal
from pydantic import BaseModel


GuideSection = Literal[
    "ACADEMIC_STAGE",
    "LEARNING_CONTEXT",
    "SUBJECT",
    "LEARNING_UNIT",
    "MATERIAL",
    "PEDAGOGICAL",
    "LIA_TUTOR",
    "LEARNING_GOAL",
    "STUDY_SCOPE",
    "STUDY_SESSION",
    "LEARNING_PROGRESS",
]

GuideStepStatus = Literal[
    "COMPLETE",
    "NEXT",
    "AVAILABLE",
    "OPTIONAL",
    "BLOCKED",
]


class LearningGuideStepContract(BaseModel):
    contractName: Literal["LearningGuideStep.v1"] = "LearningGuideStep.v1"
    section: GuideSection
    title: str
    description: str
    status: GuideStepStatus
    actionLabel: str


class LearningGuideContract(BaseModel):
    contractName: Literal["LearningGuide.v1"] = "LearningGuide.v1"
    recommendedSection: GuideSection
    headline: str
    message: str
    completedSteps: int
    totalSteps: int
    steps: list[LearningGuideStepContract]
