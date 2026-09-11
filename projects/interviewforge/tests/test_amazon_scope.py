import asyncio
from types import SimpleNamespace

import pytest

from interviewforge.ai.amazon_scope import enforce_amazon_scope
from interviewforge.ai.mcp_knowledge import AmazonKnowledgeMCP


def test_scope_guard_allows_amazon_and_rejects_named_competitor():
    assert enforce_amazon_scope("Help with Amazon coding interviews").allowed
    decision = enforce_amazon_scope("Compare Amazon with Google")
    assert not decision.allowed
    assert decision.detected_company == "Google"


def test_mcp_adapter_hard_codes_amazon_and_accepts_validated_evidence():
    class Session:
        async def call_tool(self, name, arguments=None, read_timeout_seconds=None):
            assert name == "amazon_search"
            assert arguments == {"company": "amazon", "query": "leadership principles"}
            assert read_timeout_seconds == 10.0
            return SimpleNamespace(
                is_error=False,
                structured_content={
                    "company": "Amazon",
                    "answer_context": "Reviewed Amazon evidence",
                    "source_ids": ["source-1"],
                },
            )

    knowledge = asyncio.run(
        AmazonKnowledgeMCP(Session(), tool_name="amazon_search").search("leadership principles")
    )
    assert knowledge.company == "Amazon"


def test_mcp_adapter_rejects_cross_company_data():
    class Session:
        async def call_tool(self, name, arguments=None, read_timeout_seconds=None):
            return SimpleNamespace(
                is_error=False,
                structured_content={
                    "company": "Microsoft",
                    "answer_context": "Wrong company",
                    "source_ids": ["source-2"],
                },
            )

    with pytest.raises(RuntimeError, match="out-of-scope"):
        asyncio.run(AmazonKnowledgeMCP(Session()).search("interview process"))
