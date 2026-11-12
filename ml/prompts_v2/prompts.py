# Промпты для baseline-модели (версия 2)

def prompt_summarize_v1(game_id: str, store_text: str) -> str:
    """Старый промпт из лабы 3."""
    return f'Опиши игру в 3-4 предложениях. Описание: {store_text}. Верни JSON: {{"game_id": "{game_id}", "narrative": "текст"}}'

def prompt_summarize_v2(game_id: str, store_text: str) -> str:
    """Новый промпт с жесткими ограничениями."""
    return f"""Ты — аналитик мобильных игр.
Твоя задача: написать краткое описание сути игры в 3-4 предложениях.
ПРАВИЛА:
1. Отвечай СТРОГО на русском языке. Никаких английских слов.
2. Не выдумывай факты, которых нет в описании.
3. Верни ответ ТОЛЬКО в формате JSON, без markdown-разметки (без ```json).
Формат: {{"game_id": "{game_id}", "narrative": "твой текст"}}

Описание из стора: {store_text}"""

def prompt_classify_v1(game_id: str, metrics_4w: list) -> str:
    """Старый промпт из лабы 3."""
    return f'Определи категорию (green, yellow, red, turquoise) по метрикам: {metrics_4w}. Верни JSON: {{"game_id": "{game_id}", "category": "green"}}'

def prompt_classify_v2(game_id: str, metrics_4w: list) -> str:
    """Новый промпт для классификации."""
    return f"""Ты — продуктовый аналитик.
Определи категорию игры по метрикам gross за 4 недели.
Категории: green (рост), yellow (стагнация/всплеск), red (падение), turquoise (похож на наш проект).
ПРАВИЛА:
1. Ответ должен быть СТРОГО одним словом из списка: green, yellow, red, turquoise.
2. Никаких объяснений.
3. Верни ответ ТОЛЬКО в формате JSON, без markdown.
Формат: {{"game_id": "{game_id}", "category": "твоя_категория"}}

Метрики (gross_usd): {metrics_4w}"""
