from app.contracts.aiExecutionPreferenceContract import (
    AiExecutionPreferenceContract,
)
from app.domain.common.domainError import DomainError
from app.persistence.models.materialModel import MaterialModel
from app.services.aiModelRegistryService import AiModelRegistryService


class AiExecutionPreferenceService:
    def __init__(self):
        self.registry = AiModelRegistryService()

    def validate(
        self,
        preference: AiExecutionPreferenceContract,
    ) -> None:
        models = {
            model.modelId: model
            for model in self.registry.listModels().models
            if model.available
        }

        if preference.mode == "AUTO":
            return

        if preference.mode == "FIXED":
            if not preference.fixedModelId:
                raise DomainError(
                    code="AI_FIXED_MODEL_REQUIRED",
                    message=(
                        "Escolha um modelo para usar o modo Modelo fixo."
                    ),
                    httpStatus=422,
                )

            if preference.fixedModelId not in models:
                raise DomainError(
                    code="AI_MODEL_NOT_AVAILABLE",
                    message=(
                        f"O modelo '{preference.fixedModelId}' "
                        "não está disponível."
                    ),
                    httpStatus=422,
                )
            return

        custom = {
            "TEXT": preference.textModelId,
            "VISION": preference.visionModelId,
            "EMBEDDINGS": preference.embeddingModelId,
        }

        for capability, modelId in custom.items():
            if not modelId:
                continue

            model = models.get(modelId)

            if model is None:
                raise DomainError(
                    code="AI_MODEL_NOT_AVAILABLE",
                    message=(
                        f"O modelo '{modelId}' não está disponível."
                    ),
                    httpStatus=422,
                )

            capabilities = {
                item.upper()
                for item in model.capabilities
            }

            required = {capability}

            if (
                preference.thinkingMode == "ON"
                and capability in {"TEXT", "VISION"}
            ):
                required.add("THINKING")

            missing = sorted(required - capabilities)

            if missing:
                raise DomainError(
                    code="AI_CUSTOM_MODEL_CAPABILITY_MISMATCH",
                    message=(
                        f"O modelo '{modelId}' não suporta "
                        "as capabilities necessárias: "
                        f"{', '.join(missing)}."
                    ),
                    httpStatus=422,
                )

    def validateForMaterial(
        self,
        preference: AiExecutionPreferenceContract,
        *,
        materialType: str,
        analysisRequested: bool,
    ) -> None:
        self.validate(preference)

        if not analysisRequested or preference.mode != "FIXED":
            return

        required = {"TEXT", "EMBEDDINGS"}

        if materialType in {"PDF", "IMAGE", "DOCUMENT"}:
            required.add("VISION")

        if preference.thinkingMode == "ON":
            required.add("THINKING")

        model = self._model(preference.fixedModelId)

        capabilities = {
            value.upper()
            for value in model.capabilities
        }

        missing = sorted(required - capabilities)

        if missing:
            raise DomainError(
                code="AI_FIXED_MODEL_CAPABILITY_MISMATCH",
                message=(
                    f"O modelo fixo '{model.modelId}' não cobre "
                    f"as capacidades necessárias: {', '.join(missing)}. "
                    "Use Automático ou Personalizado."
                ),
                httpStatus=422,
            )

    def requestedModelFor(
        self,
        material: MaterialModel,
        capability: str,
    ) -> tuple[str | None, bool]:
        required = capability.upper()

        if material.aiMode == "FIXED":
            return material.fixedModelId, False

        if material.aiMode == "CUSTOM":
            modelId = {
                "TEXT": material.textModelId,
                "VISION": material.visionModelId,
                "EMBEDDINGS": material.embeddingModelId,
            }.get(required)

            return modelId, modelId is None

        return None, True

    def _model(self, modelId: str | None):
        if not modelId:
            raise DomainError(
                code="AI_MODEL_NOT_AVAILABLE",
                message="Modelo não informado.",
                httpStatus=422,
            )

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
                httpStatus=422,
            )

        return model
