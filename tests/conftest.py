import pytest
from fastapi.testclient import TestClient

from app.storage import reset_storage
from app.main import app
from app.room_manager import room_manager
from app.routers import websocket as ws_router


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage() -> None:
    reset_storage()
    ws_router.reset_connections()
    room_manager.reset()
