"""Amazon coach invocation boundary for live Claude responses."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import SecretStr

from interviewforge.ai.amazon_scope import enforce_amazon_scope
from interviewforge.ai.deep_agent import create_coach_agent
from interviewforge.config import Settings


@dataclass(frozen=True)
class CoachAnswer:
    text: str
    live_model: bool
    model: str | None = None


def _message_text(message: Any) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
            elif isinstance(getattr(block, "text", None), str):
                parts.append(block.text)
        return "\n".join(parts).strip()
    return ""


def answer_amazon_question(
    settings: Settings,
    question: str,
    *,
    model_factory: Callable[..., Any] | None = None,
    agent_factory: Callable[..., Any] | None = None,
) -> CoachAnswer:
    """Apply scope first, then invoke Claude through the Deep Agents supervisor."""
    decision = enforce_amazon_scope(question)
    if not decision.allowed:
        return CoachAnswer(
            text=decision.message or "This company is outside the Amazon target.", live_model=False
        )

    if not settings.claude_ready:
        return CoachAnswer(
            text=(
                "Claude is not connected yet. Add the Anthropic API key to the local .env file "
                "and restart InterviewForge. Your question has not been sent anywhere."
            ),
            live_model=False,
        )

    if model_factory is None:
        from langchain_anthropic import ChatAnthropic

        model_factory = ChatAnthropic
    if agent_factory is None:
        agent_factory = create_coach_agent

    model_id = settings.llm_model.removeprefix("anthropic:")
    try:
        model = model_factory(
            model_name=model_id,
            api_key=SecretStr(settings.anthropic_api_key.get_secret_value()),
            timeout=30.0,
            max_retries=1,
        )
        agent = agent_factory(model=model)
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Amazon-only runtime policy: no reviewed MCP evidence is currently "
                            "attached. Give general coaching only. Do not claim current Amazon "
                            "process facts or answer for another company.\n\n"
                            f"Candidate question:\n{question}"
                        ),
                    }
                ]
            }
        )
        messages = result.get("messages", [])
        text = _message_text(messages[-1]) if messages else ""
        if not text:
            raise RuntimeError("Claude returned no displayable message")
    except Exception:
        return CoachAnswer(
            text=(
                "Claude could not complete this request. Check the local key, model access, "
                "network connection, and API balance, then try again."
            ),
            live_model=False,
            model=settings.llm_model,
        )
    return CoachAnswer(text=text, live_model=True, model=settings.llm_model)
