from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: int = Field(..., ge=1, le=5)


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: int
    owner_id: int


class CurrentUser(BaseModel):
    id: int
    role: str


class UserResponse(BaseModel):
    id: int
    role: str


class AdminStatsResponse(BaseModel):
    total_tasks: int
    by_status: dict[str, int]


class RoomUsersResponse(BaseModel):
    room_id: str
    users: list[str]


class WebSocketMessage(BaseModel):
    type: str
    task: TaskResponse | None = None
    message: str | None = None
