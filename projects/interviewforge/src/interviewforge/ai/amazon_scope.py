"""Deterministic company boundary applied before any model or retrieval call."""

import re
from dataclasses import dataclass

TARGET_COMPANY = "Amazon"
OUT_OF_SCOPE_COMPANIES = (
    "Microsoft",
    "Google",
    "Meta",
    "Facebook",
    "Apple",
    "Netflix",
    "Adobe",
    "Oracle",
    "Salesforce",
    "Uber",
)


@dataclass(frozen=True)
class ScopeDecision:
    allowed: bool
    message: str | None = None
    detected_company: str | None = None


def enforce_amazon_scope(question: str) -> ScopeDecision:
    """Reject explicit requests about companies outside the configured target."""
    for company in OUT_OF_SCOPE_COMPANIES:
        if re.search(rf"\b{re.escape(company)}\b", question, flags=re.IGNORECASE):
            return ScopeDecision(
                allowed=False,
                detected_company=company,
                message=(
                    "Your current target is Amazon, so I can only help with Amazon interview "
                    f"preparation. I cannot answer questions about {company}."
                ),
            )
    return ScopeDecision(allowed=True)
