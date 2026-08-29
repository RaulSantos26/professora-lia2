from types import SimpleNamespace

import pytest

from app.contracts.aiExecutionPreferenceContract import (
    AiExecutionPreferenceContract,
)
from app.domain.common.domainError import DomainError
from app.services.aiExecutionPreferenceService import (
    AiExecutionPreferenceService,
)


class FakeRegistry:
    def listModels(self):
        return SimpleNamespace(
            models=[
                SimpleNamespace(
                    modelId="qwen-text",
                    available=True,
                    capabilities=["TEXT", "THINKING"],
                ),
                SimpleNamespace(
                    modelId="vision",
                    available=True,
                    capabilities=["TEXT", "VISION"],
                ),
                SimpleNamespace(
                    modelId="embed",
                    available=True,
                    capabilities=["EMBEDDINGS"],
                ),
                SimpleNamespace(
                    modelId="plain-text",
                    available=True,
                    capabilities=["TEXT"],
                ),
            ]
        )


def makeService():
    service = AiExecutionPreferenceService.__new__(
        AiExecutionPreferenceService
    )
    service.registry = FakeRegistry()
    return service


def testFixedTextOnlyModelIsRejectedForImageAnalysis():
    service = makeService()
    preference = AiExecutionPreferenceContract(
        mode="FIXED",
        fixedModelId="qwen-text",
    )

    with pytest.raises(DomainError) as captured:
        service.validateForMaterial(
            preference,
            materialType="IMAGE",
            analysisRequested=True,
        )

    assert (
        captured.value.code
        == "AI_FIXED_MODEL_CAPABILITY_MISMATCH"
    )
    assert "VISION" in captured.value.message
    assert "EMBEDDINGS" in captured.value.message


def testCustomModeAllowsDifferentModels():
    service = makeService()
    preference = AiExecutionPreferenceContract(
        mode="CUSTOM",
        textModelId="qwen-text",
        visionModelId="vision",
        embeddingModelId="embed",
    )

    service.validateForMaterial(
        preference,
        materialType="IMAGE",
        analysisRequested=True,
    )

def testFixedThinkingOnRequiresThinkingCapability():
    service = makeService()
    preference = AiExecutionPreferenceContract(
        mode="FIXED",
        fixedModelId="qwen-text",
        thinkingMode="ON",
    )

    with pytest.raises(DomainError) as captured:
        service.validateForMaterial(
            preference,
            materialType="TEXT",
            analysisRequested=True,
        )

    assert (
        captured.value.code
        == "AI_FIXED_MODEL_CAPABILITY_MISMATCH"
    )
    assert "EMBEDDINGS" in captured.value.message
    assert "THINKING" not in captured.value.message


def testCustomThinkingOnRejectsNonThinkingTextModel():
    service = makeService()
    preference = AiExecutionPreferenceContract(
        mode="CUSTOM",
        textModelId="plain-text",
        thinkingMode="ON",
    )

    with pytest.raises(DomainError) as captured:
        service.validate(preference)

    assert (
        captured.value.code
        == "AI_CUSTOM_MODEL_CAPABILITY_MISMATCH"
    )
    assert "THINKING" in captured.value.message
