from pathlib import Path


def backendRoot() -> Path:
    return Path(__file__).parents[1]


def testVisionPersistsThinkingAuditWithoutReasoningTrace():
    source = (
        backendRoot()
        / "app"
        / "services"
        / "materialPipelineService.py"
    ).read_text(encoding="utf-8")

    assert '"visionMeta"' in source
    assert '"thinkingEnabled": thinkingEnabled' in source
    assert '"thinking"' not in source[
        source.index('"visionMeta"'):
        source.index('"visionMeta"') + 250
    ]


def testRagAndPedagogicalCallsPassThinkingToOllama():
    rag = (
        backendRoot()
        / "app"
        / "services"
        / "ragService.py"
    ).read_text(encoding="utf-8")

    pedagogical = (
        backendRoot()
        / "app"
        / "services"
        / "pedagogicalGenerationService.py"
    ).read_text(encoding="utf-8")

    assert "think=thinkingEnabled" in rag
    assert "think=thinkingEnabled" in pedagogical
