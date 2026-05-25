import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app
from app.routers import websocket as ws_router


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage() -> None:
    storage.reset_storage()
    ws_router.reset_connections()
