# Evals на Baseline

Скрипт для прогона Golden Dataset из лабы 2 через LLM.

## Как запустить
1. Установите зависимости: `pip install -r requirements.txt`
2. Добавьте ключ API: `export OPENAI_API_KEY="твой_ключ"`
3. Запустите прогон: `python run_evals.py`
4. Если ключа нет, проверка логики: `python run_evals.py --mock`

## Что считается
- Скорость (Latency).
- Валидность JSON.
- Наличие источников.
- Оценка качества (судья).
