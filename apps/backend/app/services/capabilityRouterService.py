from app.contracts.capabilityRoutingContract import (
    CapabilityRoutingDecisionContract,
)
from app.domain.common.domainError import DomainError
from app.services.aiModelRegistryService import AiModelRegistryService


class CapabilityRouterService:
    def __init__(self):
        self.registryService = AiModelRegistryService()

    def route(
        self,
        capability: str,
        requestedModelId: str | None = None,
        allowFallback: bool = True,
        additionalCapabilities: list[str] | None = None,
    ) -> CapabilityRoutingDecisionContract:
        required = capability.strip().upper()
        additional = {
            item.strip().upper()
            for item in (additionalCapabilities or [])
            if item.strip()
        }
        requirements = {required, *additional}
        registry = self.registryService.listModels()

        def supports(model) -> bool:
            declared = {
                item.upper()
                for item in model.capabilities
            }
            return requirements.issubset(declared)

        available = [
            model
            for model in registry.models
            if model.available and supports(model)
        ]

        if requestedModelId:
            requested = next(
                (
                    model
                    for model in registry.models
                    if model.modelId == requestedModelId
                    and model.available
                ),
                None,
            )

            if requested is not None and supports(requested):
                return CapabilityRoutingDecisionContract(
                    capability=required,
                    requestedModelId=requestedModelId,
                    effectiveModelId=requested.modelId,
                    provider=requested.provider,
                    fallbackUsed=False,
                    fallbackReason=None,
                )

            if not allowFallback:
                raise DomainError(
                    code="AI_FIXED_MODEL_CAPABILITY_MISMATCH",
                    message=(
                        f"O modelo '{requestedModelId}' não suporta "
                        "as capabilities necessárias: "
                        f"{', '.join(sorted(requirements))}."
                    ),
                    httpStatus=409,
                )

            if available:
                reason = (
                    f"O modelo solicitado '{requestedModelId}' não está "
                    "disponível para as capabilities "
                    f"{', '.join(sorted(requirements))}; "
                    f"foi usado '{available[0].modelId}'."
                )

                return CapabilityRoutingDecisionContract(
                    capability=required,
                    requestedModelId=requestedModelId,
                    effectiveModelId=available[0].modelId,
                    provider=available[0].provider,
                    fallbackUsed=True,
                    fallbackReason=reason,
                )

        if available:
            return CapabilityRoutingDecisionContract(
                capability=required,
                requestedModelId=requestedModelId,
                effectiveModelId=available[0].modelId,
                provider=available[0].provider,
                fallbackUsed=False,
                fallbackReason=None,
            )

        raise DomainError(
            code="AI_CAPABILITY_MODEL_NOT_AVAILABLE",
            message=(
                "Nenhum modelo disponível declara suporte às "
                f"capabilities {', '.join(sorted(requirements))}."
            ),
            httpStatus=409,
        )
