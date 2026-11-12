import os
import json
import time
from typing import List
from pydantic import BaseModel, Field
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from ml.tracing.config import setup_tracing, log_to_dashboard
# Импортируем наши новые промпты
from ml.prompts_v2.prompts import prompt_summarize_v2, prompt_classify_v2

setup_tracing()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY", "sk-placeholder"),
)

MODEL_SUMMARIZE = "openrouter/free"
MODEL_CLASSIFY = "openrouter/free"

class SummaryOutput(BaseModel):
    game_id: str
    narrative: str

class ClassificationOutput(BaseModel):
    game_id: str
    category: str

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _call_llm(model: str, prompt: str, step_name: str) -> str:
    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        latency = round(time.time() - start_time, 2)
        
        usage = response.usage
        trace_data = {
            "step": step_name,
            "model": model,
            "latency_s": latency,
            "prompt": prompt,
            "response": content,
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
            "status": "success"
        }
        log_to_dashboard(trace_data)
        return content
    except Exception as e:
        latency = round(time.time() - start_time, 2)
        log_to_dashboard({"step": step_name, "status": f"error: {e}", "latency_s": latency})
        raise e

class BaselineModel:
    def __init__(self):
        self._cache = {}

    def summarize(self, game_id: str, store_text: str) -> SummaryOutput:
        cache_key = f"sum_{game_id}_{hash(store_text)}"
        if cache_key in self._cache:
            print(f"[CACHE HIT] summarize для {game_id}")
            return self._cache[cache_key]

        # ИСПОЛЬЗУЕМ ИМПОРТИРОВАННЫЙ ПРОМПТ V2
        prompt = prompt_summarize_v2(game_id, store_text)
        try:
            raw = _call_llm(MODEL_SUMMARIZE, prompt, "summarize")
            result = SummaryOutput(**json.loads(raw))
            self._cache[cache_key] = result
            return result
        except Exception:
            return SummaryOutput(game_id=game_id, narrative="Ошибка")

    def classify(self, game_id: str, metrics_4w: List[float]) -> ClassificationOutput:
        cache_key = f"cls_{game_id}_{hash(tuple(metrics_4w))}"
        if cache_key in self._cache:
            print(f"[CACHE HIT] classify для {game_id}")
            return self._cache[cache_key]

        # ИСПОЛЬЗУЕМ ИМПОРТИРОВАННЫЙ ПРОМПТ V2
        prompt = prompt_classify_v2(game_id, metrics_4w)
        try:
            raw = _call_llm(MODEL_CLASSIFY, prompt, "classify")
            data = json.loads(raw)
            if data.get("category") not in ["green", "yellow", "red", "turquoise"]:
                data["category"] = "yellow"
            result = ClassificationOutput(**data)
            self._cache[cache_key] = result
            return result
        except Exception:
            return ClassificationOutput(game_id=game_id, category="yellow")
