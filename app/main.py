from fastapi import FastAPI

from app.config import get_app_env
from app.routers import admin, rooms, tasks, users, websocket

app = FastAPI(title="Task Manager API", version="1.0.0")

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(websocket.router)
app.include_router(rooms.router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "env": get_app_env()}
