# Кандидаты моделей и токен-бюджет

**Роль:** AI Engineer
**Дата:** 2026-09-17

## Допущения

Дайджест — 10 игр в неделю. Средняя карточка — 2000 токенов входа (стор и промо) и 500 токенов выхода (описание). Классификация — 500 токенов входа и 50 выхода на игру. Количество запросов в день — один или два (черновик и финал).

Эти допущения — предварительная оценка. Их нужно заменить на реальные объёмы, когда появятся данные из эксперимента.

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

## Расчёт бюджета

Суммаризация (Gemini 3.1 Pro): 20K × $2/1M + 5K × $12/1M = $0.040 + $0.060 = $0.100

Классификация (Cotype-Nano): 5K × $0.04/1M + 500 × $0.08/1M = $0.0002 + $0.00004 = $0.00024

Итого: около $0.100 за дайджест. Около $0.40 за месяц (4 дайджеста). Около $5.00 за спринт (50 прогонов).

С русской моделью GigaChat Pro: 25K токенов × 2000 руб./1M = 50 руб. (~$0.56) за дайджест.

## Что меняется при локальном хостинге

Если модель держать локально: данные не уходят в облако, но нужно железо (GPU с достаточной VRAM), качество open-weight моделей ниже топовых облачных, latency зависит от вашего железа. Для дайджеста с 10 играми это избыточно — облако дешевле и проще.

## Риски бюджета

- GigaChat Pro в 5.6 раза дороже Gemini 3.1 Pro за тот же объём.
- T-lite-it-2.1 требует self-hosting — нужна инфраструктура.
- Cotype-Nano — 1.5B параметров, качество на сложной суммаризации нужно проверять.
- Цены могли измениться — проверить на дату старта экспериментов.
- Reasoning-токены могут тарифицироваться отдельно — учесть.
- Галлюцинации могут привести к перегенерации — заложить двойной бюджет на retry.

## Источники

- Google API Pricing: https://benchlm.ai/google/api-pricing
- OpenAI Pricing: https://openai.com/api/pricing/
- Anthropic Claude Sonnet 5: https://www.anthropic.com/news/claude-sonnet-5
- Featherless.ai Cotype-Nano: https://featherless.ai/models/MTSAIR/Cotype-Nano
- HuggingFace T-lite-it-2.1: https://huggingface.co/t-tech/T-lite-it-2.1
- 3DNews (GigaChat): https://3dnews.ru/1147409/sber-i-yandeks-v-razi-snizili-tseni-na-iitokeni-no-zarubegniy-ii-vsyo-ravno-deshevle
- RB.RU (YandexGPT): https://rb.ru/news/sber-i-yandeks-snizili-stoimost-ii-generacij-gigachat-podeshevel-na-67-yandexgpt-pro-na-33/
