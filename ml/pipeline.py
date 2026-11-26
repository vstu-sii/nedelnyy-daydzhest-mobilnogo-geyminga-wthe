"""Финальный AI-пайплайн Lab 5.

Числовой тренд определяется правилами.
Описание создаётся внешним генератором и проверяется по контракту.
Карточка требует ручной проверки фактов перед публикацией.
"""

from collections.abc import Callable, Sequence
from typing import Any

from ml.classification import classify_trend
from ml.validation import validate_output


def build_game_card(
    game_id: str,
    store_description: str,
    metrics_4w: Sequence[float],
    generate_summary: Callable[[str, str], dict[str, Any]],
) -> dict[str, Any]:
    """Сформировать черновик карточки игры.

    generate_summary(game_id, store_description) должен вернуть:
    {
        "response": "JSON-ответ модели",
        "finish_reason": "stop"
    }

    Допускаются дополнительные метаданные генерации, например
    latency_s, prompt_tokens и completion_tokens.

    Ошибки входа, генерации или валидации передаются вызывающему
    коду. Непроверенная карточка не подменяется успешным результатом.
    """
    if not isinstance(game_id, str) or not game_id.strip():
        raise ValueError("game_id должен быть непустой строкой")

    if (
        not isinstance(store_description, str)
        or not store_description.strip()
    ):
        raise ValueError(
            "store_description должен быть непустой строкой"
        )

    # Некорректные метрики отклоняются до вызова модели.
    category = classify_trend(metrics_4w)

    generation = generate_summary(game_id, store_description)

    if not isinstance(generation, dict):
        raise ValueError(
            "Генератор должен вернуть словарь с результатом"
        )

    summary = validate_output(
        response=generation.get("response"),
        expected_game_id=game_id,
        task="summarize",
        finish_reason=generation.get("finish_reason"),
    )

    metadata_fields = (
        "latency_s",
        "prompt_tokens",
        "completion_tokens",
        "model",
    )

    return {
        "game_id": game_id,
        "narrative": summary["narrative"],
        "category": category,
        "classification_method": "rules-v1",
        "review_required": True,
        "publication_status": "draft",
        "generation_metadata": {
            field: generation[field]
            for field in metadata_fields
            if field in generation
        },
    }
