from app.domain.common.domainError import DomainError
from app.services.aiModelRegistryService import AiModelRegistryService


class ThinkingPolicyService:
    """
    Resolves whether Ollama Thinking should be enabled.

    The reasoning trace is never returned to Student contracts. Only the
    final model content is consumed by Lia.
    """

    def __init__(self):
        self.registry = AiModelRegistryService()

    def resolve(
        self,
        *,
        modelId: str,
        thinkingMode: str,
    ) -> bool:
        mode = (thinkingMode or "AUTO").strip().upper()

        if mode not in {"AUTO", "ON", "OFF"}:
            raise DomainError(
                code="AI_THINKING_MODE_INVALID",
                message=(
                    "Modo de raciocínio inválido. "
                    "Use AUTO, ON ou OFF."
                ),
                httpStatus=422,
            )

        if mode in {"AUTO", "OFF"}:
            return False

        supportsThinking = self.supportsThinking(modelId)

        if not supportsThinking:
            raise DomainError(
                code="AI_MODEL_THINKING_UNAVAILABLE",
                message=(
                    f"O modelo '{modelId}' não declara suporte "
                    "à capability THINKING."
                ),
                httpStatus=409,
            )

        return True

    def additionalCapabilities(
        self,
        thinkingMode: str,
    ) -> list[str]:
        return (
            ["THINKING"]
            if (thinkingMode or "AUTO").strip().upper() == "ON"
            else []
        )

    def supportsThinking(
        self,
        modelId: str,
    ) -> bool:
        model = next(
            (
                item
                for item in self.registry.listModels().models
                if item.modelId == modelId and item.available
            ),
            None,
        )

        if model is None:
            raise DomainError(
                code="AI_MODEL_NOT_AVAILABLE",
                message=f"O modelo '{modelId}' não está disponível.",
                httpStatus=409,
            )

        return "THINKING" in {
            capability.upper()
            for capability in model.capabilities
        }
