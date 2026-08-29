import pytest

from app.domain.common.domainError import DomainError
from app.services.ollamaClientService import OllamaClientService


def testOllamaTimeoutBecomesStructuredDomainError(
    monkeypatch,
):
    service = OllamaClientService()

    def timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr(
        "app.services.ollamaClientService.urllib.request.urlopen",
        timeout,
    )

    with pytest.raises(DomainError) as captured:
        service._post(
            "/api/chat",
            {"model": "test"},
            7,
        )

    assert captured.value.code == "OLLAMA_TIMEOUT"
    assert captured.value.httpStatus == 504
    assert "7 segundos" in captured.value.message


def testOllamaTimeoutsAreConfigurable(
    monkeypatch,
):
    monkeypatch.setenv(
        "LIA2_OLLAMA_CHAT_TIMEOUT_SECONDS",
        "360",
    )
    monkeypatch.setenv(
        "LIA2_OLLAMA_EMBEDDING_TIMEOUT_SECONDS",
        "180",
    )

    service = OllamaClientService()

    assert service.chatTimeoutSeconds == 360
    assert service.embeddingTimeoutSeconds == 180


def testInvalidTimeoutEnvFallsBackToDefault(
    monkeypatch,
):
    monkeypatch.setenv(
        "LIA2_OLLAMA_CHAT_TIMEOUT_SECONDS",
        "invalid",
    )

    service = OllamaClientService()

    assert service.chatTimeoutSeconds == 360
