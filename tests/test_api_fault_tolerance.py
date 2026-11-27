from fastapi.testclient import TestClient
from fastapi import HTTPException

from backend.app import main


def test_model_failure_returns_503_and_releases_usage(monkeypatch):
    released = []

    def fail_model(topic):
        raise RuntimeError("Model unavailable")

    def fake_release(user_id, estimated_tokens):
        released.append((user_id, estimated_tokens))

    monkeypatch.setattr(main, "check_spend_alert", lambda *args: None)
    monkeypatch.setattr(main, "reserve_daily_usage", lambda *args: None)
    monkeypatch.setattr(main, "generate_digest", fail_model)
    monkeypatch.setattr(main, "release_daily_usage", fake_release)

    client = TestClient(main.app)
    response = client.post(
        "/api/generate",
        json={"topic": "PUBG Mobile"},
        headers={"X-User-ID": "fault-test-user"},
    )

    assert response.status_code == 503
    assert released


def test_database_failure_returns_503(monkeypatch):
    def fail_database():
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )

    monkeypatch.setattr(main, "get_connection", fail_database)

    client = TestClient(main.app)
    response = client.get("/api/health")

    assert response.status_code == 503