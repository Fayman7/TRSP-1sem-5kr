from fastapi import FastAPI

from app.config import get_app_env
from app.routers import tasks, websocket

app = FastAPI(title="Task Manager API", version="1.0.0")

app.include_router(tasks.router)
app.include_router(websocket.router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "env": get_app_env()}
