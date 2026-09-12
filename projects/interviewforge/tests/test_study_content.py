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
