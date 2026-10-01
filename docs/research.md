# Ресёрч: автоматизация дайджеста мобильного гейминга

**Роль:** AI Engineer
**Спринт:** Lab1 — Инициация
**Дата:** 2026-09-17
**Статус:** завершён

## 1. Узкий фокус: актуальность проблемы

Продуктовые аналитики в мобильном F2P-гейминге тратят 2–6 часов в неделю на ручной сбор и написание дайджеста. Логика выводов повторяется, но переписывается заново. При ежемесячной оценке топов аналитик вручную перечитывает старые выпуски.

Источник оценки трудозатрат: внутреннее описание процесса продуктовой аналитики в геймдев-студии (файл «1. Сегмент ЦА.txt», раздел «Боли»). Это допущение команды, не внешняя метрика. Внешнее подтверждение роли аналитика в мобильном гейминге: [Game Developer — The Role of a Product Analyst in Mobile Gaming](https://www.gamedeveloper.com/business/the-role-of-a-product-analyst-in-mobile-gaming).

Проблема жива. SensorTower и AppMagic дают цифры через дашборды, но не генерируют текстовую сводку, не классифицируют игры и не собирают карточки. Это допущение на основе описания продукта команды (файл «1. Сегмент ЦА.txt», раздел «Боли», пункт «Ручное написание сводки/выводов»). Публичные страницы инструментов подтверждают, что они дают метрики, но не текст: [SensorTower](https://sensortower.com/product/mobile-app-intelligence), [AppMagic](https://appmagic.com).

Три боли — ручной сбор, ручное написание, ручной пересмотр — остаются не закрытыми.

## 2. Широкий охват: аналоги и подходы

LLM-суммаризация — для описания нарратива. Классификация категорий — через дешёвую модель. Similarity-поиск — для бирюзовой категории через эмбеддинги.

Выбор подходов (суммаризация, классификация, similarity) — архитектурное рассуждение команды, основанное на декомпозиции задачи дайджеста из брифа продукта (файл «1. Сегмент ЦА.txt», раздел «Связать боли с возможностями команды», блок AI Engineer).

**Кандидаты:**

Для суммаризации:
- Gemini 3.1 Pro: $2.00 / $12.00 за 1M токенов — [Google API Pricing](https://benchlm.ai/google/api-pricing)
- GPT-5.4: $2.50 / $15.00 — [OpenAI Pricing](https://openai.com/api/pricing/)
- Claude Sonnet 5: $2.00 / $10.00 — [Anthropic](https://www.anthropic.com/news/claude-sonnet-5)

Для классификации:
- Cotype-Nano (МТС, open-source): $0.04 / $0.08 — [Featherless.ai](https://featherless.ai/models/MTSAIR/Cotype-Nano)

Для русского языка:
- T-lite-it-2.1 (Т-Банк, Apache 2.0): open-weight, бесплатно — [HuggingFace](https://huggingface.co/t-tech/T-lite-it-2.1)
- GigaChat Pro: 0.50 руб. за 1K токенов — [3DNews](https://3dnews.ru/1147409/sber-i-yandeks-v-razi-snizili-tseni-na-iitokeni-no-zarubegniy-ii-vsyo-ravno-deshevle)
- YandexGPT Pro 5.1: 0.80 руб. за 1K токенов — [RB.RU](https://rb.ru/news/sber-i-yandeks-snizili-stoimost-ii-generacij-gigachat-podeshevel-na-67-yandexgpt-pro-na-33/)

## 3. Узкий фокус: детали для выбора

Критерии: качество суммаризации (30%), стоимость (25%), русский язык (20%), latency (15%), tool-calling (10%).

Веса критериев — экспертное допущение команды, не внешняя метрика. Обоснование: два guardrail из брифа продукта (совпадение с эталоном и цена запроса) напрямую зависят от качества и стоимости, поэтому эти два критерия получают наибольший вес. Методология подхода: [OECD — Multi-Criteria Decision Analysis](https://www.oecd.org/gov/digital-government/multi-criteria-decision-analysis.htm).

Сравнение кандидатов:

- Gemini 3.1 Pro — $2.00/$12.00 — русский да, tool-calling да — [Google API Pricing](https://benchlm.ai/google/api-pricing)
- GPT-5.4 — $2.50/$15.00 — русский да, tool-calling да — [OpenAI Pricing](https://openai.com/api/pricing/)
- Claude Sonnet 5 — $2.00/$10.00 — русский да, tool-calling да — [Anthropic](https://www.anthropic.com/news/claude-sonnet-5)
- GigaChat Pro — 0.50 руб./1K — русский нативно, tool-calling поддерживается — [Sber Developers](https://developers.sber.ru/docs/ru/gigachat/guides/functions/overview)
- YandexGPT Pro 5.1 — 0.80 руб./1K — русский нативно, tool-calling поддерживается — [Neurounit](https://neurounit.ai/blog/yandexgpt-chto-umeet-i-kak-primenyat/)
- T-lite-it-2.1 — open-weight — русский нативно, tool-calling да — [HuggingFace](https://huggingface.co/t-tech/T-lite-it-2.1)

Вывод: для суммаризации — Gemini 3.1 Pro или Claude Sonnet 5, потому что обе показали лучший баланс качества и цены среди кандидатов ([Google API Pricing](https://benchlm.ai/google/api-pricing), [Anthropic](https://www.anthropic.com/news/claude-sonnet-5)) и поддерживают tool-calling, необходимый для агентной сборки. Для русского — GigaChat Pro или T-lite-it-2.1, потому что они нативно работают с русским текстом ([Sber Developers](https://developers.sber.ru/docs/ru/gigachat/guides/functions/overview), [HuggingFace](https://huggingface.co/t-tech/T-lite-it-2.1)). Для классификации — Cotype-Nano, потому что задача простая и не требует дорогой модели ([Featherless.ai](https://featherless.ai/models/MTSAIR/Cotype-Nano)).

## 4. Решение (ADR)

**Статус:** Предложено

**Выбранный подход: агентная сборка пайплайна.**

Цена решения по деньгам:

Дайджест: 10 игр. Суммаризация: 2000 токенов входа, 500 выхода на игру. Классификация: 500 входа, 50 выхода.

Суммаризация (Gemini 3.1 Pro): 20K × $2/1M + 5K × $12/1M = $0.040 + $0.060 = $0.100 — цены по [Google API Pricing](https://benchlm.ai/google/api-pricing).

Классификация (Cotype-Nano): 5K × $0.04/1M + 500 × $0.08/1M = $0.0002 + $0.00004 = $0.00024 — цены по [Featherless.ai](https://featherless.ai/models/MTSAIR/Cotype-Nano).

Итого: около $0.100 за дайджест.

С русской моделью (GigaChat Pro, 2000 руб./1M): 25K токенов × 2000 руб./1M = 50 руб. (~$0.56). Это примерно в 5.6 раза дороже Gemini. Цены по [3DNews](https://3dnews.ru/1147409/sber-i-yandeks-v-razi-snizili-tseni-na-iitokeni-no-zarubegniy-ii-vsyo-ravno-deshevle).

Сравнение с ценой аналитика: час аналитика в геймдев-студии — допущение команды, ~$30/час. Внешний ориентир уровня зарплат: [Game Developer — Game Industry Salaries](https://www.gamedeveloper.com/business/game-industry-salaries-2025). Дайджест = 2–6 часов = $60–180. LLM-затраты = 0.06–0.17% от замещаемого времени.

**Цена решения по скорости (latency).** Агентная сборка платит скоростью. Прямой промпт даёт ответ за один вызов модели — единицы секунд. Агент выполняет 4 шага последовательно: сбор данных, суммаризация, классификация, сборка карточки. При 10 играх это 4 шага пайплайна. Ориентировочно: каждый шаг — секунды, весь прогон — минуты. Latency на текущий момент не замерян — это открытый вопрос, закрывается в записке эксперимента (docs/experiments/lab1.md). Митигация: параллелизация шагов, кеширование промежуточных результатов. Guardrail: дайджест готов за X часов до дедлайна — запас есть, но сокращается при росте числа игр.

**Цена решения по привязке.** Зависимость от SensorTower API — нужна абстракция слоя сбора данных ([SensorTower](https://sensortower.com/product/mobile-app-intelligence)).

**Цена решения по ограничениям.** Галлюцинации — валидация цифр перед публикацией. Источник проблемы: [OpenAI — GPT-4 Technical Report, раздел о галлюцинациях](https://arxiv.org/abs/2303.08774).

Альтернативы (архитектурные рассуждения команды, следуют из требований пайплайна):

- Прямые промпты — отказ: не выполняют оркестрацию 4 шагов (сбор → суммаризация → классификация → сборка), зафиксированных в разделе «Цена решения по скорости». Один вызов модели даёт один ответ и не может выполнить последовательность шагов.

- RAG — отказ: не применим, потому что задача не сводится к поиску по базе знаний. Данные приходят из внешнего API (SensorTower, [SensorTower — Mobile App Intelligence](https://sensortower.com/product/mobile-app-intelligence)), а не из коллекции документов.
