from fastapi.testclient import TestClient

from app.liaBackendApplication import application


client = TestClient(application)


def testHealthContract():
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()

    assert payload["contractName"] == "ServiceStatus.v1"
    assert payload["serviceName"] == "lia2-backend"
    assert payload["status"] == "ONLINE"
    assert "X-Correlation-Id" in response.headers
