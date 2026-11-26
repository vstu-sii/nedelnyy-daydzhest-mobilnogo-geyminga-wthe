"""Проверки контракта ответов AI.

Запуск:
python -m unittest discover -s evals -p "test_*.py" -v
"""

import json
import unittest

from ml.validation import (
    OutputValidationError,
    validate_output,
)


class ValidationTests(unittest.TestCase):
    def test_valid_summary(self):
        response = json.dumps(
            {
                "game_id": "game_01",
                "narrative": "Игрок выращивает сад.",
            },
            ensure_ascii=False,
        )

        result = validate_output(
            response,
            expected_game_id="game_01",
            task="summarize",
            finish_reason="stop",
        )

        self.assertEqual(
            result["narrative"],
            "Игрок выращивает сад.",
        )

    def test_valid_classification(self):
        response = '{"game_id":"game_01","category":"yellow"}'

        result = validate_output(
            response,
            expected_game_id="game_01",
            task="classify",
            finish_reason="stop",
        )

        self.assertEqual(result["category"], "yellow")

    def test_rejects_invalid_classifications(self):
        responses = [
            # Markdown вместо чистого JSON.
            '```json\n'
            '{"game_id":"game_01","category":"green"}'
            '\n```',

            # Составная категория из неудачного промпта Lab 5.
            '{"game_id":"game_01","category":"green|yellow"}',

            # Чужой идентификатор.
            '{"game_id":"other_game","category":"green"}',

            # Дополнительное поле.
            '{"game_id":"game_01","category":"green","score":1}',

            # Неверный тип категории.
            '{"game_id":"game_01","category":["green"]}',

            # JSON-массив вместо объекта.
            '["game_01","green"]',

            # Пояснение вместо JSON.
            'Категория игры: green',
        ]

        for response in responses:
            with self.subTest(response=response):
                with self.assertRaises(OutputValidationError):
                    validate_output(
                        response,
                        expected_game_id="game_01",
                        task="classify",
                        finish_reason="stop",
                    )

    def test_rejects_invalid_summaries(self):
        responses = [
            '{"game_id":"game_01","narrative":""}',
            '{"game_id":"game_01","narrative":"   "}',
            '{"game_id":"game_01","narrative":null}',
            '{"game_id":"game_01","narrative":42}',
            '{"game_id":"other_game","narrative":"Описание."}',
            '{"game_id":"game_01"}',
        ]

        for response in responses:
            with self.subTest(response=response):
                with self.assertRaises(OutputValidationError):
                    validate_output(
                        response,
                        expected_game_id="game_01",
                        task="summarize",
                        finish_reason="stop",
                    )

    def test_rejects_truncated_generation(self):
        response = '{"game_id":"game_01","category":"green"}'

        with self.assertRaises(OutputValidationError):
            validate_output(
                response,
                expected_game_id="game_01",
                task="classify",
                finish_reason="length",
            )

    def test_rejects_unknown_task(self):
        with self.assertRaises(ValueError):
            validate_output(
                "{}",
                expected_game_id="game_01",
                task="unknown",
                finish_reason="stop",
            )


if __name__ == "__main__":
    unittest.main()
