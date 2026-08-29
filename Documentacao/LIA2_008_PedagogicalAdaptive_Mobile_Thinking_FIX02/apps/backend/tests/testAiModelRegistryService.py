from app.services.aiModelRegistryService import AiModelRegistryService


def testAiModelRegistryReadsDynamicOllamaModels(monkeypatch):
    service = AiModelRegistryService()

    monkeypatch.setattr(
        service,
        "_getJson",
        lambda path: {
            "models": [
                {"name": "modelo-texto:latest"},
                {"name": "modelo-vision:latest"},
                {"name": "modelo-embed:latest"},
            ]
        },
    )

    def fake_show(path, body):
        if body["model"] == "modelo-vision:latest":
            return {
                "capabilities": ["completion", "vision"],
                "details": {"family": "multimodal"},
            }

        if body["model"] == "modelo-embed:latest":
            return {
                "capabilities": ["embedding"],
                "details": {"family": "embedding"},
            }

        return {
            "capabilities": ["completion"],
            "details": {"family": "text"},
        }

    monkeypatch.setattr(
        service,
        "_postJson",
        fake_show,
    )

    registry = service.listModels(forceRefresh=True)

    assert registry.providerAvailable is True
    assert len(registry.models) == 3

    vision = next(
        model
        for model in registry.models
        if model.modelId == "modelo-vision:latest"
    )

    assert "VISION" in vision.capabilities
    assert "TEXT" in vision.capabilities


    embedding = next(
        model
        for model in registry.models
        if model.modelId == "modelo-embed:latest"
    )

    assert "EMBEDDINGS" in embedding.capabilities
    assert "TEXT" not in embedding.capabilities

def testGemma4FamilyIsEnrichedWithThinkingAndVision(
    monkeypatch,
):
    service = AiModelRegistryService()

    monkeypatch.setattr(
        service,
        "_getJson",
        lambda path: {
            "models": [
                {"name": "gemma4:12b"},
            ]
        },
    )

    monkeypatch.setattr(
        service,
        "_postJson",
        lambda path, body: {
            "capabilities": ["completion"],
            "details": {
                "family": "gemma4",
                "families": ["gemma4"],
            },
        },
    )

    registry = service.listModels(forceRefresh=True)
    model = registry.models[0]

    assert "TEXT" in model.capabilities
    assert "VISION" in model.capabilities
    assert "THINKING" in model.capabilities
