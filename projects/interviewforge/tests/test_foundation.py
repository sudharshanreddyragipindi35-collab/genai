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


def test_basic_application_pages_are_visible():
    config = Settings(_env_file=None)
    with TestClient(create_app(config)) as client:
        dashboard = client.get("/")
        assert dashboard.status_code == 200
        assert "Good evening, Sudharshan" in dashboard.text
        assert "Start today’s practice" in dashboard.text

        practice = client.get("/practice")
        assert practice.status_code == 200
        assert "Two Sum" in practice.text
        assert "Code runner comes in Phase 2" in practice.text


def test_onboarding_builds_an_explicit_unsaved_preview():
    config = Settings(_env_file=None)
    with TestClient(create_app(config)) as client:
        response = client.post(
            "/onboarding",
            data={
                "name": "Sudharshan",
                "experience": "1–3 years",
                "hours_per_day": "2",
                "target_date": "2026-10-30",
            },
        )
    assert response.status_code == 200
    assert "Preview created for Sudharshan" in response.text
    assert "This has not been saved yet" in response.text
