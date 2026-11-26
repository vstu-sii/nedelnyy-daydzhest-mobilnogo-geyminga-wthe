"""Пересчёт метрик сохранённого эксперимента Qwen.

Запуск из корня проекта:
python evals/summarize_results.py

Вход:
docs/experiments/qwen/records.json
evals/dataset.json

Выход:
docs/experiments/qwen/summary.json
"""

import json
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "docs" / "experiments" / "qwen"
CATEGORIES = {"green", "yellow", "red", "turquoise"}


def parse_output(record):
    """Проверить формат ответа без исправления содержимого."""
    if record.get("finish_reason") != "stop":
        return None

    try:
        data = json.loads(record["response"])
    except (json.JSONDecodeError, TypeError, KeyError):
        return None

    if not isinstance(data, dict):
        return None

    if data.get("game_id") != record["game_id"]:
        return None

    if record["task"] == "classify":
        if set(data) != {"game_id", "category"}:
            return None
        category = data["category"]
        if not isinstance(category, str) or category not in CATEGORIES:
            return None

    elif record["task"] == "summarize":
        if set(data) != {"game_id", "narrative"}:
            return None
        if (
            not isinstance(data["narrative"], str)
            or not data["narrative"].strip()
        ):
            return None

    else:
        return None

    return data


def main():
    records = json.loads(
        (RESULTS_DIR / "records.json").read_text(encoding="utf-8")
    )
    dataset = json.loads(
        (ROOT / "evals" / "dataset.json").read_text(encoding="utf-8")
    )
    labels = {
        row["game_id"]: row["expected_category"]
        for row in dataset
    }

    expected_pairs = {
        ("classify", "lab3"),
        ("classify", "lab4"),
        ("classify", "final"),
        ("summarize", "lab4"),
        ("summarize", "final"),
        ("summarize", "without_grounding"),
    }
    expected_keys = {
        (task, variant, game_id)
        for task, variant in expected_pairs
        for game_id in labels
    }
    actual_keys = [
        (row["task"], row["variant"], row["game_id"])
        for row in records
    ]

    if len(actual_keys) != len(set(actual_keys)):
        raise ValueError("В records.json обнаружены дубли")

    if set(actual_keys) != expected_keys:
        missing = sorted(expected_keys - set(actual_keys))
        extra = sorted(set(actual_keys) - expected_keys)
        raise ValueError(
            f"Неполный или неожиданный состав результатов. "
            f"Отсутствуют: {missing}. Лишние: {extra}"
        )

    summaries = []

    for task, variant in sorted(expected_pairs):
        rows = [
            row for row in records
            if row["task"] == task and row["variant"] == variant
        ]

        valid_count = 0
        correct_count = 0
        errors = []

        for row in rows:
            parsed = parse_output(row)

            if parsed is None:
                errors.append({
                    "game_id": row["game_id"],
                    "reason": "invalid_output",
                })
                continue

            valid_count += 1

            if task == "classify":
                expected = labels[row["game_id"]]
                if parsed["category"] == expected:
                    correct_count += 1
                else:
                    errors.append({
                        "game_id": row["game_id"],
                        "reason": "wrong_category",
                        "expected": expected,
                        "predicted": parsed["category"],
                    })

        summary = {
            "task": task,
            "variant": variant,
            "cases": len(rows),
            "valid_outputs": valid_count,
            "valid_output_rate": valid_count / len(rows),
            "correct": (
                correct_count if task == "classify" else None
            ),
            "accuracy": (
                correct_count / len(rows)
                if task == "classify"
                else None
            ),
            "mean_latency_s": mean(
                row["latency_s"] for row in rows
            ),
            "mean_prompt_tokens": mean(
                row["prompt_tokens"] for row in rows
            ),
            "mean_completion_tokens": mean(
                row["completion_tokens"] for row in rows
            ),
            "api_cost_usd": sum(
                row["api_cost_usd"] for row in rows
            ),
            "errors": errors,
        }
        summaries.append(summary)

        print(
            f"{task:10} {variant:18} "
            f"valid={valid_count}/{len(rows)} "
            f"correct={summary['correct']} "
            f"latency={summary['mean_latency_s']:.3f}s"
        )

    output_path = RESULTS_DIR / "summary.json"
    output_path.write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\nПроверено ответов: {len(records)}")
    print("Метрики сохранены:", output_path.relative_to(ROOT))


if __name__ == "__main__":
    main()
