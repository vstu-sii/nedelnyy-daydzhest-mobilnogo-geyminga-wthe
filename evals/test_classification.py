"""Проверки детерминированного классификатора Lab 5.

Запуск из корня проекта:
python -m unittest discover -s evals -p "test_*.py" -v
"""

import json
import unittest
from pathlib import Path

from ml.classification import classify_trend


ROOT = Path(__file__).resolve().parents[1]


class ClassificationTests(unittest.TestCase):
    def test_fixed_dataset(self):
        dataset = json.loads(
            (ROOT / "evals" / "dataset.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(len(dataset), 12)

        for game in dataset:
            with self.subTest(game_id=game["game_id"]):
                self.assertEqual(
                    classify_trend(game["metrics_4w"]),
                    game["expected_category"],
                )

    def test_exact_growth_threshold(self):
        self.assertEqual(
            classify_trend([100, 105, 110, 115]),
            "green",
        )

    def test_exact_decline_threshold(self):
        self.assertEqual(
            classify_trend([100, 95, 90, 85]),
            "red",
        )

    def test_plateau_is_yellow(self):
        self.assertEqual(
            classify_trend([100, 100, 120, 130]),
            "yellow",
        )

    def test_invalid_inputs(self):
        invalid_cases = [
            [],
            [100, 110, 120],
            [100, 110, 120, 130, 140],
            [0, 10, 20, 30],
            [100, -10, 120, 130],
            [100, float("nan"), 120, 130],
            [100, float("inf"), 120, 130],
            [100, True, 120, 130],
            [100, "110", 120, 130],
        ]

        for values in invalid_cases:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    classify_trend(values)


if __name__ == "__main__":
    unittest.main()
