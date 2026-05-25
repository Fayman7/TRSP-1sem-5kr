from fastapi import Header, HTTPException, Query, status


def get_current_user_id(x_user_id: str | None = Header(default=None, alias="X-User-Id")) -> int:
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-User-Id header",
        )


def parse_ws_user_id(user_id: str | None = Query(default=None, alias="user_id")) -> int:
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user_id query parameter",
        )
    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user_id query parameter",
        )


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
