from types import SimpleNamespace

from interviewforge.ai.coach import answer_amazon_question
from interviewforge.config import Settings


def claude_settings():
    return Settings(
        _env_file=None,
        llm_provider="anthropic",
        llm_model="anthropic:claude-sonnet-5",
        ANTHROPIC_API_KEY="test-secret",
    )


def test_live_coach_invokes_deep_agent_with_claude_model():
    captured = {}

    def model_factory(**kwargs):
        captured["model"] = kwargs
        return "claude-model"

    class Agent:
        def invoke(self, payload):
            captured["payload"] = payload
            return {"messages": [SimpleNamespace(content="Amazon coaching response")]}

    def agent_factory(**kwargs):
        captured["agent"] = kwargs
        return Agent()

    answer = answer_amazon_question(
        claude_settings(),
        "Help me improve my Amazon interview answer",
        model_factory=model_factory,
        agent_factory=agent_factory,
    )

    assert answer.live_model
    assert answer.text == "Amazon coaching response"
    assert captured["model"]["model_name"] == "claude-sonnet-5"
    assert captured["model"]["api_key"].get_secret_value() == "test-secret"
    assert captured["agent"]["model"] == "claude-model"
    assert "Amazon-only runtime policy" in captured["payload"]["messages"][0]["content"]


def test_competitor_request_never_constructs_or_invokes_model():
    def forbidden_factory(**kwargs):
        raise AssertionError("The model must not be constructed for a Microsoft request")

    answer = answer_amazon_question(
        claude_settings(),
        "How does Microsoft conduct interviews?",
        model_factory=forbidden_factory,
        agent_factory=forbidden_factory,
    )
    assert not answer.live_model
    assert "current target is Amazon" in answer.text


def test_provider_failure_returns_safe_message():
    def failing_model(**kwargs):
        raise RuntimeError("test-secret must stay private")

    answer = answer_amazon_question(
        claude_settings(),
        "Help with Amazon coding interviews",
        model_factory=failing_model,
    )
    assert not answer.live_model
    assert "test-secret" not in answer.text
    assert "Claude could not complete" in answer.text
