# Дизайн AI-пайплайна

**Роль:** AI Engineer
**Спринт:** Lab2 — Design
**Дата:** 2026-10-15
**Связанные документы:** [research.md](./research.md), [model-candidates.md](./model-candidates.md)

---

## 1. Общая архитектура

Пайплайн — агентная сборка из четырёх последовательных шагов. Прямые промпты не подходят, потому что задача требует оркестрации (сбор → суммаризация → классификация → сборка). RAG не подходит, потому что нет базы знаний — данные приходят из внешнего API.

### Схема пайплайна (PlantUML)

```plantuml
@startuml
!theme plain
skinparam componentStyle rectangle

actor "Аналитик" as User
participant "Оркестратор\n(агент)" as Orchestrator
database "SensorTower /\nAppMagic API" as DataSource
participant "Gemini 3.1 Pro\n(суммаризация)" as LLM
participant "Cotype-Nano\n(классификация)" as Classifier
database "Векторная БД\n(Qdrant)" as VectorDB
participant "Валидатор" as Validator
participant "Рендер" as Renderer

User -> Orchestrator: Запрос на дайджест
activate Orchestrator

group Шаг 1. Сбор данных
    Orchestrator -> DataSource: Запрос метрик
    alt API доступен
        DataSource --> Orchestrator: gross, installs, geo
    else API недоступен (503)
        Orchestrator --> User: Ошибка: источник данных недоступен
        note right: Эскалация: уведомить аналитика
    end
end

group Шаг 2. Суммаризация
    Orchestrator -> LLM: Промпт
    LLM --> Orchestrator: Описание
    note right of Orchestrator: Контроль К1: галлюцинации
    alt К1 пройден
        Orchestrator -> Orchestrator: Принять описание
    else К1 не пройден
        loop Retry до 2 раз
            Orchestrator -> LLM: Повторный запрос
            LLM --> Orchestrator: Новое описание
        end
        alt Retry не помог
            Orchestrator --> User: Эскалация: ручная проверка
        end
    end
end

group Шаг 3. Классификация
    Orchestrator -> Classifier: Промпт
    Classifier --> Orchestrator: Категория
    note right of Orchestrator: Контроль К2: ложные "зелёные"
    alt К2 пройден
        Orchestrator -> Orchestrator: Принять категорию
    else К2 не пройден
        Orchestrator -> Orchestrator: Понизить до "жёлтой"
        note right: Пометка для ручной проверки
    end
end

group Шаг 4-5. Similarity и валидация
    Orchestrator -> VectorDB: Поиск похожих
    VectorDB --> Orchestrator: Список
    Orchestrator -> Validator: Проверка цифр
    alt К3 пройден
        Validator --> Orchestrator: OK
    else К3 не пройден
        Validator --> Orchestrator: Расхождение >5%
        Orchestrator --> User: Блокировка публикации
        note right: Эскалация: аналитик проверяет данные
    end
end

Orchestrator -> Renderer: Сборка карточек
Renderer --> Orchestrator: Изображение
Orchestrator --> User: Готовый дайджест
deactivate Orchestrator

note over Orchestrator
    Логирование Л1-Л5 на всех шагах
end note
@enduml
```

Схему можно отрендерить на [plantuml.com/plantuml](https://www.plantuml.com/plantuml/uml/).

---

## 2. Точки контроля качества

| ID | Где | Что проверяем | При провале |
|---|---|---|---|
| К1 | После суммаризации | Галлюцинации, путаница с похожими играми | Retry до 2 раз, затем эскалация аналитику |
| К2 | После классификации | Ложные «зелёные» на случайных всплесках | Понизить категорию, пометить для ручной проверки |
| К3 | Перед публикацией | Соответствие gross/installs первоисточнику | Блокировка публикации, эскалация при расхождении >5% |
| К4 | Финал | Соответствие структуры карточки шаблону | Отклонить, пересобрать |

---

## 3. Точки логирования

| ID | Когда | Что пишем |
|---|---|---|
| Л1 | Начало пайплайна | request_id, timestamp, список игр, источник данных |
| Л2 | Финал пайплайна | request_id, latency по шагам, стоимость, статус |
| Л3 | Каждый вызов модели | модель, input/output tokens, стоимость, latency |
| Л4 | Провал контроля качества | ID контроля (К1–К4), причина, input/output |
| Л5 | Retry | номер попытки, причина, результат |

Формат — JSON-строки, по одной на событие.

---

## 4. Границы контекста

### Что модель видит

**Суммаризация:** название, разработчик, дата релиза, платформы, описание из стора, промо-материалы, жанр, метрики gross/installs.

**Классификация:** метрики за 4 недели, geo-разбивка, категория из предыдущего дайджеста, описание нарратива из шага 2.

### Что модель НЕ видит

- Внутренние данные студии (метрики своих продуктов, юнит-экономика).
- Персональные данные (имена аналитиков, комментарии из чатов).
- Чужие дайджесты и внутренние документы конкурентов.
- Сырые логи и метаданные API (токены, URL с параметрами).
- Исторические дайджесты за прошлые периоды.

---

## 5. Что дальше

- **ADR выбора моделей** — [model-candidates.md, раздел «Решение»](./model-candidates.md).
- **Спайки** — [spikes/lab2.md](./spikes/lab2.md).
- **Контракт API** — [api/openapi.yaml](./api/openapi.yaml).

---

## 6. ERD: хранилище дайджестов

Схема описывает, где хранятся данные для `GET /digest/{digest_id}`.

```mermaid
erDiagram
    DIGEST ||--o{ GAME_CARD : contains
    DIGEST ||--|| DIGEST_META : has
    GAME_CARD ||--|| GAME_METRICS : has
    GAME_CARD ||--o| VALIDATION_STATUS : has
    GAME_CARD ||--o{ SIMILAR_PROJECT : has

    DIGEST {
        string digest_id PK
        string period
        timestamp created_at
        string status
    }
    GAME_CARD {
        string game_id PK
        string digest_id FK
        string name
        string developer
        string narrative
        string category
        date release_date
    }
    GAME_METRICS {
        string game_id PK
        float gross_usd
        int installs
        json geo_breakdown
    }
    VALIDATION_STATUS {
        string game_id PK
        boolean passed
        json checks
    }
    SIMILAR_PROJECT {
        string game_id FK
        string similar_game_id FK
    }
    DIGEST_META {
        string digest_id PK
        int latency_ms
        float cost_usd
        json models_used
        json steps_latency
    }
```

Таблицы соответствуют схемам из `api/openapi.yaml`.
