
# Недельный дайджест мобильного гейминга
[![CI](https://github.com/vstu-sii/nedelnyy-daydzhest-mobilnogo-geyminga-wthe/actions/workflows/ci.yml/badge.svg)](https://github.com/vstu-sii/nedelnyy-daydzhest-mobilnogo-geyminga-wthe/actions/workflows/ci.yml)
## Что это

Проект еженедельного дайджеста новостей и событий мобильного гейминга.

## Команда

- попов666
- санек легкий лагер
- илюха не мажик
- чувилини

## Локальный запуск

### Требования

- Git
- Docker Desktop
- Docker Compose

### Запуск

1. Клонировать репозиторий.
2. Перейти в директорию проекта.
3. Создать `.env` из `.env.example`.
4. Запустить приложение:

```bash
docker compose -f docker-compose.yml up -d --build
```

При первом запуске PostgreSQL автоматически выполняет SQL-скрипты из `database/migrations`, подключённые в `docker-compose.yml`:

- `002_postgresql_schema.sql` — создание таблиц и индексов.
- `003_seed_demo_data.sql` — добавление демонстрационных данных.

Скрипты выполняются только при первоначальной инициализации пустого PostgreSQL volume.

### Ручное применение миграций

Если база данных уже создана и миграции ещё не применялись:

```bash
make migrate
```

Команда предназначена для первоначального применения миграций. Повторный запуск может привести к ошибкам из-за существующих таблиц.

### Проверка

- Веб-интерфейс: http://localhost:8080
- API: http://localhost:8080/api/health
- Документация API: http://localhost:8080/docs

Для проверки генерации дайджеста отправить POST-запрос на `/api/generate` с JSON-полем `topic`.

Результаты генерации сохраняются в таблице `model_results`.

### Остановка

```bash
docker compose -f docker-compose.yml down
```

Для сохранения данных PostgreSQL не использовать `down -v`.