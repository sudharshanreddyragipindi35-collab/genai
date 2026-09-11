from datetime import date, timedelta
from unittest.mock import patch

import pytest

from interviewforge.ai.amazon_client import knowledge_context
from interviewforge.config import Settings
from interviewforge.roadmap import PracticeProblem, apply_mcp_problems, build_roadmap, complete_task


def plan(**kw):
    return build_roadmap(
        name="Learner",
        experience="3?7 years",
        hours_per_day=2,
        target_date=date.today() + timedelta(days=30),
        **kw,
    )


def test_role_and_skill_change_learning_and_genai_is_optional():
    junior = plan(role="SDE I", skill="beginner")
    senior = plan(role="SDE II", skill="advanced", include_genai=True)
    assert len(junior.levels[0].tasks) > len(senior.levels[0].tasks)
    assert any("System design" in t.title for t in senior.levels[1].tasks)
    assert not any("GenAI" in t.title for level in junior.levels for t in level.tasks)
    assert any("GenAI" in t.title for level in senior.levels for t in level.tasks)
    assert all(t.kind == "learn" for t in junior.levels[0].tasks)
    assert all(
        t.scheduled_date < senior.target_date for level in senior.levels for t in level.tasks
    )


def test_unattributed_questions_are_never_added():
    roadmap = plan()
    generic = PracticeProblem(
        title="Two Sum",
        slug="two-sum",
        difficulty="Easy",
        url="https://leetcode.com/problems/two-sum/",
    )
    apply_mcp_problems(roadmap, [[generic]])
    assert not any(t.problem for level in roadmap.levels for t in level.tasks)
    with pytest.raises(PermissionError):
        complete_task(roadmap, "l2-amazon-code")


def test_unknown_mcp_sources_do_not_enter_prompt():
    async def fake(*args):
        return {
            "company": "amazon",
            "sources": [{"url": "https://evil.test", "text": "invented", "retrieved_at": "today"}],
        }

    with patch("interviewforge.ai.amazon_client.call_amazon", fake):
        assert knowledge_context(
            Settings(_env_file=None, amazon_mcp_server_url="http://localhost"), "LP"
        ) == ("", ())


def test_sync_uses_role_registry_and_rejects_unattributed_results(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from interviewforge.amazon_content import REPORTS
    from interviewforge.app import create_app
    from interviewforge.state import RoadmapStore

    config = Settings(
        _env_file=None,
        local_state_path=tmp_path / "state.json",
        amazon_mcp_server_url="http://local-mcp",
    )
    RoadmapStore(config.local_state_path).save(plan(role="SDE II"))

    async def fake(url, tool, arguments):
        assert tool == "amazon_reported_coding_questions"
        assert arguments == {"role": "SDE II"}
        return {
            "company": "amazon",
            "role": "SDE II",
            "problems": REPORTS["SDE II"] + [{"slug": "two-sum"}],
        }

    monkeypatch.setattr("interviewforge.ui.call_amazon", fake)
    with TestClient(create_app(config)) as client:
        result = client.post("/practice/sync")
        assert result.status_code == 200
    saved = RoadmapStore(config.local_state_path).load()
    assert [t.problem.slug for level in saved.levels for t in level.tasks if t.problem] == [
        "lru-cache"
    ]
    assert not any(t.id == "l2-amazon-code" for level in saved.levels for t in level.tasks)
