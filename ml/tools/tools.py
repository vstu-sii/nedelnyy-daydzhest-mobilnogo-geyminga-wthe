import json
import time

def get_game_metrics(game_id: str, timeout_sec: float = 5.0) -> dict:
    """
    Инструмент: получение метрик игры.
    ПРАВА: Доступ только на чтение (read-only) для таблицы games. Нет доступа к удалению или изменению.
    Контракт:
    - Принимает: game_id (str)
    - Возвращает: dict с метриками или ошибку.
    - Таймаут: если запрос дольше timeout_sec, возвращает ошибку.
    """
    start_time = time.time()
    
    if not isinstance(game_id, str) or len(game_id) > 50:
        return {"error": "Invalid game_id format"}

    # Имитация сложного запроса к базе данных
    time.sleep(0.2) 

    # Проверка таймаута (теперь она может сработать, если timeout_sec будет меньше 0.2)
    if time.time() - start_time > timeout_sec:
        return {"error": "Database timeout"}

    return {
        "game_id": game_id,
        "gross_usd": 1000000.0,
        "installs": 500000,
        "status": "success"
    }

def handle_tool_call(tool_call):
    """
    Обработка вызова инструмента моделью.
    Если инструмент вернул ошибку, модель должна корректно это принять.
    """
    try:
        args = json.loads(tool_call.function.arguments)
        # Вызов с маленьким таймаутом для демонстрации
        result = get_game_metrics(args.get("game_id"), timeout_sec=0.1) 
        
        if "error" in result:
            print(f"[TOOL ERROR] {result['error']}")
            return f"Ошибка инструмента: {result['error']}"
            
        return json.dumps(result)
    except Exception as e:
        return f"Ошибка вызова инструмента: {e}"

# Схема для LLM (Function Calling)
TOOL_SCHEMA = {
    "name": "get_game_metrics",
    "description": "Получить метрики (выручку и установки) игры по её ID. Только чтение.",
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
