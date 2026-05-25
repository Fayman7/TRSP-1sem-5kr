from fastapi.testclient import TestClient

USER_10 = {"X-User-Id": "10", "X-User-Role": "user"}
USER_20 = {"X-User-Id": "20", "X-User-Role": "user"}
ADMIN = {"X-User-Id": "1", "X-User-Role": "admin"}


def _create_task(client: TestClient, headers: dict[str, str], owner_title: str = "Задача") -> dict:
    response = client.post(
        "/tasks",
        headers=headers,
        json={
            "title": owner_title,
            "status": "todo",
            "priority": 3,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_users_me_returns_current_user(client: TestClient) -> None:
    response = client.get("/users/me", headers=USER_10)

    assert response.status_code == 200
    assert response.json() == {"id": 10, "role": "user"}


def test_missing_user_id_returns_401(client: TestClient) -> None:
    response = client.get("/users/me")

    assert response.status_code == 401


def test_user_forbidden_on_admin_stats(client: TestClient) -> None:
    response = client.get("/admin/stats", headers=USER_10)

    assert response.status_code == 403


def test_admin_gets_stats(client: TestClient) -> None:
    _create_task(client, USER_10, "Задача один")
    _create_task(client, USER_10, "Задача два")
    task3 = _create_task(client, USER_20, "Задача три")
    task4 = _create_task(client, USER_10, "Задача четыре")
    client.patch(
        f"/tasks/{task3['id']}/status",
        headers=USER_20,
        json={"status": "in_progress"},
    )
    client.patch(
        f"/tasks/{task4['id']}/status",
        headers=USER_10,
        json={"status": "done"},
    )

    response = client.get("/admin/stats", headers=ADMIN)

    assert response.status_code == 200
    stats = response.json()
    assert stats["total_tasks"] == 4
    assert stats["by_status"]["todo"] == 2
    assert stats["by_status"]["in_progress"] == 1
    assert stats["by_status"]["done"] == 1


def test_user_cannot_delete_foreign_task(client: TestClient) -> None:
    task = _create_task(client, USER_10)

    response = client.delete(f"/tasks/{task['id']}", headers=USER_20)

    assert response.status_code == 404


def test_admin_can_delete_foreign_task(client: TestClient) -> None:
    task = _create_task(client, USER_10)

    response = client.delete(f"/admin/tasks/{task['id']}", headers=ADMIN)

    assert response.status_code == 204
    assert client.get(f"/tasks/{task['id']}", headers=USER_10).status_code == 404


def test_openapi_routes_grouped_by_tags(client: TestClient) -> None:
    openapi = client.get("/openapi.json").json()

    assert openapi["paths"]["/tasks"]["post"]["tags"] == ["tasks"]
    assert openapi["paths"]["/users/me"]["get"]["tags"] == ["users"]
    assert openapi["paths"]["/admin/stats"]["get"]["tags"] == ["admin"]
