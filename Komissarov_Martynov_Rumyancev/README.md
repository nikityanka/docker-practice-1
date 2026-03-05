# Game Leaderboard API (Вариант 9)

HTTP API для хранения и отображения топ-результатов игроков по разным играм.

## Стек
- **FastAPI** — фреймворк для HTTP API
- **PostgreSQL 16** — хранение очков
- **SQLAlchemy 2** — ORM
- **Docker + Docker Compose** — контейнеризация

## Запуск

```bash
docker compose up --build
```

API будет доступно на `http://localhost:5000`.

## Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/scores` | Добавить результат |
| GET | `/scores/top` | Топ игроков по игре |
| GET | `/scores/player/{name}` | Результаты конкретного игрока |

## Примеры запросов

```bash
# Добавить очки
curl -X POST http://localhost:5000/scores \
  -H "Content-Type: application/json" \
  -d '{"player":"madmax","game":"digdug","score":751300}'

# Топ-5 по игре digdug
curl "http://localhost:5000/scores/top?game=digdug&limit=5"

# Личные результаты игрока
curl http://localhost:5000/scores/player/madmax
```
