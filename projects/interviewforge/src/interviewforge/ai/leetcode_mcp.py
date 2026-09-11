"""Validated Streamable HTTP MCP boundary for public LeetCode problems."""

import json
import re
from typing import Any
from urllib.parse import urlparse

from interviewforge.roadmap import PracticeProblem


def _objects(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _objects(child)


def parse_problem_result(value: Any) -> list[PracticeProblem]:
    if isinstance(value, str):
        value = json.loads(value)
    found: list[PracticeProblem] = []
    seen: set[str] = set()
    for item in _objects(value):
        slug = item.get("titleSlug") or item.get("title_slug") or item.get("slug")
        title = item.get("title")
        raw_difficulty = str(item.get("difficulty", "")).title()
        if (
            not isinstance(slug, str)
            or not isinstance(title, str)
            or re.fullmatch(r"[a-z0-9-]+", slug) is None
        ):
            continue
        if raw_difficulty not in {"Easy", "Medium", "Hard"} or slug in seen:
            continue
        url = f"https://leetcode.com/problems/{slug}/"
        if urlparse(url).hostname != "leetcode.com":
            continue
        found.append(
            PracticeProblem(
                title=title, slug=slug, difficulty=raw_difficulty, url=url, source="leetcode_mcp"
            )
        )
        seen.add(slug)
    return found


async def search_problems(
    server_url: str, tool_name: str, difficulty: str, limit: int = 3
) -> list[PracticeProblem]:
    """Call an explicitly configured MCP server; no credentials are handled here."""
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    async with streamable_http_client(server_url) as streams:
        read, write = streams[:2]
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                tool_name, {"difficulty": difficulty.upper(), "limit": limit}
            )
    texts = [block.text for block in result.content if getattr(block, "type", None) == "text"]
    return parse_problem_result(json.loads(texts[0])) if texts else []
