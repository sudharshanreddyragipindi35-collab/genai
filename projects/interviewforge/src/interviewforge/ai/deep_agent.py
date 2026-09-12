"""Deep Agents factory. Importing this module never triggers a model call."""

from collections.abc import Callable, Sequence
from typing import Any

from interviewforge.ai.prompts import SPECIALIST_PROMPTS, SUPERVISOR_PROMPT

SUBAGENTS: list[dict[str, Any]] = [
    {
        "name": name,
        "description": description,
        "system_prompt": SPECIALIST_PROMPTS[name],
        "tools": [],
    }
    for name, description in [
        ("knowledge-verifier", "Check Amazon company claims against supplied evidence."),
        ("learning-strategist", "Recommend practice using role, skills and time constraints."),
        ("code-reviewer", "Review Python logic and explain concrete errors."),
        ("evaluation-critic", "Check a draft for accuracy, evidence and readability."),
    ]
]


def create_coach_agent(model: Any, tools: Sequence[Callable[..., Any]] = ()) -> Any:
    """Build the provider-neutral coach with isolated specialist subagents."""
    try:
        from deepagents import create_deep_agent
    except ImportError as exc:
        raise RuntimeError(
            "Agent dependencies are not installed. Run `uv sync --extra agents --locked`."
        ) from exc

    return create_deep_agent(
        model=model,
        tools=list(tools),
        system_prompt=SUPERVISOR_PROMPT,
        subagents=SUBAGENTS,
    )
