from __future__ import annotations

from fastapi import WebSocket
from starlette.websockets import WebSocketState


class RoomManager:
    def __init__(self) -> None:
        self._rooms: dict[str, dict[str, list[WebSocket]]] = {}

    def reset(self) -> None:
        self._rooms.clear()

    async def connect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms.setdefault(room_id, {}).setdefault(username, []).append(websocket)

    async def disconnect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        room = self._rooms.get(room_id)
        if room is None:
            return
        connections = room.get(username, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            room.pop(username, None)
        if not room:
            self._rooms.pop(room_id, None)

    async def broadcast(self, room_id: str, payload: dict) -> None:
        room = self._rooms.get(room_id)
        if room is None:
            return
        for connections in room.values():
            for websocket in list(connections):
                try:
                    await websocket.send_json(payload)
                except RuntimeError:
                    pass

    def _prune_room(self, room_id: str) -> None:
        room = self._rooms.get(room_id)
        if room is None:
            return
        for username, connections in list(room.items()):
            alive = [ws for ws in connections if ws.client_state == WebSocketState.CONNECTED]
            if alive:
                room[username] = alive
            else:
                room.pop(username, None)
        if not room:
            self._rooms.pop(room_id, None)

    def has_active_user(self, room_id: str, username: str) -> bool:
        self._prune_room(room_id)
        room = self._rooms.get(room_id)
        return bool(room and room.get(username))

    def get_users(self, room_id: str) -> list[str]:
        self._prune_room(room_id)
        room = self._rooms.get(room_id)
        if room is None:
            return []
        return sorted(room.keys())


room_manager = RoomManager()
