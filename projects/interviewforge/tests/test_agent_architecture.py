import sys
from types import SimpleNamespace

from interviewforge.ai.architecture import AGENT_TEAM, AI_CAPABILITIES
from interviewforge.ai.deep_agent import SUBAGENTS, create_coach_agent


def test_capability_map_has_agentic_rag_ml_and_evaluation_layers():
    concepts = " ".join(item.name for item in AI_CAPABILITIES)
    roles = {agent.name for agent in AGENT_TEAM}
    assert "Deep Agents" in concepts
    assert "Hybrid RAG" in concepts
    assert "Learning intelligence" in concepts
    assert "Evaluation and observability" in concepts
    assert {"Coach supervisor", "Knowledge verifier", "Code reviewer"} <= roles


def test_deep_agent_factory_passes_bounded_specialists(monkeypatch):
    captured = {}

    def fake_create_deep_agent(**kwargs):
        captured.update(kwargs)
        return "coach-graph"

    monkeypatch.setitem(
        sys.modules,
        "deepagents",
        SimpleNamespace(create_deep_agent=fake_create_deep_agent),
    )
    graph = create_coach_agent("provider:model")
    assert graph == "coach-graph"
    assert captured["model"] == "provider:model"
    assert captured["tools"] == []
    assert captured["subagents"] == SUBAGENTS
    assert all(agent["tools"] == [] for agent in captured["subagents"])
