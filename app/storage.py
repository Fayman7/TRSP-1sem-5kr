from __future__ import annotations

from typing import Any


class TaskStorage:
    def __init__(self) -> None:
        self._tasks: dict[int, dict[str, Any]] = {}
        self._next_id = 1

    def reset(self) -> None:
        self._tasks.clear()
        self._next_id = 1

    def create_task(self, data: dict[str, Any]) -> dict[str, Any]:
        task = {"id": self._next_id, **data}
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task.copy()

    def get_task(self, task_id: int) -> dict[str, Any] | None:
        task = self._tasks.get(task_id)
        return task.copy() if task else None

    def list_tasks(
        self,
        owner_id: int,
        *,
        status: str | None = None,
        min_priority: int | None = None,
    ) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for task in self._tasks.values():
            if task["owner_id"] != owner_id:
                continue
            if status is not None and task["status"] != status:
                continue
            if min_priority is not None and task["priority"] < min_priority:
                continue
            result.append(task.copy())
        return sorted(result, key=lambda t: t["id"])

    def update_task_status(self, task_id: int, status: str) -> dict[str, Any] | None:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        task["status"] = status
        return task.copy()

    def delete_task(self, task_id: int) -> bool:
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        return True

    def get_stats(self) -> dict[str, Any]:
        by_status = {"todo": 0, "in_progress": 0, "done": 0}
        for task in self._tasks.values():
            by_status[task["status"]] += 1
        return {
            "total_tasks": len(self._tasks),
            "by_status": by_status,
        }


task_storage = TaskStorage()


def reset_storage() -> None:
    task_storage.reset()
