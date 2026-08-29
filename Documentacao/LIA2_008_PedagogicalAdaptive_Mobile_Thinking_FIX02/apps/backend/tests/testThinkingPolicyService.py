from types import SimpleNamespace

import pytest

from app.domain.common.domainError import DomainError
from app.services.thinkingPolicyService import ThinkingPolicyService


class FakeRegistry:
    def listModels(self):
        return SimpleNamespace(
            models=[
                SimpleNamespace(
                    modelId="qwen-thinking",
                    available=True,
                    capabilities=["TEXT", "THINKING"],
                ),
                SimpleNamespace(
                    modelId="gemma-thinking",
                    available=True,
                    capabilities=[
                        "TEXT",
                        "VISION",
                        "THINKING",
                    ],
                ),
                SimpleNamespace(
                    modelId="plain-text",
                    available=True,
                    capabilities=["TEXT"],
                ),
            ]
        )


def service():
    result = ThinkingPolicyService.__new__(
        ThinkingPolicyService
    )
    result.registry = FakeRegistry()
    return result


def testAutoEnablesThinkingForQwenAndGemma():
    policy = service()

    assert policy.resolve(
        modelId="qwen-thinking",
        thinkingMode="AUTO",
    ) is True

    assert policy.resolve(
        modelId="gemma-thinking",
        thinkingMode="AUTO",
    ) is True


def testAutoDoesNotInventThinkingCapability():
    policy = service()

    assert policy.resolve(
        modelId="plain-text",
        thinkingMode="AUTO",
    ) is False


def testOnRequiresThinkingCapability():
    policy = service()

    with pytest.raises(DomainError) as captured:
        policy.resolve(
            modelId="plain-text",
            thinkingMode="ON",
        )

    assert (
        captured.value.code
        == "AI_MODEL_THINKING_UNAVAILABLE"
    )


def testOffDisablesEvenThinkingCapableModel():
    policy = service()

    assert policy.resolve(
        modelId="qwen-thinking",
        thinkingMode="OFF",
    ) is False


def testOnAddsThinkingToRouterRequirements():
    policy = service()

    assert policy.additionalCapabilities("ON") == [
        "THINKING"
    ]
    assert policy.additionalCapabilities("AUTO") == []
