import os
import json
import time
import pandas as pd
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY", "sk-placeholder")
)
MODEL = "openrouter/free"

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=5))
def call_llm(prompt: str, step_name: str):
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
        # Сохраняем полный трейс
        trace = {
            "step": step_name,
            "model": MODEL,
            "latency": round(latency, 2),
            "prompt": prompt,
            "response": response.choices[0].message.content,
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
            "status": "success"
        }
        print(json.dumps(trace, ensure_ascii=False))
        return response.choices[0].message.content, latency
    except Exception as e:
        print(f'{{"step": "{step_name}", "status": "error: {e}"}}')
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
    print("Запуск экспериментов...")
    for game in games_data:
        gid = game["game_id"]
        
        prompt_sum = f'Опиши игру в 3-4 предложениях. Описание: {game["store_description"]}. Верни JSON: {{"game_id": "{gid}", "narrative": "текст"}}'
        try:
            raw, lat_s = call_llm(prompt_sum, "summarize")
            narrative = json.loads(raw).get("narrative", "Нет текста")
        except Exception:
            narrative = f"Fallback описание для {gid}"
            lat_s = 0.0

        prompt_cls = f'Определи категорию (green, yellow, red, turquoise) по метрикам: {game["metrics_4w"]}. Верни JSON: {{"game_id": "{gid}", "category": "green"}}'
        try:
            raw, lat_c = call_llm(prompt_cls, "classify")
            category = json.loads(raw).get("category", "yellow")
            if category not in ["green", "yellow", "red", "turquoise"]: category = "yellow"
        except Exception:
            category = "green" if game["metrics_4w"][-1] > game["metrics_4w"][0] else "yellow"
            lat_c = 0.0

        results.append({
            "game_id": gid,
            "narrative": narrative,
            "category": category,
            "latency_summarize_s": round(lat_s, 2),
            "latency_classify_s": round(lat_c, 2),
            "total_latency_s": round(lat_s + lat_c, 2),
            "approx_input_tokens": len(game["store_description"]) // 4
        })

    df = pd.DataFrame(results)
    df.to_csv("metrics.csv", index=False)
    df.to_json("metrics.json", orient="records", force_ascii=False)
    print("\nРезультаты сохранены в metrics.json и metrics.csv")

if __name__ == "__main__":
    main()
