# Кандидаты моделей и токен-бюджет

**Роль:** AI Engineer
**Дата:** 2026-10-01
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

Итого: около $0.100 за дайджест. Около $0.40 за месяц (4 дайджеста). Около $5.00 за спринт (50 прогонов).

С русской моделью GigaChat Pro: 25K токенов × 2000 руб./1M = 50 руб. (~$0.56) за дайджест — цены по [3DNews](https://3dnews.ru/1147409/sber-i-yandeks-v-razi-snizili-tseni-na-iitokeni-no-zarubegniy-ii-vsyo-ravno-deshevle).

---

## Что меняется при локальном хостинге

Если модель держать локально: данные не уходят в облако, но нужно железо. Однако утверждение «качество open-weight ниже топовых облачных» в 2026 году уже неверно как общее правило.

Mozilla в отчёте State of Open Source AI (сентябрь 2026) зафиксировала: разрыв между лучшими open-weight и закрытыми фронтирными моделями сократился до ~4.4 месяцев по методологии METR, а по Artificial Analysis Intelligence Index лучшая open-weight модель отстаёт от закрытого лидера всего на 3 балла — [Mozilla — State of Open Source AI](https://unwire.hk/2026/09/18/china-open-source-ai-models-narrow-gap-us-mozilla-report/column/).

GLM-5.2 (open-weight, MIT) набрал 81.0 на Terminal-Bench 2.1 — первый open-weight результат выше 80% на этом бенчмарке. Разрыв с Claude Opus 4.7 — 1 балл, стоимость — менее 1/5 от цены конкурента. Цена GLM-5.2: $1.40/$4.40 за 1M токенов на официальном API Z.ai против $5.00/$25.00 у Claude Opus 4.8 — [GLM-5.2 — vLLM Recipes](https://recipes.vllm.ai/zai-org/GLM-5.2?hardware=h200), [Morph — GLM-5.2 Pricing](https://www.morphllm.com/glm-5-2).

**Вывод «облако дешевле и проще» требует уточнения.** Облако проще — не нужна инфраструктура. Но дешевле — не всегда: при наличии GPU локальный GLM-5.2 может быть дешевле облачных моделей за тот же объём. Для дайджеста с 10 играми это требует отдельного расчёта, который не входит в скоуп Lab1.

---

## Риски бюджета

- GigaChat Pro в 5.6 раза дороже Gemini 3.1 Pro за тот же объём — цены по [3DNews](https://3dnews.ru/1147409/sber-i-yandeks-v-razi-snizili-tseni-na-iitokeni-no-zarubegniy-ii-vsyo-ravno-deshevle) и [Google API Pricing](https://benchlm.ai/google/api-pricing).
- T-lite-it-2.1 требует self-hosting — нужна инфраструктура. Источник: [HuggingFace](https://huggingface.co/t-tech/T-lite-it-2.1).
- Cotype-Nano — 1.5B параметров, качество на сложной суммаризации нужно проверять. Источник: [Featherless.ai](https://featherless.ai/models/MTSAIR/Cotype-Nano).
- Цены могли измениться — проверить на дату старта экспериментов.
- Reasoning-токены могут тарифицироваться отдельно. Это допущение команды: у некоторых провайдеров reasoning-токены включены в стоимость выходных, у других тарифицируются отдельно. Требует проверки на странице тарификации конкретного провайдера перед финальным расчётом.
- Галлюцинации могут привести к перегенерации — заложить двойной бюджет на retry. Источник: [OpenAI — GPT-4 Technical Report](https://arxiv.org/abs/2303.08774).
- Агентная сборка платит latency: несколько шагов последовательно вместо одного вызова. При 10 играх пайплайн занимает минуты. Митигация — параллелизация и кеширование.

---

## Решение

**Статус:** Принято

**Финальный выбор: Gemini 3.1 Pro для суммаризации + Cotype-Nano для классификации.**

**Обоснование выбора:**

1. **Gemini 3.1 Pro для суммаризации.** Показал лучший баланс качества и цены среди кандидатов ([Google API Pricing](https://benchlm.ai/google/api-pricing), [Anthropic](https://www.anthropic.com/news/claude-sonnet-5)), поддерживает tool-calling, необходимый для агентной сборки. Стоимость для нашей задачи — $0.100 за дайджест.

2. **Cotype-Nano для классификации.** Задача простая (метка категории из четырёх), не требует дорогой модели. Стоимость — $0.00024 за дайджест ([Featherless.ai](https://featherless.ai/models/MTSAIR/Cotype-Nano)). Разница с Gemini 3.1 Pro в 400+ раз, качество на задаче классификации достаточно.

3. **Почему не GPT-5.4 и не Claude Sonnet 5** — дороже или сопоставимы, но не дают преимуществ для нашей задачи. GPT-5.4: $2.50/$15.00 против $2.00/$12.00 у Gemini. Claude Sonnet 5: $2.00/$10.00 — сопоставим, но tool-calling не отличается.

4. **Почему не российские модели (GigaChat Pro, YandexGPT).** Для русского языка они дают нативное качество, но в 5.6 раза дороже Gemini. Если качество перевода у Gemini окажется недостаточным — переключимся на GigaChat Pro как запасной вариант (см. план деградации).

5. **Почему не GLM-5.2 (open-weight).** По качеству сопоставим с топовыми, стоит дешевле, но требует инфраструктуры (GPU). Для дайджеста с 10 играми это избыточно.

**План деградации на дешёвую модель:**

| Сценарий | Что делаем | Ожидаемый эффект |
|---|---|---|
| Бюджет обрезали в 2 раза | Переключаем суммаризацию на DeepSeek V3.2 ($0.26/$0.38) | Стоимость падает до ~$0.02 за дайджест, качество ниже на сложных нарративах |
| Качество Gemini не устроило на русском | Переключаем на GigaChat Pro | Стоимость растёт до 50 руб. (~$0.56), качество на русском выше |
| Нужен полностью локальный контур | Переключаем на GLM-5.2 (self-hosted) | Зависит от наличия GPU, качество сопоставимо с Gemini |
| Классификация ошибается | Переключаем Cotype-Nano на Gemini 3.5 Flash Lite | Стоимость растёт до ~$0.003, но точность выше |

**Поле «Цена решения» (заполнено):**

**Деньги:** ~$0.100 за дайджест (Gemini 3.1 Pro + Cotype-Nano), что составляет 0.06–0.17% от стоимости 2–6 часов аналитика (~$60–180). За месяц: ~$0.40. За спринт (50 прогонов): ~$5.00.

**Скорость:** агентная сборка платит latency — 4 шага последовательно. Ориентировочно минуты на дайджест. Точная оценка — открытый вопрос, закрывается в эксперименте (см. [spikes/lab2.md](./spikes/lab2.md)).

**Привязка:** зависимость от SensorTower API для сбора данных. Митигация — абстракция слоя сбора данных, чтобы заменить источник без переписывания пайплайна.

**Ограничения:** галлюцинации в описании нарратива. Митигация — валидация цифр перед публикацией (контроль К3 в [ai-pipeline.md](./ai-pipeline.md)).

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
- GLM-5.2 Terminal-Bench 2.1 (81.0): https://recipes.vllm.ai/zai-org/GLM-5.2?hardware=h200
- GLM-5.2 Pricing (Morph): https://www.morphllm.com/glm-5-2
- Mozilla State of Open Source AI: https://unwire.hk/2026/09/18/china-open-source-ai-models-narrow-gap-us-mozilla-report/column/
