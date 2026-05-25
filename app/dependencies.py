from fastapi import Depends, Header, HTTPException, Query, status

from app.schemas import CurrentUser
from app.storage import TaskStorage, task_storage


def get_current_user(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_user_role: str | None = Header(default="user", alias="X-User-Role"),
) -> CurrentUser:
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-User-Id header",
        )
    return CurrentUser(id=user_id, role=x_user_role or "user")


def require_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def get_storage() -> TaskStorage:
    return task_storage


def validate_task_status_filter(
    status_filter: str | None = Query(default=None, alias="status"),
) -> str | None:
    if status_filter is None:
        return None
    allowed = {"todo", "in_progress", "done"}
    if status_filter not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status filter. Allowed: {', '.join(sorted(allowed))}",
        )
    return status_filter
