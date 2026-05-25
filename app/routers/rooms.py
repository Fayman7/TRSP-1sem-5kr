from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.room_manager import room_manager
from app.schemas import RoomUsersResponse

router = APIRouter(tags=["rooms"])

MAX_MESSAGE_LENGTH = 300


@router.websocket("/ws/rooms/{room_id}")
async def room_chat(
    websocket: WebSocket,
    room_id: str,
    username: str | None = Query(default=None),
) -> None:
    if username is None or not username.strip():
        await websocket.close(code=1008, reason="Missing or empty username")
        return

    normalized_username = username.strip()

    await room_manager.connect(room_id, normalized_username, websocket)
    await room_manager.broadcast(
        room_id,
        {
            "type": "user_connected",
            "room_id": room_id,
            "username": normalized_username,
        },
    )

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") != "message":
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "Unsupported message type",
                    }
                )
                continue

            text = data.get("text", "")
            if len(text) > MAX_MESSAGE_LENGTH:
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "Message is too long",
                    }
                )
                continue

            await room_manager.broadcast(
                room_id,
                {
                    "type": "message",
                    "room_id": room_id,
                    "username": normalized_username,
                    "text": text,
                },
            )
    except WebSocketDisconnect:
        pass
    finally:
        await room_manager.disconnect(room_id, normalized_username, websocket)
        if not room_manager.has_active_user(room_id, normalized_username):
            await room_manager.broadcast(
                room_id,
                {
                    "type": "user_disconnected",
                    "room_id": room_id,
                    "username": normalized_username,
                },
            )


@router.get("/rooms/{room_id}/users", response_model=RoomUsersResponse)
def get_room_users(room_id: str) -> RoomUsersResponse:
    return RoomUsersResponse(room_id=room_id, users=room_manager.get_users(room_id))
