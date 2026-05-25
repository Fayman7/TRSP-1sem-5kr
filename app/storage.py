from __future__ import annotations

from typing import Any

_tasks: dict[int, dict[str, Any]] = {}
_next_id = 1


def reset_storage() -> None:
    global _next_id
    _tasks.clear()
    _next_id = 1


def create_task(data: dict[str, Any]) -> dict[str, Any]:
    global _next_id
    task = {"id": _next_id, **data}
    _tasks[_next_id] = task
    _next_id += 1
    return task.copy()


def get_task(task_id: int) -> dict[str, Any] | None:
    task = _tasks.get(task_id)
    return task.copy() if task else None


def list_tasks(
    owner_id: int,
    *,
    status: str | None = None,
    min_priority: int | None = None,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for task in _tasks.values():
        if task["owner_id"] != owner_id:
            continue
        if status is not None and task["status"] != status:
            continue
        if min_priority is not None and task["priority"] < min_priority:
            continue
        result.append(task.copy())
    return sorted(result, key=lambda t: t["id"])


def update_task_status(task_id: int, status: str) -> dict[str, Any] | None:
    task = _tasks.get(task_id)
    if task is None:
        return None
    task["status"] = status
    return task.copy()


def delete_task(task_id: int) -> bool:
    if task_id not in _tasks:
        return False
    del _tasks[task_id]
    return True
