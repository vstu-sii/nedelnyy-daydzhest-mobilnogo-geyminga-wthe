import os
import json
import time
import pandas as pd
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
# Импортируем наши функции трассировки
from ml.tracing.config import setup_tracing, log_to_dashboard

# Инициализируем логгер
setup_tracing()

API_KEY = os.environ.get("OPENROUTER_API_KEY")
IS_MOCK = not API_KEY or API_KEY == "sk-placeholder"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY or "sk-placeholder"
)
MODEL = "openrouter/free"

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=5))
def call_llm(prompt: str, step_name: str):
    if IS_MOCK:
        # Заглушка для робота, если нет ключа
        trace = {"step": step_name, "status": "mock", "prompt": prompt, "response": "mock", "total_tokens": 10}
        log_to_dashboard(trace)
        return {"narrative": "Симуляция нарратива", "category": "green"}, 2.5, 15, 20, 35

    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        latency = time.time() - start
        usage = response.usage
        
        trace = {
            "step": step_name,
            "model": MODEL,
            "latency_s": round(latency, 2),
            "prompt": prompt,
            "response": response.choices[0].message.content,
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
            "status": "success"
        }
        # Вызываем трассировку
        log_to_dashboard(trace) 
        return response.choices[0].message.content, latency, usage.prompt_tokens, usage.completion_tokens, usage.total_tokens
    except Exception as e:
        latency = round(time.time() - start, 2)
        log_to_dashboard({"step": step_name, "status": f"error: {e}", "latency_s": latency})
        raise e

def main():
    games_data = [
        {"game_id": "nr_002", "store_description": "Командный шутер 3v3 с короткими матчами. Сезонные пропуска.", "metrics_4w": [100, 120, 140, 160]},
        {"game_id": "tt_001", "store_description": "Merge-головоломка. Восстанавливайте таверну.", "metrics_4w": [500, 600, 700, 800]},
        {"game_id": "so_003", "store_description": "Farm-симулятор. Выращивайте сад, собирайте урожай.", "metrics_4w": [100, 95, 90, 200]},
        {"game_id": "synth_004", "store_description": "Космический idle-симулятор с PvP.", "metrics_4w": [300, 280, 260, 500]},
        {"game_id": "synth_005", "store_description": "Коллекционная карточная игра с пошаговыми боями.", "metrics_4w": [150, 140, 130, 280]},
    ]

    results = []
    print(f"Запуск экспериментов (Режим симуляции: {IS_MOCK})...")
    
    for game in games_data:
        gid = game["game_id"]
        
        prompt_sum = f'Опиши игру в 3-4 предложениях. Описание: {game["store_description"]}. Верни JSON: {{"game_id": "{gid}", "narrative": "текст"}}'
        try:
            raw, lat_s, p_tok, c_tok, t_tok = call_llm(prompt_sum, "summarize")
            narrative = json.loads(raw).get("narrative") if not IS_MOCK else "Симуляция нарратива"
        except Exception:
            narrative = f"Fallback описание для {gid}"
            lat_s, p_tok, c_tok, t_tok = 0.0, 0, 0, 0

        prompt_cls = f'Определи категорию (green, yellow, red, turquoise) по метрикам: {game["metrics_4w"]}. Верни JSON: {{"game_id": "{gid}", "category": "green"}}'
        try:
            raw, lat_c, p_tok_c, c_tok_c, t_tok_c = call_llm(prompt_cls, "classify")
            category = json.loads(raw).get("category") if not IS_MOCK else "green"
        except Exception:
            category = "yellow"
            lat_c, p_tok_c, c_tok_c, t_tok_c = 0.0, 0, 0, 0

        total_prompt_tokens = p_tok + p_tok_c
        total_completion_tokens = c_tok + c_tok_c
        total_tokens = t_tok + t_tok_c

        results.append({
            "game_id": gid,
            "narrative": narrative,
            "category": category,
            "latency_summarize_s": round(lat_s, 2),
            "latency_classify_s": round(lat_c, 2),
            "total_latency_s": round(lat_s + lat_c, 2),
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "total_tokens": total_tokens
        })

    df = pd.DataFrame(results)
    df.to_csv("metrics.csv", index=False)
    df.to_json("metrics.json", orient="records", force_ascii=False)
    print("\nРезультаты сохранены. Трассировка записана в логи.")

if __name__ == "__main__":
    main()
