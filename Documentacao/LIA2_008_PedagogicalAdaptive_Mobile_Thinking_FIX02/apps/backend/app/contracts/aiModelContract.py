from typing import Literal

from pydantic import BaseModel


class AiModelContract(BaseModel):
    contractName: Literal["AiModel.v1"] = "AiModel.v1"
    modelId: str
    displayName: str
    provider: str
    capabilities: list[str]
    available: bool


class AiModelRegistryContract(BaseModel):
    contractName: Literal["AiModelRegistry.v1"] = "AiModelRegistry.v1"
    providerAvailable: bool
    provider: str
    defaultMode: Literal["AUTO"] = "AUTO"
    models: list[AiModelContract]
    warning: str | None = None
