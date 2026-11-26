CREATE TABLE IF NOT EXISTS model_usage (
    user_id TEXT NOT NULL,
    usage_date DATE NOT NULL DEFAULT CURRENT_DATE,

    request_count INTEGER NOT NULL DEFAULT 0
        CHECK (request_count >= 0),

    token_count BIGINT NOT NULL DEFAULT 0
        CHECK (token_count >= 0),

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, usage_date)
);

CREATE INDEX IF NOT EXISTS idx_model_usage_date
    ON model_usage(usage_date);