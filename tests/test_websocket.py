import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


def test_websocket_connect_and_list_tasks(client: TestClient) -> None:
    client.post(
        "/tasks",
        headers={"X-User-Id": "10"},
        json={
            "title": "WS задача",
            "status": "todo",
            "priority": 3,
        },
    )

    with client.websocket_connect("/ws/tasks", headers={"X-User-Id": "10"}) as websocket:
        connected = websocket.receive_json()
        assert connected["type"] == "connected"

        websocket.send_json({"action": "list"})
        task_list = websocket.receive_json()

        assert task_list["type"] == "task_list"
        assert len(task_list["tasks"]) == 1
        assert task_list["tasks"][0]["title"] == "WS задача"


def test_websocket_without_header_is_rejected(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/tasks") as websocket:
            websocket.receive_json()
