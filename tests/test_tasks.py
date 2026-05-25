from fastapi.testclient import TestClient

USER_10 = {"X-User-Id": "10"}
USER_20 = {"X-User-Id": "20"}


def _create_task(
    client: TestClient,
    headers: dict[str, str],
    *,
    title: str = "Подготовить тесты",
    description: str | None = "Написать интеграционные тесты",
    status: str = "todo",
    priority: int = 4,
) -> dict:
    response = client.post(
        "/tasks",
        headers=headers,
        json={
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
        },
    )
    return response


def test_create_task_success(client: TestClient) -> None:
    response = _create_task(client, USER_10)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["title"] == "Подготовить тесты"
    assert body["description"] == "Написать интеграционные тесты"
    assert body["status"] == "todo"
    assert body["priority"] == 4
    assert body["owner_id"] == 10


def test_create_task_title_too_short_returns_422(client: TestClient) -> None:
    response = client.post(
        "/tasks",
        headers=USER_10,
        json={
            "title": "ab",
            "status": "todo",
            "priority": 3,
        },
    )

    assert response.status_code == 422


def test_missing_user_header_returns_401(client: TestClient) -> None:
    response = client.get("/tasks")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing X-User-Id header"


def test_user_sees_only_own_tasks(client: TestClient) -> None:
    _create_task(client, USER_10, title="Задача пользователя 10")
    _create_task(client, USER_20, title="Задача пользователя 20")

    response = client.get("/tasks", headers=USER_10)

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Задача пользователя 10"
    assert tasks[0]["owner_id"] == 10


def test_filter_tasks_by_status_and_min_priority(client: TestClient) -> None:
    _create_task(client, USER_10, title="Низкий приоритет", status="todo", priority=2)
    _create_task(client, USER_10, title="В работе", status="in_progress", priority=4)
    _create_task(client, USER_10, title="Готово", status="done", priority=5)

    response = client.get(
        "/tasks",
        headers=USER_10,
        params={"status": "in_progress", "min_priority": 4},
    )

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "В работе"
    assert tasks[0]["status"] == "in_progress"
    assert tasks[0]["priority"] == 4


def test_update_task_status_success(client: TestClient) -> None:
    created = _create_task(client, USER_10).json()

    response = client.patch(
        f"/tasks/{created['id']}/status",
        headers=USER_10,
        json={"status": "done"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_get_foreign_or_missing_task_returns_404(client: TestClient) -> None:
    created = _create_task(client, USER_10).json()

    foreign = client.get(f"/tasks/{created['id']}", headers=USER_20)
    assert foreign.status_code == 404

    missing = client.get("/tasks/9999", headers=USER_10)
    assert missing.status_code == 404


def test_delete_task_success(client: TestClient) -> None:
    created = _create_task(client, USER_10).json()

    delete_response = client.delete(f"/tasks/{created['id']}", headers=USER_10)
    assert delete_response.status_code == 204

    get_response = client.get(f"/tasks/{created['id']}", headers=USER_10)
    assert get_response.status_code == 404


def test_invalid_status_filter_returns_400(client: TestClient) -> None:
    response = client.get("/tasks", headers=USER_10, params={"status": "invalid"})

    assert response.status_code == 400


def test_patch_foreign_task_returns_403(client: TestClient) -> None:
    created = _create_task(client, USER_10).json()

    response = client.patch(
        f"/tasks/{created['id']}/status",
        headers=USER_20,
        json={"status": "done"},
    )

    assert response.status_code == 403
