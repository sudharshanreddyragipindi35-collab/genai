from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from interviewforge.ai.leetcode_mcp import parse_problem_result
from interviewforge.amazon_content import REPORTS
from interviewforge.app import create_app
from interviewforge.config import Settings
from interviewforge.roadmap import PracticeProblem, apply_mcp_problems, build_roadmap, complete_task


def make_roadmap():
    today = date(2026, 9, 12)
    return build_roadmap(
        name="Sudharshan",
        experience="1–3 years",
        hours_per_day=2,
        target_date=today + timedelta(days=45),
        today=today,
    )


def test_roadmap_has_three_ordered_levels_and_assessment_gate():
    roadmap = make_roadmap()
    assert [level.number for level in roadmap.levels] == [1, 2, 3]
    assert roadmap.level_unlocked(1)
    assert not roadmap.level_unlocked(2)
    assert not roadmap.assessment_unlocked

    for task in roadmap.levels[0].tasks:
        complete_task(roadmap, task.id)
    assert roadmap.level_unlocked(2)


def test_locked_level_cannot_be_completed_early():
    roadmap = make_roadmap()
    with pytest.raises(PermissionError):
        complete_task(roadmap, roadmap.levels[1].tasks[0].id)


def test_assessment_and_interview_unlock_in_sequence(tmp_path):
    config = Settings(_env_file=None, local_state_path=tmp_path / "state.json")
    roadmap = make_roadmap()
    problem = PracticeProblem(
        **REPORTS["SDE I"][0],
        url="https://leetcode.com/problems/intersection-of-two-arrays-ii/",
        source="leetcode_mcp",
    )
    apply_mcp_problems(roadmap, [[problem]])
    config.local_state_path.write_text(roadmap.model_dump_json(), encoding="utf-8")
    with TestClient(create_app(config)) as client:
        assert client.post("/assessment/complete").status_code == 409
        for level in roadmap.levels:
            for task in level.tasks:
                response = client.post(f"/roadmap/tasks/{task.id}/complete", follow_redirects=False)
                assert response.status_code == 303
        page = client.get("/roadmap")
        assert "Open assessment" in page.text
        assert client.post("/assessment/complete", follow_redirects=False).status_code == 303
        assert "Ready to schedule" in client.get("/roadmap").text


def test_leetcode_mcp_result_is_converted_to_validated_public_links():
    result = {
        "questions": [
            {"title": "Two Sum", "titleSlug": "intersection-of-two-arrays-ii", "difficulty": "EASY"}
        ]
    }
    problems = parse_problem_result(result)
    assert len(problems) == 1
    assert problems[0].source == "leetcode_mcp"
    assert problems[0].url == "https://leetcode.com/problems/intersection-of-two-arrays-ii/"


def test_unlocked_problem_has_embedded_contextual_coach(tmp_path):
    config = Settings(_env_file=None, local_state_path=tmp_path / "state.json")
    roadmap = make_roadmap()
    problem = PracticeProblem(
        **REPORTS["SDE I"][0],
        url="https://leetcode.com/problems/intersection-of-two-arrays-ii/",
        source="leetcode_mcp",
    )
    apply_mcp_problems(roadmap, [[problem]])
    for task in roadmap.levels[0].tasks:
        complete_task(roadmap, task.id)
    config.local_state_path.write_text(roadmap.model_dump_json(), encoding="utf-8")
    with TestClient(create_app(config)) as client:
        page = client.get("/practice?problem=intersection-of-two-arrays-ii")
        assert "Discuss Intersection of Two Arrays II" in page.text
        response = client.post(
            "/practice/coach",
            data={
                "problem_slug": "intersection-of-two-arrays-ii",
                "question": "Give me the first hint",
            },
        )
    assert response.status_code == 200
    assert "Give me the first hint" in response.text
    assert "Claude is not connected yet" in response.text


def test_locked_problem_cannot_be_sent_to_coach(tmp_path):
    config = Settings(_env_file=None, local_state_path=tmp_path / "state.json")
    roadmap = make_roadmap()
    problem = PracticeProblem(
        **REPORTS["SDE I"][0],
        url="https://leetcode.com/problems/intersection-of-two-arrays-ii/",
        source="leetcode_mcp",
    )
    apply_mcp_problems(roadmap, [[problem]])
    for task in roadmap.levels[0].tasks:
        complete_task(roadmap, task.id)
    config.local_state_path.write_text(roadmap.model_dump_json(), encoding="utf-8")
    with TestClient(create_app(config)) as client:
        response = client.post(
            "/practice/coach",
            data={"problem_slug": "number-of-islands", "question": "Explain this"},
        )
    assert response.status_code == 404


def test_target_date_must_be_in_future():
    with pytest.raises(ValueError, match="after today"):
        build_roadmap(
            name="Candidate",
            experience="Student / fresher",
            hours_per_day=1,
            target_date=date(2026, 9, 12),
            today=date(2026, 9, 12),
        )
