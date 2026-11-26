"""Классификация тренда недельной выручки по правилам Lab 5."""

import math
from typing import Sequence


def classify_trend(values: Sequence[float]) -> str:
    """Определить категорию по четырём недельным значениям.

    green: строго последовательный рост и общий рост не менее 15%.
    red: строго последовательное падение и общее падение не менее 15%.
    yellow: остальные случаи, включая разовые всплески.

    Категория turquoise здесь не определяется:
    для неё нужны сведения о сходстве с собственным проектом.
    """
    if len(values) != 4:
        raise ValueError("Нужны ровно четыре недельных значения")

    for value in values:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError(
                "Значения должны быть конечными неотрицательными числами"
            )

    first, last = values[0], values[-1]

    if first == 0:
        raise ValueError(
            "Первое значение должно быть больше нуля "
            "для расчёта относительного изменения"
        )

    increasing = all(
        current > previous
        for previous, current in zip(values, values[1:])
    )
    decreasing = all(
        current < previous
        for previous, current in zip(values, values[1:])
    )

    if increasing and last >= first * 1.15:
        return "green"

    if decreasing and last <= first * 0.85:
        return "red"

    return "yellow"
