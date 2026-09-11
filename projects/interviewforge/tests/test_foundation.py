import json
import logging
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from interviewforge.app import create_app
from interviewforge.config import Settings, load_settings


def settings():
    return Settings(
        _env_file=None,
        database_url="postgresql+psycopg://user:secret@127.0.0.1:1/test",
        db_connect_timeout=1,
    )


def test_application_can_start_without_database_configuration(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("INTERVIEWFORGE_DATABASE_URL", raising=False)
    config = load_settings()
    assert config.database_url is None
    with TestClient(create_app(config)) as client:
        assert client.get("/").status_code == 200
        assert client.get("/ready").json()["database"] == "not_configured"


def test_claude_provider_configuration_is_supported():
    config = Settings(
        _env_file=None,
        llm_provider="anthropic",
        llm_model="anthropic:claude-sonnet-5",
    )
    assert config.llm_provider == "anthropic"
    assert config.llm_model == "anthropic:claude-sonnet-5"


def test_invalid_configuration_does_not_expose_secret(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("INTERVIEWFORGE_DATABASE_URL", "invalid-super-secret")
    with pytest.raises(RuntimeError) as result:
        load_settings()
    assert "super-secret" not in str(result.value)


def test_health_survives_real_database_outage():
    with TestClient(create_app(settings())) as client:
        assert client.get("/health").status_code == 200
        response = client.get("/ready")
        assert response.status_code == 503
        assert response.json()["trace_id"] == response.headers["X-Trace-ID"]
        assert "secret" not in response.text


def test_ready_queries_database_and_lifespan_disposes_engine(monkeypatch):
    engine = MagicMock()
    monkeypatch.setattr("interviewforge.app.create_engine", lambda *a, **kw: engine)
    with TestClient(create_app(settings())) as client:
        assert client.get("/ready").json() == {"status": "ready", "database": "available"}
        connection = engine.connect.return_value.__enter__.return_value
        assert str(connection.execute.call_args.args[0]) == "SELECT 1"
    engine.dispose.assert_called_once()


def test_unhandled_errors_are_correlated_and_redacted(caplog):
    app = create_app(settings())

    @app.get("/broken")
    def broken():
        raise RuntimeError("private-password")

    with caplog.at_level(logging.INFO, logger="interviewforge"):
        with TestClient(app) as client:
            response = client.get("/broken?token=private-token")
    assert response.status_code == 500
    trace_id = response.headers["X-Trace-ID"]
    assert response.json()["trace_id"] == trace_id
    assert "private" not in response.text + caplog.text
    event = json.loads(next(r.message for r in caplog.records if r.name == "interviewforge"))
    assert event["trace_id"] == trace_id


def test_production_hides_api_documentation():
    config = settings().model_copy(update={"environment": "production"})
    with TestClient(create_app(config)) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404


def test_basic_application_pages_are_visible(tmp_path):
    config = Settings(_env_file=None, local_state_path=tmp_path / "state.json")
    with TestClient(create_app(config)) as client:
        dashboard = client.get("/")
        assert dashboard.status_code == 200
        assert "Start with your interview date" in dashboard.text
        assert "Choose Amazon" in dashboard.text

        practice = client.get("/practice")
        assert practice.status_code == 200
        assert "Amazon-reported coding practice" in practice.text
        assert "Create your Amazon roadmap first" in practice.text

        coach = client.get("/coach")
        assert coach.status_code == 200
        assert "AMAZON INTERVIEW COACH" in coach.text
        assert "Current target: Amazon" in coach.text


def test_coach_rejects_other_company_before_llm_call():
    with TestClient(create_app(Settings(_env_file=None))) as client:
        response = client.post("/coach", data={"question": "Explain Microsoft interviews"})
    assert response.status_code == 200
    assert "current target is Amazon" in response.text
    assert "cannot answer questions about Microsoft" in response.text


def test_amazon_question_stays_local_until_integrations_are_configured():
    with TestClient(create_app(Settings(_env_file=None))) as client:
        response = client.post(
            "/coach", data={"question": "How do Amazon leadership principles work?"}
        )
    assert response.status_code == 200
    assert "Claude is not connected yet" in response.text
    assert "has not been sent anywhere" in response.text


def test_coach_status_never_exposes_key():
    config = Settings(
        _env_file=None,
        llm_provider="anthropic",
        llm_model="anthropic:claude-sonnet-5",
        ANTHROPIC_API_KEY="private-claude-key",
    )
    with TestClient(create_app(config)) as client:
        response = client.get("/coach/status")
    assert response.json() == {
        "provider": "anthropic",
        "model": "anthropic:claude-sonnet-5",
        "configured": True,
        "amazon_mcp_configured": False,
        "leetcode_mcp_configured": False,
    }
    assert "private-claude-key" not in response.text


def test_onboarding_saves_roadmap_and_redirects(tmp_path):
    config = Settings(_env_file=None, local_state_path=tmp_path / "state.json")
    with TestClient(create_app(config)) as client:
        response = client.post(
            "/onboarding",
            data={
                "name": "Sudharshan",
                "experience": "1–3 years",
                "hours_per_day": "2",
                "target_date": "2099-10-30",
            },
            follow_redirects=False,
        )
    assert response.status_code == 303
    assert response.headers["location"] == "/roadmap"
    assert "Sudharshan" in (tmp_path / "state.json").read_text(encoding="utf-8")
