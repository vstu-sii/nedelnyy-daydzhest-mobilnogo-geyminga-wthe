
import os
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .model import generate_digest

app = FastAPI(
    title="Gaming Digest API",
    description="API еженедельного дайджеста мобильного гейминга",
    version="1.0.0",
)

def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise HTTPException(
            status_code=503,
            detail="DATABASE_URL не настроен",
        )

    try:
        return psycopg.connect(
            database_url,
            row_factory=dict_row,
        )
    except psycopg.Error as error:
        raise HTTPException(
            status_code=503,
            detail="Не удалось подключиться к базе данных",
        ) from error

@app.get("/api/health")
def health_check():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")

        return {
            "status": "ok",
            "service": "gaming-digest-api",
            "database": "connected",
        }
    except HTTPException:
        raise

@app.get("/api/news")
def get_news():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.id,
                    a.title,
                    a.summary,
                    c.slug AS category
                FROM articles a
                JOIN article_categories ac
                    ON ac.article_id = a.id
                JOIN categories c
                    ON c.id = ac.category_id
                WHERE a.status = 'published'
                ORDER BY a.published_at DESC NULLS LAST, a.id DESC
            """)

            return cursor.fetchall()

@app.get("/api/news/{news_id}")
def get_news_item(news_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.id,
                    a.title,
                    a.summary,
                    a.content,
                    c.slug AS category
                FROM articles a
                JOIN article_categories ac
                    ON ac.article_id = a.id
                JOIN categories c
                    ON c.id = ac.category_id
                WHERE a.id = %s
                  AND a.status = 'published'
                LIMIT 1
            """, (news_id,))

            article = cursor.fetchone()

    if article is None:
        raise HTTPException(
            status_code=404,
            detail="Новость не найдена",
        )

    return article

@app.get("/api/events")
def get_events():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    title,
                    description,
                    starts_at,
                    ends_at,
                    game_id
                FROM events
                ORDER BY starts_at
            """)

            return cursor.fetchall()

class ModelResult(BaseModel):
    model_name: str
    input_data: dict[str, Any]
    result_data: dict[str, Any]

@app.post("/api/model-results", status_code=201)
def save_model_result(result: ModelResult):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO model_results (
                    model_name,
                    input_data,
                    result_data
                )
                VALUES (%s, %s, %s)
                RETURNING id, model_name, created_at
            """, (
                result.model_name,
                Jsonb(result.input_data),
                Jsonb(result.result_data),
            ))

            saved_result = cursor.fetchone()

    return saved_result

class GenerateRequest(BaseModel):
    topic: str

@app.post("/api/generate", status_code=201)
def generate_result(request: GenerateRequest):
    # 1. Вызываем локальную модель-заглушку
    result = generate_digest(request.topic)

    # 2. Сохраняем входные данные и результат в PostgreSQL
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO model_results (
                    model_name,
                    input_data,
                    result_data
                )
                VALUES (%s, %s, %s)
                RETURNING id, model_name, created_at
            """, (
                result["model_name"],
                Jsonb({"topic": request.topic}),
                Jsonb(result),
            ))

            saved_result = cursor.fetchone()

    # 3. Возвращаем результат интерфейсу
    return {
        "id": saved_result["id"],
        "model_name": saved_result["model_name"],
        "topic": request.topic,
        "result": result,
        "created_at": saved_result["created_at"],
    }