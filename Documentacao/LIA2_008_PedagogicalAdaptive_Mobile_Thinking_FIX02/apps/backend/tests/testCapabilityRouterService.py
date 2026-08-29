from app.contracts.aiModelContract import (
    AiModelContract,
    AiModelRegistryContract,
)
from app.services.capabilityRouterService import CapabilityRouterService


def registry():
    return AiModelRegistryContract(
        providerAvailable=True,
        provider="OLLAMA",
        models=[
            AiModelContract(
                modelId="texto",
                displayName="texto",
                provider="OLLAMA",
                capabilities=["TEXT"],
                available=True,
            ),
            AiModelContract(
                modelId="visao",
                displayName="visao",
                provider="OLLAMA",
                capabilities=["TEXT", "VISION"],
                available=True,
            ),
            AiModelContract(
                modelId="visao-thinking",
                displayName="visao-thinking",
                provider="OLLAMA",
                capabilities=["TEXT", "VISION", "THINKING"],
                available=True,
            ),
            AiModelContract(
                modelId="embed",
                displayName="embed",
                provider="OLLAMA",
                capabilities=["EMBEDDINGS"],
                available=True,
            ),
        ],
    )


def testRouterUsesRequestedModelWhenCompatible(monkeypatch):
    service = CapabilityRouterService()
    monkeypatch.setattr(
        service.registryService,
        "listModels",
        lambda: registry(),
    )

    decision = service.route("VISION", "visao")

    assert decision.effectiveModelId == "visao"
    assert decision.fallbackUsed is False


def testRouterFallsBackWhenRequestedModelLacksCapability(monkeypatch):
    service = CapabilityRouterService()
    monkeypatch.setattr(
        service.registryService,
        "listModels",
        lambda: registry(),
    )

    decision = service.route("VISION", "texto")

    assert decision.effectiveModelId == "visao"
    assert decision.fallbackUsed is True


def testEmbeddingModelIsNotUsedAsTextModel(monkeypatch):
    service = CapabilityRouterService()
    monkeypatch.setattr(
        service.registryService,
        "listModels",
        lambda: registry(),
    )

    decision = service.route("TEXT")

    assert decision.effectiveModelId != "embed"

def testRouterCanRequireThinkingInAdditionToVision(monkeypatch):
    service = CapabilityRouterService()
    monkeypatch.setattr(
        service.registryService,
        "listModels",
        lambda: registry(),
    )

    decision = service.route(
        "VISION",
        additionalCapabilities=["THINKING"],
    )

    assert decision.effectiveModelId == "visao-thinking"


def testStrictRequestedModelCannotIgnoreThinkingRequirement(
    monkeypatch,
):
    service = CapabilityRouterService()
    monkeypatch.setattr(
        service.registryService,
        "listModels",
        lambda: registry(),
    )

    import pytest
    from app.domain.common.domainError import DomainError

    with pytest.raises(DomainError):
        service.route(
            "VISION",
            "visao",
            allowFallback=False,
            additionalCapabilities=["THINKING"],
        )
