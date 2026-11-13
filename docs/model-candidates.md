# Кандидаты моделей и токен-бюджет

**Роль:** AI Engineer
**Дата:** 2026-10-15
**Спринт:** Lab2 — Design
**Связанные документы:** [research.md](./research.md), [ai-pipeline.md](./ai-pipeline.md)

---

## Допущения

Дайджест — 10 игр в неделю. Средняя карточка — 2000 токенов входа (стор и промо) и 500 токенов выхода (описание). Классификация — 500 токенов входа и 50 выхода на игру. Количество запросов в день — один или два (черновик и финал).

Эти допущения — предварительная оценка на основе внутреннего описания процесса аналитики (файл «1. Сегмент ЦА.txt», раздел «Боли»). Их нужно заменить на реальные объёмы после прогона экспериментов.

---

## Кандидаты

**Облако (США/Китай):**
- Gemini 3.1 Pro: $2.00 / $12.00 за 1M токенов — [Google API Pricing](https://benchlm.ai/google/api-pricing)
- GPT-5.4: $2.50 / $15.00 — [OpenAI Pricing](https://openai.com/api/pricing/)
- Claude Sonnet 5: $2.00 / $10.00 — [Anthropic](https://www.anthropic.com/news/claude-sonnet-5)

**Российские:**
- GigaChat Pro: 0.50 руб. за 1K токенов — [3DNews](https://3dnews.ru/1147409/sber-i-yandeks-v-razi-snizili-tseni-na-iitokeni-no-zarubegniy-ii-vsyo-ravno-deshevle)
- YandexGPT Pro 5.1: 0.80 руб. за 1K токенов — [RB.RU](https://rb.ru/news/sber-i-yandeks-snizili-stoimost-ii-generacij-gigachat-podeshevel-na-67-yandexgpt-pro-na-33/)
- T-lite-it-2.1 (Т-Банк, Apache 2.0): open-weight, бесплатно — [HuggingFace](https://huggingface.co/t-tech/T-lite-it-2.1)

**Локальные (open-source):**
- Cotype-Nano (МТС): $0.04 / $0.08 — [Featherless.ai](https://featherless.ai/models/MTSAIR/Cotype-Nano)
- GLM-5.2 (MIT, open-weight): $1.40 / $4.40 за 1M токенов — [GLM-5.2 — vLLM Recipes](https://recipes.vllm.ai/zai-org/GLM-5.2?hardware=h200)

---

## Расчёт бюджета

Суммаризация (Gemini 3.1 Pro): 20K × $2/1M + 5K × $12/1M = $0.040 + $0.060 = $0.100 — цены по [Google API Pricing](https://benchlm.ai/google/api-pricing).

Классификация (Cotype-Nano): 5K × $0.04/1M + 500 × $0.08/1M = $0.0002 + $0.00004 = $0.00024 — цены по [Featherless.ai](https://featherless.ai/models/MTSAIR/Cotype-Nano).

Итого: около $0.100 за дайджест. Около $0.40 за месяц. Около $5.00 за спринт (50 прогонов).

С русской моделью GigaChat Pro: 25K токенов × 2000 руб./1M = 50 руб. (~$0.56) за дайджест.

---

## Что меняется при локальном хостинге

Утверждение «качество open-weight ниже топовых облачных» в 2026 году уже неверно как общее правило.

Mozilla в отчёте State of Open Source AI (сентябрь 2026) зафиксировала: разрыв между лучшими open-weight и закрытыми фронтирными моделями сократился до ~4.4 месяцев по методологии METR, по Artificial Analysis Intelligence Index — 3 балла — [Mozilla — State of Open Source AI](https://unwire.hk/2026/09/18/china-open-source-ai-models-narrow-gap-us-mozilla-report/column/).

GLM-5.2 (open-weight, MIT) набрал 81.0 на Terminal-Bench 2.1 — первый open-weight результат выше 80%. Цена $1.40/$4.40 за 1M токенов против $5.00/$25.00 у Claude Opus 4.8 — [GLM-5.2 — vLLM Recipes](https://recipes.vllm.ai/zai-org/GLM-5.2?hardware=h200).

---

## Риски бюджета

- GigaChat Pro в 5.6 раза дороже Gemini 3.1 Pro.
- T-lite-it-2.1 требует self-hosting.
- Cotype-Nano — 1.5B параметров, качество на сложной суммаризации нужно проверять.
- Цены могли измениться — проверить на дату старта экспериментов.
- Reasoning-токены могут тарифицироваться отдельно — допущение команды, требует проверки на странице провайдера.
- Галлюцинации могут привести к перегенерации — заложить двойной бюджет.
- Агентная сборка платит latency: несколько шагов последовательно.

---

## Решение

**Статус:** Принято

**Финальный выбор: Gemini 3.1 Pro для суммаризации + Cotype-Nano для классификации.**

**Обоснование:**

1. **Gemini 3.1 Pro.** Лучший баланс качества и цены, tool-calling для агентной сборки. Стоимость — $0.100 за дайджест.

2. **Cotype-Nano.** Задача классификации простая, дорогая модель избыточна. В 400+ раз дешевле Gemini.

3. **Не GPT-5.4 и не Claude Sonnet 5** — дороже или сопоставимы без преимуществ.

4. **Не российские модели** — GigaChat Pro в 5.6 раза дороже. GigaChat в плане деградации.

5. **Не GLM-5.2** — сопоставим по качеству, но требует GPU.

**План деградации:**

| Сценарий | Действие | Эффект |
|---|---|---|
| Бюджет обрезали вдвое | DeepSeek V3.2 для суммаризации | ~$0.02 за дайджест |
| Русский не устроил | GigaChat Pro | 50 руб. (~$0.56) за дайджест |
| Локальный контур | GLM-5.2 self-hosted | Зависит от GPU |
| Классификация ошибается | Gemini 3.5 Flash Lite | ~$0.003, точность выше |

**Цена решения:**

- **Деньги:** ~$0.100 за дайджест (0.06–0.17% от 2–6 часов аналитика).
- **Скорость:** 4 шага последовательно, минуты на дайджест. Latency не замерен — открытый вопрос.
- **Привязка:** зависимость от SensorTower API. Митигация — абстракция слоя сбора.
- **Ограничения:** галлюцинации. Митигация — валидация цифр (К3).

---

## Источники

- Google API Pricing: https://benchlm.ai/google/api-pricing
- OpenAI Pricing: https://openai.com/api/pricing/
- Anthropic Claude Sonnet 5: https://www.anthropic.com/news/claude-sonnet-5
- Featherless.ai Cotype-Nano: https://featherless.ai/models/MTSAIR/Cotype-Nano
- HuggingFace T-lite-it-2.1: https://huggingface.co/t-tech/T-lite-it-2.1
- 3DNews (GigaChat): https://3dnews.ru/1147409/sber-i-yandeks-v-razi-snizili-tseni-na-iitokeni-no-zarubegniy-ii-vsyo-ravno-deshevle
- RB.RU (YandexGPT): https://rb.ru/news/sber-i-yandeks-snizili-stoimost-ii-generacij-gigachat-podeshevel-na-67-yandexgpt-pro-na-33/
- Game Developer (роль аналитика): https://www.gamedeveloper.com/business/the-role-of-a-product-analyst-in-mobile-gaming
- Game Developer (зарплаты): https://www.gamedeveloper.com/business/game-industry-salaries-2025
- OECD MCDA: https://www.oecd.org/gov/digital-government/multi-criteria-decision-analysis.htm
- OpenAI GPT-4 Technical Report: https://arxiv.org/abs/2303.08774
- SensorTower: https://sensortower.com/product/mobile-app-intelligence
- AppMagic: https://appmagic.com
- GLM-5.2 Terminal-Bench: https://recipes.vllm.ai/zai-org/GLM-5.2?hardware=h200
- GLM-5.2 Pricing: https://www.morphllm.com/glm-5-2
- Mozilla State of Open Source AI: https://unwire.hk/2026/09/18/china-open-source-ai-models-narrow-gap-us-mozilla-report/column/
