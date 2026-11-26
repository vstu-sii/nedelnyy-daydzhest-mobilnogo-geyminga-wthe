
import os
import time
import logging
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import Response
from pydantic import BaseModel

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from .model import generate_digest


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("gaming_digest_api")


# --------------------------------------------------
# OpenTelemetry and Tempo
# --------------------------------------------------

resource = Resource.create({
    "service.name": "gaming-digest-api",
    "service.version": "1.0.0",
})

tracer_provider = TracerProvider(resource=resource)

otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://tempo:4317",
    ),
    insecure=True,
)

tracer_provider.add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer("gaming-digest-api")


# --------------------------------------------------
# Prometheus metrics
# --------------------------------------------------

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
)

LIMIT_REJECTIONS = Counter(
    "model_limit_rejections_total",
    "Total model requests rejected by usage limits",
    ["limit_type"],
)

# Demonstration spend metrics.
# Replace estimated costs with provider billing data in production.
MODEL_ESTIMATED_SPEND = Gauge(
    "model_estimated_spend_usd",
    "Estimated model spending in USD for the current day",
)

MODEL_SPEND_ALERTS = Counter(
    "model_spend_alerts_total",
    "Number of model spending threshold warnings",
)


# --------------------------------------------------
# Application
# --------------------------------------------------

app = FastAPI(
    title="Gaming Digest API",
    description="API еженедельного дайджеста мобильного гейминга",
    version="1.0.0",
)

FastAPIInstrumentor.instrument_app(
    app,
    tracer_provider=tracer_provider,
)


# --------------------------------------------------
# Request metrics and logging middleware
# --------------------------------------------------

@app.middleware("http")
async def observe_requests(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)

    method = request.method
    start_time = time.perf_counter()
    status = "500"

    REQUESTS_IN_PROGRESS.inc()

    try:
        response = await call_next(request)
        status = str(response.status_code)
        return response

    except Exception:
        logger.exception(
            "Unhandled request error: method=%s",
            method,
        )
        raise

    finally:
        duration = time.perf_counter() - start_time

        route = request.scope.get("route")
        path = getattr(route, "path", "unmatched")

        REQUEST_COUNT.labels(
            method=method,
            path=path,
            status=status,
        ).inc()

        REQUEST_LATENCY.labels(
            method=method,
            path=path,
        ).observe(duration)

        REQUESTS_IN_PROGRESS.dec()

        logger.info(
            "http_request method=%s path=%s status=%s duration_seconds=%.4f",
            method,
            path,
            status,
            duration,
        )


# --------------------------------------------------
# Prometheus endpoint
# --------------------------------------------------

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        headers={"Content-Type": CONTENT_TYPE_LATEST},
    )


# --------------------------------------------------
# Database connection
# --------------------------------------------------

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


# --------------------------------------------------
# Daily usage and spending limits
# --------------------------------------------------

DAILY_REQUEST_LIMIT = int(
    os.getenv("DAILY_REQUEST_LIMIT", "20")
)

DAILY_TOKEN_LIMIT = int(
    os.getenv("DAILY_TOKEN_LIMIT", "10000")
)

DAILY_SPEND_LIMIT_USD = float(
    os.getenv("DAILY_SPEND_LIMIT_USD", "1.00")
)

SPEND_ALERT_THRESHOLD = float(
    os.getenv("SPEND_ALERT_THRESHOLD", "0.80")
)

# Demonstration price per 1000 estimated tokens.
# This is NOT a real provider price.
DEMO_PRICE_PER_1000_TOKENS = float(
    os.getenv("DEMO_PRICE_PER_1000_TOKENS", "0.002")
)


def estimate_tokens(result: dict[str, Any]) -> int:
    """
    Approximate token count for the local demo model.
    Replace with actual provider usage when a real LLM is connected.
    """
    text = str(result)
    return max(1, len(text) // 4)


def estimate_cost_usd(tokens: int) -> float:
    """Calculate demonstration cost from estimated token count."""

    return (
        tokens / 1000
    ) * DEMO_PRICE_PER_1000_TOKENS


def check_spend_alert(
    user_id: str,
    estimated_tokens: int,
) -> float:
    """
    Calculate demonstration daily spending and emit a warning
    when the configured threshold is reached.
    """

    estimated_cost = estimate_cost_usd(estimated_tokens)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COALESCE(SUM(token_count), 0) AS total_tokens
                FROM model_usage
                WHERE usage_date = CURRENT_DATE
                """
            )

            usage = cursor.fetchone()

    total_tokens = int(usage["total_tokens"])
    estimated_daily_spend = estimate_cost_usd(total_tokens)

    MODEL_ESTIMATED_SPEND.set(estimated_daily_spend)

    warning_threshold = (
        DAILY_SPEND_LIMIT_USD * SPEND_ALERT_THRESHOLD
    )

    if estimated_daily_spend >= warning_threshold:
        MODEL_SPEND_ALERTS.inc()

        logger.warning(
            "model_spend_alert user_id=%s estimated_spend_usd=%.6f "
            "warning_threshold_usd=%.6f daily_limit_usd=%.6f",
            user_id,
            estimated_daily_spend,
            warning_threshold,
            DAILY_SPEND_LIMIT_USD,
        )

    if estimated_daily_spend >= DAILY_SPEND_LIMIT_USD:
        logger.error(
            "model_spend_limit_reached user_id=%s "
            "estimated_spend_usd=%.6f daily_limit_usd=%.6f",
            user_id,
            estimated_daily_spend,
            DAILY_SPEND_LIMIT_USD,
        )

        raise HTTPException(
            status_code=429,
            detail="Превышен демонстрационный дневной бюджет",
        )

    return estimated_cost


def reserve_daily_usage(
    user_id: str,
    estimated_tokens: int,
) -> None:
    """
    Atomically reserve one request and estimated tokens.
    PostgreSQL protects concurrent updates using ON CONFLICT.
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO model_usage (
                    user_id,
                    usage_date,
                    request_count,
                    token_count,
                    updated_at
                )
                VALUES (
                    %s,
                    CURRENT_DATE,
                    1,
                    %s,
                    CURRENT_TIMESTAMP
                )
                ON CONFLICT (user_id, usage_date)
                DO UPDATE SET
                    request_count = model_usage.request_count + 1,
                    token_count = model_usage.token_count + EXCLUDED.token_count,
                    updated_at = CURRENT_TIMESTAMP
                WHERE
                    model_usage.request_count < %s
                    AND model_usage.token_count + EXCLUDED.token_count <= %s
                RETURNING request_count, token_count
                """,
                (
                    user_id,
                    estimated_tokens,
                    DAILY_REQUEST_LIMIT,
                    DAILY_TOKEN_LIMIT,
                ),
            )

            usage = cursor.fetchone()

            if usage is not None:
                logger.info(
                    "model_usage_reserved user_id=%s requests=%s tokens=%s",
                    user_id,
                    usage["request_count"],
                    usage["token_count"],
                )
                return

            cursor.execute(
                """
                SELECT request_count, token_count
                FROM model_usage
                WHERE user_id = %s
                  AND usage_date = CURRENT_DATE
                """,
                (user_id,),
            )

            current_usage = cursor.fetchone()

    if current_usage is None:
        raise HTTPException(
            status_code=503,
            detail="Не удалось проверить дневной лимит",
        )

    if current_usage["request_count"] >= DAILY_REQUEST_LIMIT:
        LIMIT_REJECTIONS.labels(limit_type="requests").inc()

        logger.warning(
            "model_limit_rejected user_id=%s limit_type=requests "
            "current=%s limit=%s",
            user_id,
            current_usage["request_count"],
            DAILY_REQUEST_LIMIT,
        )

        raise HTTPException(
            status_code=429,
            detail="Превышен дневной лимит запросов",
        )

    LIMIT_REJECTIONS.labels(limit_type="tokens").inc()

    logger.warning(
        "model_limit_rejected user_id=%s limit_type=tokens "
        "current=%s requested=%s limit=%s",
        user_id,
        current_usage["token_count"],
        estimated_tokens,
        DAILY_TOKEN_LIMIT,
    )

    raise HTTPException(
        status_code=429,
        detail="Превышен дневной лимит токенов",
    )


# --------------------------------------------------
# Health check
# --------------------------------------------------

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


# --------------------------------------------------
# News list
# --------------------------------------------------

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


# --------------------------------------------------
# Single news item
# --------------------------------------------------

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


# --------------------------------------------------
# Events
# --------------------------------------------------

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


# --------------------------------------------------
# Model result
# --------------------------------------------------

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


# --------------------------------------------------
# Generate request
# --------------------------------------------------

class GenerateRequest(BaseModel):
    topic: str


# --------------------------------------------------
# Generate digest with limits and spend alerts
# --------------------------------------------------

@app.post("/api/generate", status_code=201)
def generate_result(
    request: GenerateRequest,
    x_user_id: str = Header(default="demo-user"),
):
    user_id = x_user_id.strip()

    if not user_id or len(user_id) > 128:
        raise HTTPException(
            status_code=400,
            detail="Некорректный X-User-ID",
        )

    with tracer.start_as_current_span("digest.generate") as generation_span:
        generation_span.set_attribute(
            "digest.topic",
            request.topic,
        )

        generation_span.set_attribute(
            "user.id",
            user_id,
        )

        estimated_tokens = max(
            1,
            len(request.topic) // 4,
        ) + 500

        # Check daily spending budget before generation.
        check_spend_alert(
            user_id,
            estimated_tokens,
        )

        # Reserve daily request and token usage.
        reserve_daily_usage(
            user_id,
            estimated_tokens,
        )

        with tracer.start_as_current_span("model.generate") as model_span:
            model_span.set_attribute(
                "model.operation",
                "generate_digest",
            )

            result = generate_digest(request.topic)

            model_span.set_attribute(
                "model.name",
                str(result.get("model_name", "unknown")),
            )

        actual_tokens = estimate_tokens(result)

        token_difference = (
            actual_tokens - estimated_tokens
        )

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE model_usage
                    SET token_count = GREATEST(
                        0,
                        token_count + %s
                    ),
                    updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                      AND usage_date = CURRENT_DATE
                    """,
                    (
                        token_difference,
                        user_id,
                    ),
                )

        # Update the demonstration spend metric after generation.
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT COALESCE(SUM(token_count), 0) AS total_tokens
                    FROM model_usage
                    WHERE usage_date = CURRENT_DATE
                    """
                )

                usage = cursor.fetchone()

        daily_spend = estimate_cost_usd(
            int(usage["total_tokens"])
        )

        MODEL_ESTIMATED_SPEND.set(daily_spend)

        warning_threshold = (
            DAILY_SPEND_LIMIT_USD * SPEND_ALERT_THRESHOLD
        )

        if daily_spend >= warning_threshold:
            MODEL_SPEND_ALERTS.inc()

            logger.warning(
                "model_spend_alert user_id=%s "
                "estimated_spend_usd=%.6f "
                "warning_threshold_usd=%.6f",
                user_id,
                daily_spend,
                warning_threshold,
            )

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

        generation_span.set_attribute(
            "database.record_id",
            saved_result["id"],
        )

        generation_span.set_attribute(
            "model.estimated_tokens",
            estimated_tokens,
        )

        generation_span.set_attribute(
            "model.actual_tokens_estimate",
            actual_tokens,
        )

        generation_span.set_attribute(
            "model.estimated_cost_usd",
            daily_spend,
        )

    return {
        "id": saved_result["id"],
        "model_name": saved_result["model_name"],
        "topic": request.topic,
        "result": result,
        "estimated_tokens": actual_tokens,
        "estimated_cost_usd": estimate_cost_usd(actual_tokens),
        "daily_estimated_spend_usd": daily_spend,
        "created_at": saved_result["created_at"],
    }
