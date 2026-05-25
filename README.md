# 5kr TRSP.

## Локальный запуск

```bash
python -m venv .venv
```

Активация виртуального окружения:

- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
- **Windows (cmd):** `.venv\Scripts\activate.bat`
- **Linux/macOS:** `source .venv/bin/activate`

```bash
pip install -r requirements.txt
```

Запуск сервера (если `uvicorn` не в PATH, используйте модуль Python):

```bash
uvicorn app.main:app --reload
```

или:

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Тесты:

```bash
pytest
```

Документация API: http://127.0.0.1:8000/docs

## Docker

Требуется установленный [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/).

Сборка и запуск:

```bash
docker compose up --build
```

Проверка (пустой список задач):

```bash
curl http://localhost:8000/tasks -H "X-User-Id: 10"
```

**PowerShell (Windows):** команда `curl` там вызывает `Invoke-WebRequest`, а не настоящий curl. Используйте один из вариантов:

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/tasks -H "X-User-Id: 10"
```

Ожидаемый ответ для задач: `[]`

Проверка состояния:

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ в контейнере:

```json
{"status":"ok","env":"docker"}
```

## Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/health` | Проверка состояния (`env` из `APP_ENV`) |
| POST | `/tasks` | Создать задачу (201) |
| GET | `/tasks` | Список задач текущего пользователя |
| GET | `/tasks/{id}` | Одна задача |
| PATCH | `/tasks/{id}/status` | Изменить статус |
| DELETE | `/tasks/{id}` | Удалить задачу (204) |
| WS | `/ws/tasks` | WebSocket (заголовок `X-User-Id`) |
| WS | `/ws/rooms/{room_id}?username=alice` | Чат в комнате |
| GET | `/rooms/{room_id}/users` | Активные пользователи комнаты |

Авторизация задач: заголовок `X-User-Id` (например, `10`).

### WebSocket-чат

WebSocket (`ws://`) — постоянное двустороннее соединение с сервером (в отличие от HTTP, где каждый запрос открывается и закрывается).

Подключение: `ws://localhost:8000/ws/rooms/python?username=alice`

Проверка (сервер должен быть запущен):

```powershell
python -m pytest tests/test_websocket.py -v
```

Список пользователей в комнате (HTTP):

```powershell
Invoke-RestMethod http://localhost:8000/rooms/python/users
```

## Структура проекта

```
task-api/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── storage.py
│   ├── room_manager.py
│   ├── schemas/
│   └── routers/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── requirements.txt
```
