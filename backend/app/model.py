
import os


# Модели, разрешённые политикой приложения.
ALLOWED_MODELS = frozenset({
    "local-demo-model",
})

DEFAULT_MODEL = "local-demo-model"


def get_model_name() -> str:
    """Проверяет, разрешена ли выбранная модель."""

    requested_model = os.getenv(
        "MODEL_NAME",
        DEFAULT_MODEL,
    ).strip()

    if requested_model not in ALLOWED_MODELS:
        raise ValueError(
            f"Модель '{requested_model}' запрещена. "
            f"Разрешённые модели: "
            f"{', '.join(sorted(ALLOWED_MODELS))}"
        )

    return requested_model


def generate_digest(topic: str) -> dict:
    """Создаёт демонстрационный игровой дайджест."""

    topic = topic.strip() or "мобильный гейминг"

    model_name = get_model_name()

    return {
        "model_name": model_name,
        "summary": (
            f"Демонстрационный дайджест по теме «{topic}». "
            "В мобильном гейминге продолжают развиваться "
            "игровые механики, обновления и соревновательные события."
        ),
        "highlights": [
            f"Новости и тенденции по теме: {topic}",
            "Новые игровые обновления и возможности",
            "Предстоящие события мобильного гейминга",
        ],
    }
