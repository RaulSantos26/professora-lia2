import json

from app.services.ollamaClientService import OllamaClientService


def testChatStructuredSendsThinkTrueAndUsesOnlyFinalContent(
    monkeypatch,
):
    service = OllamaClientService()
    captured = {}

    def fakePost(path, payload, timeoutSeconds):
        captured["path"] = path
        captured["payload"] = payload

        return {
            "message": {
                "thinking": (
                    "raciocínio interno que não deve "
                    "ser retornado pelo contrato"
                ),
                "content": json.dumps(
                    {
                        "answer": "Resposta final",
                    }
                ),
            }
        }

    monkeypatch.setattr(service, "_post", fakePost)

    result = service.chatStructured(
        modelId="modelo-thinking",
        prompt="Explique.",
        schema={
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
            },
            "required": ["answer"],
        },
        think=True,
    )

    assert captured["path"] == "/api/chat"
    assert captured["payload"]["think"] is True
    assert result == {"answer": "Resposta final"}
    assert "thinking" not in result


def testChatStructuredCanExplicitlyDisableThinking(
    monkeypatch,
):
    service = OllamaClientService()
    captured = {}

    monkeypatch.setattr(
        service,
        "_post",
        lambda path, payload, timeoutSeconds: (
            captured.setdefault("payload", payload)
            or {}
        ),
    )
    captured.clear()

    def fakePost(path, payload, timeoutSeconds):
        captured["payload"] = payload
        return {
            "message": {
                "content": '{"answer":"ok"}',
            }
        }

    monkeypatch.setattr(service, "_post", fakePost)

    service.chatStructured(
        modelId="modelo",
        prompt="Teste",
        schema={
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
            },
            "required": ["answer"],
        },
        think=False,
    )

    assert captured["payload"]["think"] is False
