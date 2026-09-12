from datetime import date, timedelta

from fastapi.testclient import TestClient

from interviewforge.app import create_app
from interviewforge.config import Settings
from interviewforge.roadmap import build_roadmap
from interviewforge.state import RoadmapStore


def test_first_lesson_visible_without_mcp_sync_or_external_links(tmp_path):
    settings = Settings(
        _env_file=None, environment="test", local_state_path=tmp_path / "state.json"
    )
    roadmap = build_roadmap(
        name="Learner",
        experience="Student / fresher",
        hours_per_day=1,
        target_date=date.today() + timedelta(days=30),
    )
    RoadmapStore(settings.local_state_path).save(roadmap)
    with TestClient(create_app(settings)) as client:
        result = client.get("/practice")
        assert result.status_code == 200
        assert "Understand the problem" in result.text
        assert "<table>" in result.text
        assert 'class="language-python"' in result.text
        assert 'href="https://' not in result.text
        result = client.post(
            "/practice/lesson-coach",
            data={"task_id": roadmap.levels[1].tasks[0].id, "question": "Explain"},
        )
        assert result.status_code == 404


def test_more_generates_only_on_click_with_profile_and_saves(tmp_path, monkeypatch):
    from interviewforge.ai.coach import CoachAnswer

    settings = Settings(
        _env_file=None, environment="test", local_state_path=tmp_path / "state.json"
    )
    plan = build_roadmap(
        name="Learner",
        experience="3 years",
        role="SDE II",
        skill="intermediate",
        hours_per_day=2,
        target_date=date.today() + timedelta(days=20),
    )
    RoadmapStore(settings.local_state_path).save(plan)
    task_id = plan.levels[0].tasks[0].id
    calls = []

    def fake(settings, prompt):
        calls.append(prompt)
        return CoachAnswer("## Detailed worked example\n\nPersonalized content.", "live")

    monkeypatch.setattr("interviewforge.ui.answer_amazon_question", fake)
    with TestClient(create_app(settings)) as client:
        page = client.get("/practice")
        assert "More detail" in page.text
        assert not calls
        assert "roadmap.css?v=" in page.text
        response = client.post("/practice/more", data={"task_id": task_id})
        assert response.status_code == 200
        assert "<h2>Detailed worked example</h2>" in response.text
        assert "SDE II" in calls[0] and "3 years" in calls[0]
        assert str(plan.target_date) in calls[0] and "2 hours/day" in calls[0]
        client.post("/practice/more", data={"task_id": task_id})
        assert len(calls) == 1
        locked = client.post("/practice/more", data={"task_id": plan.levels[1].tasks[0].id})
        assert locked.status_code == 404
        assert len(calls) == 1
