"""Amazon-scoped adapter around an MCP company-knowledge tool."""

from dataclasses import dataclass
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class MCPToolSession(Protocol):
    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        read_timeout_seconds: float | None = None,
    ) -> Any: ...


class AmazonKnowledge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: str
    answer_context: str = Field(min_length=1, max_length=20_000)
    source_ids: list[str] = Field(min_length=1, max_length=20)


@dataclass(frozen=True)
class AmazonKnowledgeMCP:
    session: MCPToolSession
    tool_name: str = "search_amazon_company_knowledge"
    timeout_seconds: float = 10.0

    async def search(self, query: str) -> AmazonKnowledge:
        """Call MCP with a fixed company and validate the returned company boundary."""
        result = await self.session.call_tool(
            self.tool_name,
            {"company": "amazon", "query": query},
            read_timeout_seconds=self.timeout_seconds,
        )
        if getattr(result, "is_error", False):
            raise RuntimeError("Amazon knowledge service could not complete the request")
        try:
            knowledge = AmazonKnowledge.model_validate(result.structured_content)
        except (AttributeError, ValidationError) as exc:
            raise RuntimeError("Amazon knowledge service returned an invalid result") from exc
        if knowledge.company.casefold() != "amazon":
            raise RuntimeError("Amazon knowledge service returned out-of-scope company data")
        return knowledge
