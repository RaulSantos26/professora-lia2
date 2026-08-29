from typing import Literal

from pydantic import BaseModel, Field


class VisionElementContract(BaseModel):
    elementType: Literal[
        "FIGURE",
        "DIAGRAM",
        "TABLE",
        "PHOTO",
        "CAPTION",
        "OTHER",
    ]
    title: str | None = None
    description: str
    labels: list[str] = Field(default_factory=list)


class VisionAnalysisContract(BaseModel):
    orientationDegrees: Literal[0, 90, 180, 270] = 0
    extractedText: str = ""
    summary: str = ""
    visualElements: list[VisionElementContract] = Field(
        default_factory=list
    )
