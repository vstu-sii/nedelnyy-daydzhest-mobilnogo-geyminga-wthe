import json
import time

def get_game_metrics(game_id: str, timeout_sec: float = 5.0) -> dict:
    """
    Инструмент: получение метрик игры из базы данных.
    Контракт:
    - Принимает: game_id (str)
    - Возвращает: dict с метриками (gross_usd, installs) или ошибку.
    - Таймаут: если база данных не отвечает дольше timeout_sec, возвращает ошибку.
    """
    start_time = time.time()
    
    # Имитация запроса к базе данных (в реальности был бы SQL или API)
    # Для безопасности мы проверяем, что game_id имеет правильный формат
    if not isinstance(game_id, str) or len(game_id) > 50:
        return {"error": "Invalid game_id format"}

    # Имитация задержки базы данных
    time.sleep(0.1)

    if time.time() - start_time > timeout_sec:
        return {"error": "Database timeout"}

    # В реальности здесь был бы запрос к БД.
    # Сейчас отдаем заглушку для примера.
    return {
        "game_id": game_id,
        "gross_usd": 1000000.0,
        "installs": 500000,
        "status": "success"
    }

# Пример того, как этот инструмент описывается для LLM (Function Calling)
TOOL_SCHEMA = {
    "name": "get_game_metrics",
    "description": "Получить метрики (выручку и установки) игры по её ID.",
    "parameters": {
        "type": "object",
        "properties": {
            "game_id": {
                "type": "string",
                "description": "Уникальный идентификатор игры (например, nr_002)"
            }
        },
        "required": ["game_id"]
    }
}
