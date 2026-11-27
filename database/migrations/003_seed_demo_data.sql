INSERT INTO sources (name, url)
VALUES (
    'Gaming Digest Demo',
    'https://example.com/gaming-digest-demo'
)
ON CONFLICT (url) DO NOTHING;

INSERT INTO categories (name, slug)
VALUES
    ('Новости', 'news'),
    ('Обновления', 'updates'),
    ('Релизы', 'releases')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO articles (
    title, summary, url, published_at, status, source_id
)
SELECT
    'Новая эра мобильных игровых миров',
    'Демонстрационная новость для проверки API.',
    'https://example.com/news/mobile-worlds',
    CURRENT_TIMESTAMP,
    'published',
    id
FROM sources
WHERE url = 'https://example.com/gaming-digest-demo'
ON CONFLICT (url) DO NOTHING;

INSERT INTO articles (
    title, summary, url, published_at, status, source_id
)
SELECT
    'Обновления мобильных игр',
    'Пример материала об игровых обновлениях.',
    'https://example.com/news/mobile-updates',
    CURRENT_TIMESTAMP,
    'published',
    id
FROM sources
WHERE url = 'https://example.com/gaming-digest-demo'
ON CONFLICT (url) DO NOTHING;

INSERT INTO articles (
    title, summary, url, published_at, status, source_id
)
SELECT
    'Игровые новинки недели',
    'Демонстрационная подборка релизов.',
    'https://example.com/news/weekly-releases',
    CURRENT_TIMESTAMP,
    'published',
    id
FROM sources
WHERE url = 'https://example.com/gaming-digest-demo'
ON CONFLICT (url) DO NOTHING;

INSERT INTO article_categories (article_id, category_id)
SELECT a.id, c.id
FROM articles a
JOIN categories c ON c.slug = 'news'
WHERE a.url = 'https://example.com/news/mobile-worlds'
ON CONFLICT DO NOTHING;

INSERT INTO article_categories (article_id, category_id)
SELECT a.id, c.id
FROM articles a
JOIN categories c ON c.slug = 'updates'
WHERE a.url = 'https://example.com/news/mobile-updates'
ON CONFLICT DO NOTHING;

INSERT INTO article_categories (article_id, category_id)
SELECT a.id, c.id
FROM articles a
JOIN categories c ON c.slug = 'releases'
WHERE a.url = 'https://example.com/news/weekly-releases'
ON CONFLICT DO NOTHING;

INSERT INTO events (title, description, starts_at)
SELECT
    'Турнир по мобильному геймингу',
    'Демонстрационное игровое событие.',
    CURRENT_TIMESTAMP + INTERVAL '7 days'
WHERE NOT EXISTS (
    SELECT 1 FROM events
    WHERE title = 'Турнир по мобильному геймингу'
);