import threading

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

ROOM_WS = "/ws/rooms/{room}?username={user}"


def _connect(client: TestClient, room: str, username: str):
    return client.websocket_connect(ROOM_WS.format(room=room, user=username))


def _drain_connected_event(websocket) -> dict:
    return websocket.receive_json()


def test_connect_with_valid_username(client: TestClient) -> None:
    with _connect(client, "python", "alice") as websocket:
        event = _drain_connected_event(websocket)
        assert event == {
            "type": "user_connected",
            "room_id": "python",
            "username": "alice",
        }

        response = client.get("/rooms/python/users")
        assert response.status_code == 200
        assert response.json() == {"room_id": "python", "users": ["alice"]}


def test_send_message_and_receive(client: TestClient) -> None:
    with _connect(client, "python", "alice") as websocket:
        _drain_connected_event(websocket)

        websocket.send_json({"type": "message", "text": "Всем привет"})
        message = websocket.receive_json()

        assert message == {
            "type": "message",
            "room_id": "python",
            "username": "alice",
            "text": "Всем привет",
        }


def test_two_clients_receive_same_message(client: TestClient) -> None:
    with _connect(client, "python", "alice") as ws_alice:
        _drain_connected_event(ws_alice)

        with _connect(client, "python", "bob") as ws_bob:
            _drain_connected_event(ws_alice)
            _drain_connected_event(ws_bob)

            ws_bob.send_json({"type": "message", "text": "Привет комнате"})
            alice_message = ws_alice.receive_json()
            bob_message = ws_bob.receive_json()

            expected = {
                "type": "message",
                "room_id": "python",
                "username": "bob",
                "text": "Привет комнате",
            }
            assert alice_message == expected
            assert bob_message == expected


def test_different_rooms_do_not_receive_foreign_messages(client: TestClient) -> None:
    with _connect(client, "python", "alice") as ws_python:
        _drain_connected_event(ws_python)

        with _connect(client, "java", "bob") as ws_java:
            _drain_connected_event(ws_java)

            ws_python.send_json({"type": "message", "text": "Только python"})
            python_message = ws_python.receive_json()
            assert python_message["room_id"] == "python"

            received: list[dict] = []
            error: list[Exception] = []

            def try_receive() -> None:
                try:
                    received.append(ws_java.receive_json())
                except Exception as exc:
                    error.append(exc)

            thread = threading.Thread(target=try_receive, daemon=True)
            thread.start()
            thread.join(timeout=0.5)

            assert received == []


def test_too_long_message_returns_error(client: TestClient) -> None:
    with _connect(client, "python", "alice") as websocket:
        _drain_connected_event(websocket)

        websocket.send_json({"type": "message", "text": "x" * 301})
        error = websocket.receive_json()

        assert error == {"type": "error", "detail": "Message is too long"}


def test_user_removed_from_room_after_disconnect(client: TestClient) -> None:
    with _connect(client, "python", "alice"):
        pass

    response = client.get("/rooms/python/users")
    assert response.json() == {"room_id": "python", "users": []}


def test_empty_username_closes_connection(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect):
        with _connect(client, "python", "   "):
            pass
