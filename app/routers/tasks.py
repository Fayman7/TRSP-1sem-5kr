from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app import storage
from app.dependencies import get_current_user_id, validate_task_status_filter
from app.schemas.task import TaskCreate, TaskResponse, TaskStatusUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _to_response(task: dict) -> TaskResponse:
    return TaskResponse.model_validate(task)


def _get_owned_task(task_id: int, owner_id: int) -> dict:
    task = storage.get_task(task_id)
    if task is None or task["owner_id"] != owner_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    owner_id: int = Depends(get_current_user_id),
) -> TaskResponse:
    task = storage.create_task(
        {
            "title": payload.title,
            "description": payload.description,
            "status": payload.status.value,
            "priority": payload.priority,
            "owner_id": owner_id,
        }
    )
    return _to_response(task)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    owner_id: int = Depends(get_current_user_id),
    status_filter: str | None = Depends(validate_task_status_filter),
    min_priority: int | None = Query(default=None, ge=1, le=5),
) -> list[TaskResponse]:
    tasks = storage.list_tasks(
        owner_id,
        status=status_filter,
        min_priority=min_priority,
    )
    return [_to_response(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    owner_id: int = Depends(get_current_user_id),
) -> TaskResponse:
    task = _get_owned_task(task_id, owner_id)
    return _to_response(task)


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    owner_id: int = Depends(get_current_user_id),
) -> TaskResponse:
    existing = storage.get_task(task_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    if existing["owner_id"] != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify another user's task",
        )
    updated = storage.update_task_status(task_id, payload.status.value)
    assert updated is not None
    return _to_response(updated)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    owner_id: int = Depends(get_current_user_id),
) -> Response:
    existing = storage.get_task(task_id)
    if existing is None or existing["owner_id"] != owner_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    storage.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
