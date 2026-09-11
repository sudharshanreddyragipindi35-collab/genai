"""Inspectable GenAI capability map used by the app and future orchestration."""

from dataclasses import dataclass
from enum import StrEnum


class CapabilityStatus(StrEnum):
    FOUNDATION = "Foundation ready"
    PHASE_2 = "Phase 2"
    PHASE_4 = "Phase 4"


@dataclass(frozen=True)
class AgentDefinition:
    name: str
    purpose: str
    status: CapabilityStatus


@dataclass(frozen=True)
class AICapability:
    name: str
    purpose: str
    status: CapabilityStatus


AGENT_TEAM = (
    AgentDefinition(
        "Coach supervisor",
        "Plans multi-step learning sessions and delegates bounded work to specialists.",
        CapabilityStatus.PHASE_2,
    ),
    AgentDefinition(
        "Knowledge verifier",
        "Checks company claims against approved, current source evidence and can abstain.",
        CapabilityStatus.PHASE_2,
    ),
    AgentDefinition(
        "Learning strategist",
        "Explains roadmap priorities from mastery evidence, time and prerequisites.",
        CapabilityStatus.PHASE_2,
    ),
    AgentDefinition(
        "Code reviewer",
        "Uses immutable source and sandbox results to explain errors and trade-offs.",
        CapabilityStatus.PHASE_2,
    ),
    AgentDefinition(
        "Interview conductor",
        "Runs role-specific interview state machines and chooses targeted follow-ups.",
        CapabilityStatus.PHASE_4,
    ),
    AgentDefinition(
        "Evaluation critic",
        "Scores agent outputs against versioned rubrics before model or prompt releases.",
        CapabilityStatus.PHASE_2,
    ),
)


AI_CAPABILITIES = (
    AICapability(
        "Deep Agents and LangGraph",
        "Durable planning, specialist delegation, streaming and human review checkpoints.",
        CapabilityStatus.FOUNDATION,
    ),
    AICapability(
        "Hybrid RAG",
        "Metadata filtering plus lexical and vector retrieval, reranking and cited answers.",
        CapabilityStatus.PHASE_2,
    ),
    AICapability(
        "Context engineering",
        "Candidate state, retrieved evidence, conversation summaries and token budgets.",
        CapabilityStatus.PHASE_2,
    ),
    AICapability(
        "Structured generation",
        "Schema-validated tool calls, rubric results, citations and safe failure handling.",
        CapabilityStatus.PHASE_2,
    ),
    AICapability(
        "Learning intelligence",
        "Evidence-weighted mastery, spaced repetition and calibrated ML recommendations.",
        CapabilityStatus.PHASE_2,
    ),
    AICapability(
        "Evaluation and observability",
        "Golden datasets, retrieval metrics, leakage checks, traces, latency and cost.",
        CapabilityStatus.FOUNDATION,
    ),
)
