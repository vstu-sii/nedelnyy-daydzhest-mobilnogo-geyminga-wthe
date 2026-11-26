"""Интеграционные проверки пайплайна без загрузки модели.

Запуск:
python -m unittest discover -s evals -p "test_*.py" -v
"""

import json
import unittest

from ml.pipeline import build_game_card
from ml.validation import OutputValidationError


class PipelineTests(unittest.TestCase):
    def test_builds_draft_card(self):
        def generator(game_id, description):
            return {
                "response": json.dumps(
                    {
                        "game_id": game_id,
                        "narrative": description,
                    },
                    ensure_ascii=False,
                ),
                "finish_reason": "stop",
                "latency_s": 1.5,
                "prompt_tokens": 100,
                "completion_tokens": 20,
                "model": "test-generator",
            }

        card = build_game_card(
            game_id="so_003",
            store_description="Игрок выращивает сад.",
            metrics_4w=[100, 95, 90, 200],
            generate_summary=generator,
        )

        self.assertEqual(card["game_id"], "so_003")
        self.assertEqual(card["category"], "yellow")
        self.assertEqual(
            card["narrative"], "Игрок выращивает сад."
        )
        self.assertEqual(
            card["classification_method"], "rules-v1"
        )
        self.assertTrue(card["review_required"])
        self.assertEqual(card["publication_status"], "draft")
        self.assertEqual(
            card["generation_metadata"]["latency_s"], 1.5
        )

    def test_invalid_metrics_do_not_call_generator(self):
        calls = []

        def generator(game_id, description):
            calls.append(game_id)
            raise AssertionError("Генератор не должен вызываться")

        with self.assertRaises(ValueError):
            build_game_card(
                game_id="game_01",
                store_description="Описание игры.",
                metrics_4w=[100, -10, 120, 130],
                generate_summary=generator,
            )

        self.assertEqual(calls, [])

    def test_wrong_game_id_blocks_card(self):
        def generator(game_id, description):
            return {
                "response": (
                    '{"game_id":"other_game",'
                    '"narrative":"Описание."}'
                ),
                "finish_reason": "stop",
            }

        with self.assertRaises(OutputValidationError):
            build_game_card(
                game_id="game_01",
                store_description="Описание игры.",
                metrics_4w=[100, 120, 140, 160],
                generate_summary=generator,
            )

    def test_truncated_output_blocks_card(self):
        def generator(game_id, description):
            return {
                "response": json.dumps(
                    {
                        "game_id": game_id,
                        "narrative": "Описание.",
                    },
                    ensure_ascii=False,
                ),
                "finish_reason": "length",
            }

        with self.assertRaises(OutputValidationError):
            build_game_card(
                game_id="game_01",
                store_description="Описание игры.",
                metrics_4w=[100, 120, 140, 160],
                generate_summary=generator,
            )

    def test_model_failure_is_not_hidden(self):
        def generator(game_id, description):
            raise RuntimeError("Модель недоступна")

        with self.assertRaisesRegex(
            RuntimeError, "Модель недоступна"
        ):
            build_game_card(
                game_id="game_01",
                store_description="Описание игры.",
                metrics_4w=[100, 120, 140, 160],
                generate_summary=generator,
            )

    def test_empty_input_is_rejected(self):
        for game_id, description in [
            ("", "Описание игры."),
            ("game_01", "   "),
        ]:
            with self.subTest(
                game_id=game_id, description=description
            ):
                with self.assertRaises(ValueError):
                    build_game_card(
                        game_id=game_id,
                        store_description=description,
                        metrics_4w=[100, 120, 140, 160],
                        generate_summary=lambda *_: {},
                    )


if __name__ == "__main__":
    unittest.main()
