import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas import TaskResponse, WebSocketMessage
from app.storage import task_storage

router = APIRouter(tags=["websocket"])

_connections: dict[int, list[WebSocket]] = {}


def reset_connections() -> None:
    _connections.clear()


async def _register(user_id: int, websocket: WebSocket) -> None:
    await websocket.accept()
    _connections.setdefault(user_id, []).append(websocket)


def _unregister(user_id: int, websocket: WebSocket) -> None:
    peers = _connections.get(user_id, [])
    if websocket in peers:
        peers.remove(websocket)
    if not peers:
        _connections.pop(user_id, None)


async def broadcast_task_event(user_id: int, event_type: str, task: dict) -> None:
    message = WebSocketMessage(
        type=event_type,
        task=TaskResponse.model_validate(task),
    )
    payload = message.model_dump(mode="json")
    for ws in list(_connections.get(user_id, [])):
        try:
            await ws.send_json(payload)
        except RuntimeError:
            _unregister(user_id, ws)


@router.websocket("/ws/tasks")
async def tasks_websocket(websocket: WebSocket) -> None:
    user_id_raw = websocket.headers.get("x-user-id")
    if user_id_raw is None:
        await websocket.close(code=1008, reason="Missing X-User-Id header")
        return
    try:
        user_id = int(user_id_raw)
    except ValueError:
        await websocket.close(code=1008, reason="Invalid X-User-Id header")
        return

    await _register(user_id, websocket)
    try:
        await websocket.send_json(
            WebSocketMessage(
                type="connected",
                message=f"Subscribed to tasks for user {user_id}",
            ).model_dump(mode="json")
        )
        while True:
            data = await websocket.receive_text()
            try:
                command = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json(
                    WebSocketMessage(
                        type="error",
                        message="Invalid JSON payload",
                    ).model_dump(mode="json")
                )
                continue

            if command.get("action") == "list":
                tasks = task_storage.list_tasks(user_id)
                await websocket.send_json(
                    {
                        "type": "task_list",
                        "tasks": [
                            TaskResponse.model_validate(t).model_dump(mode="json")
                            for t in tasks
                        ],
                    }
                )
            else:
                await websocket.send_json(
                    WebSocketMessage(
                        type="error",
                        message="Unknown action. Use: list",
                    ).model_dump(mode="json")
                )
    except WebSocketDisconnect:
        pass
    finally:
        _unregister(user_id, websocket)
