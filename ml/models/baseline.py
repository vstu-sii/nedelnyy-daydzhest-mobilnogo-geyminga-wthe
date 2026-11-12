import os
import json
import time
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

# --- Конфигурация ---
API_KEY = os.getenv("OPENROUTER_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY or "sk-placeholder",
)

MODEL_SUMMARIZE = "google/gemma-3-27b-it:free"
MODEL_CLASSIFY = "google/gemma-3-12b-it:free"

# --- Структуры данных (по контракту из лабы 2) ---
class SummaryOutput(BaseModel):
    game_id: str
    narrative: str = Field(description="Краткое описание игры")

class ClassificationOutput(BaseModel):
    game_id: str
    category: str = Field(description="green, yellow, red, turquoise")

# --- Логирование (Трассировка) ---
def _log_trace(step: str, model: str, input_len: int, latency: float, status: str):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "step": step,
        "model": model,
        "input_chars": input_len,
        "latency_s": round(latency, 2),
        "status": status
    }
    print(json.dumps(log_entry, ensure_ascii=False))

# --- Вызов LLM с ретраями ---
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _call_llm(model: str, prompt: str, step_name: str) -> str:
    if not API_KEY:
        raise ValueError("OPENROUTER_API_KEY не задан")

    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Модель вернула пустой ответ")
        
        _log_trace(step_name, model, len(prompt), time.time() - start_time, "success")
        return content
    except Exception as e:
        _log_trace(step_name, model, len(prompt), time.time() - start_time, f"error: {str(e)}")
        raise e

# --- Модель ---
class BaselineModel:
    
    def summarize(self, game_id: str, store_text: str) -> SummaryOutput:
        prompt = f"""Ты аналитик мобильных игр. Опиши суть игры в 3-4 предложениях на русском языке, без выдуманных деталей.
Описание из стора: {store_text}

Верни строго JSON: {{"game_id": "{game_id}", "narrative": "твой текст"}}"""
        
        try:
            raw = _call_llm(MODEL_SUMMARIZE, prompt, "summarize")
            data = json.loads(raw)
            return SummaryOutput(**data)
        except Exception:
            return SummaryOutput(game_id=game_id, narrative="Ошибка генерации описания")

    def classify(self, game_id: str, metrics_4w: List[float]) -> ClassificationOutput:
        prompt = f"""Определи категорию игры по метрикам за 4 недели.
Категории: green (рост), yellow (стагнация/всплеск), red (падение), turquoise (похож на наш проект).
Метрики (gross_usd): {metrics_4w}

Верни строго JSON: {{"game_id": "{game_id}", "category": "green|yellow|red|turquoise"}}"""
        
        try:
            raw = _call_llm(MODEL_CLASSIFY, prompt, "classify")
            data = json.loads(raw)
            if data.get("category") not in ["green", "yellow", "red", "turquoise"]:
                data["category"] = "yellow"
            return ClassificationOutput(**data)
        except Exception:
            return ClassificationOutput(game_id=game_id, category="yellow")
