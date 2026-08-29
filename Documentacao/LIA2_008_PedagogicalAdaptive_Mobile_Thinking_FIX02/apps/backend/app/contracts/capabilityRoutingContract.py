from typing import Literal

from pydantic import BaseModel


class CapabilityRoutingDecisionContract(BaseModel):
    contractName: Literal[
        "CapabilityRoutingDecision.v1"
    ] = "CapabilityRoutingDecision.v1"

    capability: str
    requestedModelId: str | None
    effectiveModelId: str
    provider: str
    fallbackUsed: bool
    fallbackReason: str | None
