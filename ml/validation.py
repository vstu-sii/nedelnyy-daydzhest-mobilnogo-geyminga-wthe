"""Проверка контракта ответов AI перед использованием в карточке.

Проверка структуры не гарантирует фактическую точность текста.
Содержание описания требует отдельной сверки с источником.
"""

import json
from typing import Any


CATEGORIES = {"green", "yellow", "red", "turquoise"}


class OutputValidationError(ValueError):
    """Ответ модели не соответствует контракту."""


def validate_output(
    response: str,
    expected_game_id: str,
    task: str,
    finish_reason: str,
) -> dict[str, Any]:
    """Разобрать и проверить ответ без автоматического исправления.

    task: summarize или classify.
    Возвращает проверенный объект.
    При нарушении контракта вызывает OutputValidationError.
    """
    if task not in {"summarize", "classify"}:
        raise ValueError("Неизвестная задача")

    if finish_reason != "stop":
        raise OutputValidationError(
            "Генерация не завершена штатно"
        )

    if not isinstance(response, str):
        raise OutputValidationError(
            "Ответ должен быть строкой"
        )

    try:
        data = json.loads(response)
    except json.JSONDecodeError as error:
        raise OutputValidationError(
            "Ответ не является корректным JSON"
        ) from error

    if not isinstance(data, dict):
        raise OutputValidationError(
            "Корень JSON должен быть объектом"
        )

    value_field = (
        "narrative" if task == "summarize" else "category"
    )
    expected_fields = {"game_id", value_field}

    if set(data) != expected_fields:
        raise OutputValidationError(
            f"Ожидаются только поля: {sorted(expected_fields)}"
        )

    if data["game_id"] != expected_game_id:
        raise OutputValidationError(
            "game_id ответа не совпадает с исходным"
        )

    if task == "summarize":
        narrative = data["narrative"]

        if not isinstance(narrative, str) or not narrative.strip():
            raise OutputValidationError(
                "narrative должен быть непустой строкой"
            )

    else:
        category = data["category"]

        if (
            not isinstance(category, str)
            or category not in CATEGORIES
        ):
            raise OutputValidationError(
                "category должна содержать одну допустимую категорию"
            )

    return data
