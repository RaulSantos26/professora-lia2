import os

import httpx

from app.domain.common.domainError import DomainError


class ImageServiceClient:
    def __init__(self):
        self.baseUrl = os.getenv("LIA2_IMAGE_SERVICE_URL", "http://lia2-image-service:8000").rstrip("/")
        self.token = os.getenv("LIA2_IMAGE_INTERNAL_TOKEN", "")
        self.timeout = float(os.getenv("LIA2_IMAGE_SERVICE_TIMEOUT_SECONDS", "20"))

    def submit(self, payload: dict) -> dict:
        return self._request("POST", "/v1/image-jobs", json=payload)

    def get(self, requestId: str) -> dict:
        return self._request("GET", f"/v1/image-jobs/{requestId}")

    def health(self) -> dict:
        return self._request("GET", "/health")

    def _request(self, method: str, path: str, **kwargs) -> dict:
        headers = {"X-Lia2-Internal-Token": self.token} if self.token else {}
        try:
            response = httpx.request(method, f"{self.baseUrl}{path}", headers=headers, timeout=self.timeout, **kwargs)
        except httpx.HTTPError as error:
            raise DomainError(code="IMAGE_SERVICE_UNAVAILABLE", message="O serviço de imagens está indisponível.", httpStatus=503) from error
        if response.status_code == 404:
            raise DomainError(code="IMAGE_SERVICE_JOB_NOT_FOUND", message="O trabalho de imagem não existe no serviço.", httpStatus=409)
        if response.status_code >= 400:
            raise DomainError(code="IMAGE_SERVICE_REJECTED", message="O serviço de imagens rejeitou a solicitação.", httpStatus=503)
        return response.json()
