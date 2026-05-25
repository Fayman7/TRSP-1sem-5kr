import pytest
from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok", "env": "local"}


def test_health_returns_docker_env(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    monkeypatch.setenv("APP_ENV", "docker")

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "env": "docker"}
