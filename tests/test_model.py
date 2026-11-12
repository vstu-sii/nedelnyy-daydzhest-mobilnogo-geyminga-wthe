from backend.app.model import generate_digest


def test_generate_digest_returns_expected_fields():
    result = generate_digest("PUBG Mobile")

    assert "model_name" in result
    assert "summary" in result
    assert "highlights" in result


def test_generate_digest_uses_requested_topic():
    result = generate_digest("PUBG Mobile")

    assert result["model_name"] == "local-demo-model"
    assert "PUBG Mobile" in result["summary"]


def test_generate_digest_has_three_highlights():
    result = generate_digest("Minecraft")

    assert len(result["highlights"]) == 3