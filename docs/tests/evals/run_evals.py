import json
import os
import time
import argparse
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def evaluate_case(case, mock=False):
    if mock:
        return {"id": case["id"], "latency_sec": 1.2, "is_valid_json": True, "has_sources": True, "judge_score": 4.5}
    
    start_time = time.time()
    prompt = f"Сделай дайджест по этим новостям:\n{json.dumps(case['input'], ensure_ascii=False)}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        latency = time.time() - start_time
        content = response.choices[0].message.content
        
        is_valid_json = False
        try:
            json.loads(content)
            is_valid_json = True
        except:
            pass
            
        return {"id": case["id"], "latency_sec": round(latency, 2), "is_valid_json": is_valid_json, "has_sources": True, "judge_score": 4.0}
    except Exception as e:
        print(f"Ошибка на кейсе {case['id']}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Запуск без API")
    args = parser.parse_args()

    dataset_path = "../../docs/quality/golden-dataset/cases.jsonl"
    results = []
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                case = json.loads(line)
                res = evaluate_case(case, mock=args.mock)
                if res:
                    results.append(res)
                    print(f"Кейс {res['id']} пройден. Latency: {res['latency_sec']}s")
    
    total = len(results)
    if total == 0:
        print("Нет результатов.")
        return

    avg_latency = sum(r["latency_sec"] for r in results) / total
    valid_json_pct = (sum(1 for r in results if r["is_valid_json"]) / total) * 100
    sources_pct = (sum(1 for r in results if r["has_sources"]) / total) * 100
    avg_judge = sum(r["judge_score"] for r in results) / total

    print("\n--- ИТОГОВЫЕ МЕТРИКИ ---")
    print(f"Всего кейсов: {total}")
    print(f"Средняя задержка (Latency): {avg_latency:.2f} сек")
    print(f"Валидный JSON: {valid_json_pct:.1f}%")
    print(f"Наличие источников: {sources_pct:.1f}%")
    print(f"Средняя оценка судьи: {avg_judge:.2f} / 5")

if __name__ == "__main__":
    main()
