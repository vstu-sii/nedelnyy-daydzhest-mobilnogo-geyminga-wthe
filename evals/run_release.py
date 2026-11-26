"""Полный прогон финального AI-пайплайна.

Запуск из корня проекта:
python -m evals.run_release --tag lab5-ai-v1 --gpu-hour-usd 0

Тариф 0 допустим для фактически бесплатной сессии Colab.
Он не является оценкой платного размещения.
"""

import argparse
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

from ml.pipeline import build_game_card
from ml.qwen_generator import QwenSummaryGenerator


ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
REVISION = "aa8e72537993ba99e69dfaafa59ed015b17504d1"


def git(*args):
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        text=True,
    ).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--gpu-hour-usd", type=float, required=True)
    args = parser.parse_args()

    if args.gpu_hour_usd < 0:
        raise ValueError("Тариф не может быть отрицательным")

    commit = git("rev-parse", "HEAD")
    tag_commit = git("rev-list", "-n", "1", args.tag)

    if commit != tag_commit:
        raise RuntimeError("HEAD не соответствует указанному тегу")

    if git("status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("Отслеживаемые файлы изменены")

    if not torch.cuda.is_available():
        raise RuntimeError("Нужна среда с GPU")

    dataset_path = ROOT / "evals/dataset.json"
    dataset = json.loads(
        dataset_path.read_text(encoding="utf-8")
    )

    session_started = time.perf_counter()

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID, revision=REVISION
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=REVISION,
        torch_dtype=torch.float16,
        device_map={"": 0},
    )
    generator = QwenSummaryGenerator(model, tokenizer)

    # Прогрев входит в общее время сессии,
    # но не в измерение сценария обработки 12 игр.
    generator("warmup", "Игра про выращивание сада.")

    scenario_started = time.perf_counter()
    rows = []

    for game in dataset:
        started = time.perf_counter()

        try:
            card = build_game_card(
                game_id=game["game_id"],
                store_description=game["store_description"],
                metrics_4w=game["metrics_4w"],
                generate_summary=generator,
            )
            row = {
                "game_id": game["game_id"],
                "status": "success",
                "expected_category": game["expected_category"],
                "category_correct": (
                    card["category"] == game["expected_category"]
                ),
                "card": card,
            }
        except Exception as error:
            row = {
                "game_id": game["game_id"],
                "status": "error",
                "category_correct": False,
                "error": str(error),
            }

        row["end_to_end_latency_s"] = (
            time.perf_counter() - started
        )
        rows.append(row)

        print(
            game["game_id"],
            row["status"],
            f"{row['end_to_end_latency_s']:.3f} с",
            flush=True,
        )

    scenario_seconds = time.perf_counter() - scenario_started
    session_seconds = time.perf_counter() - session_started
    successful = [r for r in rows if r["status"] == "success"]

    report = {
        "release_tag": args.tag,
        "commit": commit,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL_ID,
        "model_revision": REVISION,
        "gpu": torch.cuda.get_device_name(0),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "dataset_sha256": hashlib.sha256(
            dataset_path.read_bytes()
        ).hexdigest(),
        "cases": len(rows),
        "successful_cards": len(successful),
        "valid_card_rate": len(successful) / len(rows),
        "classification_accuracy": (
            sum(r["category_correct"] for r in rows) / len(rows)
        ),
        "scenario_seconds": scenario_seconds,
        "mean_end_to_end_latency_s": (
            sum(r["end_to_end_latency_s"] for r in rows)
            / len(rows)
        ),
        "session_seconds_including_load_and_warmup": session_seconds,
        "api_cost_usd": 0,
        "gpu_hour_usd": args.gpu_hour_usd,
        "scenario_compute_cost_usd": (
            scenario_seconds / 3600 * args.gpu_hour_usd
        ),
        "session_compute_cost_usd": (
            session_seconds / 3600 * args.gpu_hour_usd
        ),
        "cost_scope": (
            "GPU-вычисления по указанному тарифу; "
            "сопровождение, хранение и редактура не включены."
        ),
        "quality_scope": (
            "Категории проверены по политике команды. "
            "Валидность карточки не доказывает точность описания."
        ),
        "rows": rows,
    }

    output = ROOT / "release-results.json"
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("\nРезультат сохранён:", output)


if __name__ == "__main__":
    main()
