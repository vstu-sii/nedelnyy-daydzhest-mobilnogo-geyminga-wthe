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

### Запуск базового окружения

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

## Dev-среда

Для разработки используется отдельная конфигурация Docker Compose — `docker-compose.dev.yml`.

Особенности Dev-среды:

- `APP_ENV=development`.
- Автоматическая перезагрузка API при изменении кода (`--reload`).
- Исходный код backend подключён как volume.
- Отдельная база данных `dev-postgres-data`.
- Отдельная Docker-сеть.
- Веб-интерфейс доступен на порту `8082`.
- API доступен на порту `8000`.
- PostgreSQL доступен на порту `5433`.

Создать файл `.env.dev`:

```env
WEB_PORT=8082
APP_ENV=development
```

Запуск Dev:

```bash
docker compose -p digest-dev --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

Проверка:

- Web: http://localhost:8082
- API: http://localhost:8000/api/health
- Документация API: http://localhost:8000/docs

Остановка Dev:

```bash
docker compose -p digest-dev --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml down
```

## Staging-среда

Staging использует ту же базовую конфигурацию, что и Production, но отдельные Docker-образы, базу данных, сеть и настройки.

Особенности Staging:

- `APP_ENV=staging`.
- Используются опубликованные Docker-образы с тегом `lab4-test`.
- Отдельная база данных `staging-postgres-data`.
- Отдельная Docker-сеть `digest-staging-network`.
- Веб-интерфейс доступен на порту `8081`.
- API доступен внутри Docker-сети на порту `8000`.
- Worker запускается отдельно от Dev.

Создать файл `.env.staging`:

```env
IMAGE_TAG=lab4-test
STAGING_DB_PASSWORD=your_strong_password
```

Вместо `your_strong_password` необходимо указать надёжный пароль.

Запуск Staging:

```bash
docker compose -p digest-staging --env-file .env.staging -f docker-compose.yml -f docker-compose.staging.yml up -d
```

Проверка:

- Web: http://localhost:8081
- API проверяется внутри контейнера:

```bash
docker exec digest-staging-api python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/api/health').read().decode())"
```

Остановка Staging:

```bash
docker compose -p digest-staging --env-file .env.staging -f docker-compose.yml -f docker-compose.staging.yml down
```

Для сохранения данных PostgreSQL не использовать `down -v`.

## Production-среда

Production использует отдельную конфигурацию `docker-compose.prod.yml`.

Особенности:

- `APP_ENV=production`.
- Используются опубликованные Docker-образы с тегом `latest` по умолчанию.
- Отдельная база данных `prod-postgres-data`.
- Отдельная Docker-сеть `digest-prod-network`.
- Веб-интерфейс использует порт `8080`.
- API доступен внутри Docker-сети на порту `8000`.
- Настройки и пароль базы данных задаются через `.env.production`.

Создать файл `.env.production` на основе параметров Production-конфигурации. Файл должен содержать необходимые переменные окружения, включая `PROD_DB_PASSWORD`.

Запуск Production:

```bash
docker compose -p digest-prod --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Остановка Production:

```bash
docker compose -p digest-prod --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml down
```

Production-запуск и автоматическое развёртывание на сервере требуют настроенного Production-сервера.

## Различия окружений

| Параметр | Dev | Staging | Production |
|---|---|---|---|
| APP_ENV | development | staging | production |
| Образы | Локальная сборка | lab4-test | latest |
| Web-порт | 8082 | 8081 | 8080 |
| API | localhost:8000 | Внутри Docker | Внутри Docker |
| PostgreSQL | localhost:5433 | Внутри Docker | Внутри Docker |
| Volume БД | dev-postgres-data | staging-postgres-data | prod-postgres-data |
| Назначение | Разработка | Тестирование | Рабочее окружение |

## Ручное применение миграций

Если база данных уже создана и миграции ещё не применялись:

```bash
make migrate
```

Команда предназначена для первоначального применения миграций. Повторный запуск может привести к ошибкам из-за существующих таблиц.

## Проверка приложения

Для проверки генерации дайджеста отправить POST-запрос на `/api/generate` с JSON-полем `topic`.

Результаты генерации сохраняются в таблице `model_results`.

## Остановка базового окружения

```bash
docker compose -f docker-compose.yml down
```

Для сохранения данных PostgreSQL не использовать `down -v`.

## Безопасность

- Файлы `.env`, `.env.dev`, `.env.staging` и `.env.production` не должны попадать в Git.
- Не хранить пароли и токены непосредственно в исходном коде.
- Для каждого окружения использовать отдельные настройки и надёжные пароли.