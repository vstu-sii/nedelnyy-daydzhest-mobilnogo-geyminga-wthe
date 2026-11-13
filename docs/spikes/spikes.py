# spikes.py — ЛОКАЛЬНЫЙ файл, не коммитить в GitHub
import json
import time
from openai import OpenAI
from rouge_score import rouge_scorer

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="",
)

SUMMARIZE_MODEL = "openrouter/free"
CLASSIFY_MODEL = "openrouter/free"

# ============ СПАЙК 1: СУММАРИЗАЦИЯ ============

summarize_examples = [
    {
        "game_id": "nr_002",
        "store_text": "Командный шутер с короткими матчами. Игрок выбирает героя с уникальными способностями, сражается в команде 3v3. Есть сезонные пропуска, ежедневные задания, ранкед.",
        "reference": "Neon Raiders — командный шутер 3v3 с короткими матчами. Акцент на героях с уникальными способностями и сезонных пропусках.",
    },
    {
        "game_id": "tt_001",
        "store_text": "Восстанавливайте старую таверну, объединяя предметы. Проходите сюжетные главы, открывайте рецепты, украшайте залы. Механика merge + сторителлинг.",
        "reference": "Tidy Tavern — merge-головоломка с сюжетом. Игрок восстанавливает таверну, объединяя предметы и открывая новые рецепты.",
    },
    {
        "game_id": "so_003",
        "store_text": "Выращивайте сад и открывайте новые участки. Сажайте растения, собирайте урожай, выполняйте заказы. Расслабляющий farm-симулятор с элементами декора.",
        "reference": "Sunny Orchard — расслабляющий farm-симулятор. Игрок выращивает сад, собирает урожай и открывает новые участки.",
    },
    {
        "game_id": "synth_004",
        "store_text": "Космический симулятор добычи ресурсов. Управляй флотом дронов, строй базы на астероидах, торгуй с фракциями. Idle-механики + PvP-рейды.",
        "reference": "Astro Miner — космический idle-симулятор с PvP. Игрок управляет дронами, добывает ресурсы на астероидах и торгует с фракциями.",
    },
    {
        "game_id": "synth_005",
        "store_text": "Собирайте карты, сражайтесь в пошаговых боях. Коллекция из 200+ героев, комбинации способностей, PvP-арена и гильдейские войны.",
        "reference": "Card Clash — коллекционная карточная игра с пошаговыми боями. 200+ героев, PvP-арена и гильдейские войны.",
    },
]

print("=" * 60)
print("СПАЙК 1: СУММАРИЗАЦИЯ")
print("=" * 60)

scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
spike1_results = []

for ex in summarize_examples:
    prompt = f"""Опиши суть игры в 3-4 предложениях на русском языке, без выдуманных деталей.
Игра: {ex['game_id']}
Описание из стора: {ex['store_text']}

Верни только описание, без пояснений."""

    start = time.time()
    try:
        response = client.chat.completions.create(
            model=SUMMARIZE_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        generated = response.choices[0].message.content.strip()
        latency = round(time.time() - start, 2)
        score = scorer.score(ex["reference"], generated)["rougeL"].fmeasure

        spike1_results.append({
            "game_id": ex["game_id"],
            "rouge_l": round(score, 3),
            "latency_s": latency,
            "generated": generated[:150],
        })
        print(f"{ex['game_id']}: ROUGE-L={score:.3f}, latency={latency}s")
        print(f"  {generated[:120]}...\n")
    except Exception as e:
        print(f"{ex['game_id']}: ОШИБКА — {e}")
        spike1_results.append({"game_id": ex["game_id"], "error": str(e)})

valid = [r for r in spike1_results if "rouge_l" in r]
avg_rouge = sum(r["rouge_l"] for r in valid) / len(valid) if valid else 0
print(f"\nСредний ROUGE-L F1: {avg_rouge:.3f}\n")

# ============ СПАЙК 2: КЛАССИФИКАЦИЯ ============

classify_examples = [
    {"game_id": "synth_g1", "metrics_4w": [100, 120, 140, 160], "true": "green"},
    {"game_id": "synth_g2", "metrics_4w": [500, 600, 700, 800], "true": "green"},
    {"game_id": "synth_g3", "metrics_4w": [200, 240, 290, 350], "true": "green"},
    {"game_id": "synth_g4", "metrics_4w": [80, 100, 120, 145], "true": "green"},
    {"game_id": "synth_g5", "metrics_4w": [1000, 1150, 1300, 1500], "true": "green"},
    {"game_id": "synth_y1", "metrics_4w": [100, 95, 90, 200], "true": "yellow"},
    {"game_id": "synth_y2", "metrics_4w": [300, 280, 260, 500], "true": "yellow"},
    {"game_id": "synth_y3", "metrics_4w": [150, 140, 130, 280], "true": "yellow"},
    {"game_id": "synth_y4", "metrics_4w": [400, 380, 360, 700], "true": "yellow"},
    {"game_id": "synth_y5", "metrics_4w": [50, 45, 40, 90], "true": "yellow"},
]

print("=" * 60)
print("СПАЙК 2: КЛАССИФИКАЦИЯ")
print("=" * 60)

spike2_results = []

for ex in classify_examples:
    prompt = f"""Определи категорию игры по метрикам за 4 недели.
Категории: green (стабильный рост), yellow (стагнация или случайный всплеск), red (падение), turquoise (похож на наш проект).

Метрики (gross_usd по неделям): {ex['metrics_4w']}

Ответь одним словом: green, yellow, red или turquoise."""

    try:
        response = client.chat.completions.create(
            model=CLASSIFY_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
        )
        predicted = response.choices[0].message.content.strip().lower()
        predicted = predicted.split()[0].strip(".,!?")
        is_false_green = (ex["true"] != "green" and predicted == "green")

        spike2_results.append({
            "game_id": ex["game_id"],
            "true": ex["true"],
            "predicted": predicted,
            "false_green": is_false_green,
        })
        print(f"{ex['game_id']}: true={ex['true']}, pred={predicted}, false_green={is_false_green}")
    except Exception as e:
        print(f"{ex['game_id']}: ОШИБКА — {e}")
        spike2_results.append({"game_id": ex["game_id"], "error": str(e)})

correct = sum(1 for r in spike2_results if r.get("true") == r.get("predicted"))
accuracy = correct / len(classify_examples)
false_greens = sum(1 for r in spike2_results if r.get("false_green"))
fpr = false_greens / 5

print(f"\nAccuracy: {accuracy:.2f}")
print(f"False positive rate (зелёный): {fpr:.2f}\n")

# ============ СОХРАНИТЬ РЕЗУЛЬТАТЫ ============

output = {
    "spike_1_summarization": {
        "model": SUMMARIZE_MODEL,
        "results": spike1_results,
        "avg_rouge_l": round(avg_rouge, 3),
    },
    "spike_2_classification": {
        "model": CLASSIFY_MODEL,
        "results": spike2_results,
        "accuracy": round(accuracy, 2),
        "false_positive_rate_green": round(fpr, 2),
    },
}

with open("spike_results.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Результаты сохранены в spike_results.json")
