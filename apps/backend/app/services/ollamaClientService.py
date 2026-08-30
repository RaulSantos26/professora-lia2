import base64
import json
import os
import socket
import urllib.error
import urllib.request
from pathlib import Path

from app.domain.common.domainError import DomainError


class OllamaClientService:
    def __init__(self):
        self.baseUrl = os.getenv(
            "LIA2_OLLAMA_URL",
            "http://ollama:11434",
        ).rstrip("/")

        self.chatTimeoutSeconds = self._positiveIntEnv(
            "LIA2_OLLAMA_CHAT_TIMEOUT_SECONDS",
            360,
        )
        self.embeddingTimeoutSeconds = self._positiveIntEnv(
            "LIA2_OLLAMA_EMBEDDING_TIMEOUT_SECONDS",
            180,
        )

    def chatStructured(
        self,
        *,
        modelId: str,
        prompt: str,
        schema: dict,
        imagePath: Path | None = None,
        timeoutSeconds: int | None = None,
        think: bool | str | None = None,
    ) -> dict:
        message: dict = {
            "role": "user",
            "content": prompt,
        }

        if imagePath is not None:
            imageBase64 = base64.b64encode(
                imagePath.read_bytes()
            ).decode("ascii")
            message["images"] = [imageBase64]

        payload = {
            "model": modelId,
            "messages": [message],
            "stream": False,
            "format": schema,
            "options": {
                "temperature": 0,
                "num_predict": -1,
            },
        }

        if think is not None:
            payload["think"] = think

        effectiveTimeout = (
            timeoutSeconds
            if timeoutSeconds is not None
            else self.chatTimeoutSeconds
        )

        response = self._post(
            "/api/chat",
            payload,
            effectiveTimeout,
        )

        content = (
            (response.get("message") or {}).get("content")
            or ""
        ).strip()

        # Alguns modelos encerram uma resposta estruturada após preencher
        # apenas o campo interno "thinking". Preservamos o modo solicitado
        # na primeira tentativa, mas recuperamos a resposta final uma vez
        # sem thinking para não transformar esse comportamento em erro para
        # o aluno.
        if not content and think is True:
            retryPayload = dict(payload)
            retryPayload["think"] = False
            response = self._post(
                "/api/chat",
                retryPayload,
                effectiveTimeout,
            )
            content = (
                (response.get("message") or {}).get("content")
                or ""
            ).strip()

        if not content:
            raise DomainError(
                code="OLLAMA_EMPTY_RESPONSE",
                message=(
                    f"O modelo {modelId} não retornou conteúdo."
                ),
                httpStatus=502,
            )

        try:
            return json.loads(content)
        except json.JSONDecodeError as error:
            raise DomainError(
                code="OLLAMA_INVALID_STRUCTURED_OUTPUT",
                message=(
                    f"O modelo {modelId} retornou uma resposta "
                    f"estruturada inválida."
                ),
                httpStatus=502,
            ) from error

    def embed(
        self,
        *,
        modelId: str,
        inputs: list[str],
        timeoutSeconds: int | None = None,
    ) -> list[list[float]]:
        if not inputs:
            return []

        effectiveTimeout = (
            timeoutSeconds
            if timeoutSeconds is not None
            else self.embeddingTimeoutSeconds
        )

        response = self._post(
            "/api/embed",
            {
                "model": modelId,
                "input": inputs,
            },
            effectiveTimeout,
        )

        embeddings = response.get("embeddings")

        if (
            not isinstance(embeddings, list)
            or len(embeddings) != len(inputs)
        ):
            raise DomainError(
                code="OLLAMA_EMBEDDING_RESPONSE_INVALID",
                message=(
                    "O provedor de embeddings retornou uma "
                    "quantidade inesperada de vetores."
                ),
                httpStatus=502,
            )

        return [
            [float(value) for value in vector]
            for vector in embeddings
        ]

    def _post(
        self,
        path: str,
        payload: dict,
        timeoutSeconds: int,
    ) -> dict:
        request = urllib.request.Request(
            f"{self.baseUrl}{path}",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=timeoutSeconds,
            ) as response:
                return json.loads(
                    response.read().decode("utf-8")
                )

        except urllib.error.HTTPError as error:
            try:
                detail = error.read().decode("utf-8")
            except Exception:
                detail = ""

            raise DomainError(
                code="OLLAMA_HTTP_ERROR",
                message=(
                    f"Ollama retornou HTTP {error.code}. "
                    f"{detail[:300]}"
                ),
                httpStatus=502,
            ) from error

        except (TimeoutError, socket.timeout) as error:
            raise DomainError(
                code="OLLAMA_TIMEOUT",
                message=(
                    "O modelo demorou mais que o limite configurado "
                    f"de {timeoutSeconds} segundos para responder."
                ),
                httpStatus=504,
            ) from error

        except urllib.error.URLError as error:
            if isinstance(error.reason, (TimeoutError, socket.timeout)):
                raise DomainError(
                    code="OLLAMA_TIMEOUT",
                    message=(
                        "O modelo demorou mais que o limite configurado "
                        f"de {timeoutSeconds} segundos para responder."
                    ),
                    httpStatus=504,
                ) from error

            raise DomainError(
                code="OLLAMA_UNAVAILABLE",
                message=(
                    "Não foi possível acessar o Ollama para "
                    "executar a capability solicitada."
                ),
                httpStatus=503,
            ) from error

    def _positiveIntEnv(
        self,
        name: str,
        default: int,
    ) -> int:
        raw = os.getenv(name)

        if raw is None:
            return default

        try:
            value = int(raw)
        except ValueError:
            return default

        return value if value > 0 else default
