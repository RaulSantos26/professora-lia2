from typing import Literal

from pydantic import BaseModel


class AiExecutionPreferenceContract(BaseModel):
    contractName: Literal[
        "AiExecutionPreference.v1"
    ] = "AiExecutionPreference.v1"

    mode: Literal["AUTO", "FIXED", "CUSTOM"] = "AUTO"
    fixedModelId: str | None = None
    textModelId: str | None = None
    visionModelId: str | None = None
    embeddingModelId: str | None = None
    thinkingMode: Literal["AUTO", "ON", "OFF"] = "AUTO"


class MaterialAiPreferenceUpdateContract(
    AiExecutionPreferenceContract
):
    contractName: Literal[
        "MaterialAiPreferenceUpdate.v1"
    ] = "MaterialAiPreferenceUpdate.v1"
