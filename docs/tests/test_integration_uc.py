import pytest

# Имитация функций из нашего пайплайна
def fetch_news(sources):
    if not sources:
        return []
    return [{"title": "Новость 1", "source": "dtf"}, {"title": "Реклама", "source": "spam"}]

def filter_news(news_list):
    return [n for n in news_list if n["source"] != "spam"]

def generate_digest(filtered_news):
    if not filtered_news:
        return "Нет новостей"
    return f"Дайджест: {len(filtered_news)} новостей."

def test_key_use_case_happy_path():
    """Критический путь: сбор -> фильтрация -> генерация"""
    sources = ["dtf", "spam"]
    
    # 1. Сбор
    raw_news = fetch_news(sources)
    assert len(raw_news) == 2
    
    # 2. Фильтрация (отсекаем спам)
    clean_news = filter_news(raw_news)
    assert len(clean_news) == 1
    assert clean_news[0]["title"] == "Новость 1"
    
    # 3. Генерация
    digest = generate_digest(clean_news)
    assert "1 новостей" in digest

def test_key_use_case_degradation():
    """Тест деградации: если все источники отвалились, система не падает"""
    sources = []
    raw_news = fetch_news(sources)
    clean_news = filter_news(raw_news)
    digest = generate_digest(clean_news)
    
    assert digest == "Нет новостей"
