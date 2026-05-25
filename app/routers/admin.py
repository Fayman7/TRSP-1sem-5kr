from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_storage, require_admin
from app.schemas import AdminStatsResponse, CurrentUser
from app.storage import TaskStorage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
def get_stats(
    _: CurrentUser = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage),
) -> AdminStatsResponse:
    stats = storage.get_stats()
    return AdminStatsResponse.model_validate(stats)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_as_admin(
    task_id: int,
    _: CurrentUser = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage),
) -> Response:
    if storage.get_task(task_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    storage.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
