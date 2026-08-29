import json
import os
import time
import urllib.error
import urllib.request

from app.contracts.aiModelContract import (
    AiModelContract,
    AiModelRegistryContract,
)
from app.domain.common.domainError import DomainError


class AiModelRegistryService:
    CACHE_SECONDS = 60

    _cache: AiModelRegistryContract | None = None
    _cacheAt: float = 0

    def __init__(self):
        self.ollamaUrl = os.getenv(
            "LIA2_OLLAMA_URL",
            "http://ollama:11434",
        ).rstrip("/")

    def listModels(
        self,
        forceRefresh: bool = False,
    ) -> AiModelRegistryContract:
        now = time.monotonic()

        if (
            not forceRefresh
            and self.__class__._cache is not None
            and now - self.__class__._cacheAt < self.CACHE_SECONDS
        ):
            return self.__class__._cache

        try:
            tags = self._getJson("/api/tags")
            models = []

            for item in tags.get("models", []):
                modelId = item.get("name") or item.get("model")
                if not modelId:
                    continue

                capabilities = self._capabilities(modelId)

                models.append(
                    AiModelContract(
                        modelId=modelId,
                        displayName=modelId,
                        provider="OLLAMA",
                        capabilities=capabilities,
                        available=True,
                    )
                )

            models.sort(key=lambda model: model.displayName.lower())

            registry = AiModelRegistryContract(
                providerAvailable=True,
                provider="OLLAMA",
                models=models,
                warning=None if models else "Nenhum modelo instalado no Ollama.",
            )

        except Exception as error:
            registry = AiModelRegistryContract(
                providerAvailable=False,
                provider="OLLAMA",
                models=[],
                warning=(
                    "Não foi possível consultar o Ollama. "
                    f"{type(error).__name__}"
                ),
            )

        self.__class__._cache = registry
        self.__class__._cacheAt = now

        return registry

    def validateModel(
        self,
        modelId: str | None,
        requiredCapability: str | None = None,
    ) -> None:
        if modelId is None:
            return

        registry = self.listModels()

        model = next(
            (
                item
                for item in registry.models
                if item.modelId == modelId
            ),
            None,
        )

        if model is None:
            raise DomainError(
                code="AI_MODEL_NOT_AVAILABLE",
                message=(
                    "O modelo escolhido não está disponível no servidor. "
                    "Selecione Automático ou outro modelo."
                ),
                httpStatus=409,
            )

        if (
            requiredCapability is not None
            and requiredCapability not in model.capabilities
        ):
            raise DomainError(
                code="AI_MODEL_CAPABILITY_MISMATCH",
                message=(
                    f"O modelo {model.displayName} não declara suporte a "
                    f"{requiredCapability}."
                ),
                httpStatus=409,
            )

    def _capabilities(self, modelId: str) -> list[str]:
        capabilities: list[str] = []

        try:
            payload = self._postJson(
                "/api/show",
                {"model": modelId},
            )

            rawCapabilities = payload.get("capabilities")
            if isinstance(rawCapabilities, list):
                normalized = {
                    str(item).strip().upper()
                    for item in rawCapabilities
                    if str(item).strip()
                }

                mapped: set[str] = set()
                for item in normalized:
                    if item in {"VISION", "IMAGES", "IMAGE"}:
                        mapped.add("VISION")
                    elif item in {"TOOLS", "TOOL"}:
                        mapped.add("TOOLS")
                    elif item in {"EMBEDDING", "EMBEDDINGS"}:
                        mapped.add("EMBEDDINGS")
                    elif item in {"COMPLETION", "GENERATE", "TEXT"}:
                        mapped.add("TEXT")
                    else:
                        mapped.add(item)

                capabilities = sorted(mapped)

            details = payload.get("details") or {}
            family = str(details.get("family") or "").lower()
            families = " ".join(
                str(item).lower()
                for item in details.get("families") or []
            )

            # Conservatively enrich only from provider metadata/model family.
            familyMetadata = f"{family} {families}"

            if any(
                marker in familyMetadata
                for marker in (
                    "clip",
                    "llava",
                    "vision",
                    "mllama",
                    "qwen2vl",
                    "qwen2.5vl",
                    "qwen3-vl",
                    "gemma3",
                    "gemma4",
                )
            ):
                if "VISION" not in capabilities:
                    capabilities.append("VISION")

            # Gemma 4 is a reasoning family in Ollama. Keep the provider
            # capability as source of truth when present, but enrich the
            # family metadata if older /api/show responses omit THINKING.
            if "gemma4" in familyMetadata:
                if "THINKING" not in capabilities:
                    capabilities.append("THINKING")

        except Exception:
            # Registry remains useful even if /api/show is unavailable.
            pass

        if not capabilities:
            # Conservative fallback only when the provider gave no
            # capability metadata at all.
            capabilities = ["TEXT"]

        return sorted(set(capabilities))

    def _getJson(self, path: str) -> dict:
        request = urllib.request.Request(
            f"{self.ollamaUrl}{path}",
            headers={"Accept": "application/json"},
        )

        with urllib.request.urlopen(request, timeout=4) as response:
            return json.loads(response.read().decode("utf-8"))

    def _postJson(self, path: str, body: dict) -> dict:
        request = urllib.request.Request(
            f"{self.ollamaUrl}{path}",
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(request, timeout=6) as response:
            return json.loads(response.read().decode("utf-8"))
