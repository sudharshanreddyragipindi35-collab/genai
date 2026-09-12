"""Amazon coach invocation boundary for live Claude responses."""

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import SecretStr

from interviewforge.ai.amazon_client import knowledge_context
from interviewforge.ai.amazon_scope import enforce_amazon_scope
from interviewforge.ai.deep_agent import create_coach_agent
from interviewforge.config import Settings

logger = logging.getLogger("interviewforge.ai")


@dataclass(frozen=True)
class CoachAnswer:
    text: str
    kind: Literal["live", "policy", "offline", "error"]
    model: str | None = None

    @property
    def live_model(self) -> bool:
        return self.kind == "live"


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
            text=decision.message or "This company is outside the Amazon target.", kind="policy"
        )

    if not settings.claude_ready:
        return CoachAnswer(
            text=(
                "Claude is not connected yet. Add the Anthropic API key to the local .env file "
                "and restart InterviewForge. Your question has not been sent anywhere."
            ),
            kind="offline",
        )

    if model_factory is None:
        from langchain_anthropic import ChatAnthropic

        model_factory = ChatAnthropic
    if agent_factory is None:
        agent_factory = create_coach_agent

    evidence, _source_urls = knowledge_context(settings, question)
    request_context = json.dumps(
        {
            "context_label": "Amazon-only runtime policy",
            "evidence_status": "available" if evidence else "unavailable",
            "official_document_excerpts": evidence,
            "candidate_request": question,
        },
        ensure_ascii=False,
    )
    model_id = settings.llm_model.removeprefix("anthropic:")
    try:
        model = model_factory(
            model_name=model_id,
            api_key=SecretStr(settings.anthropic_api_key.get_secret_value()),
            timeout=30.0,
            max_retries=2,
        )
        agent = agent_factory(model=model)
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": request_context,
                    }
                ]
            }
        )
        messages = result.get("messages", [])
        text = _message_text(messages[-1]) if messages else ""
        if not text:
            raise RuntimeError("Claude returned no displayable message")
    except Exception as exc:
        logger.warning(
            json.dumps({"event": "claude_invocation_failed", "error_type": type(exc).__name__})
        )
        return CoachAnswer(
            text=(
                "Claude could not complete this request. Check the local key, model access, "
                "network connection, and API balance, then try again."
            ),
            kind="error",
            model=settings.llm_model,
        )
    return CoachAnswer(text=text, kind="live", model=settings.llm_model)
