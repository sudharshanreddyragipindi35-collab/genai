"""Bounded MCP retrieval and source validation."""

import asyncio
import json

from interviewforge.amazon_content import SOURCES


async def call_amazon(url, tool, arguments):
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    async with asyncio.timeout(25):
        async with streamable_http_client(url) as streams:
            async with ClientSession(*streams[:2]) as session:
                await session.initialize()
                result = await session.call_tool(tool, arguments)
                if getattr(result, "is_error", False) or getattr(result, "isError", False):
                    raise ValueError("MCP tool failed")
                structured = getattr(result, "structured_content", None) or getattr(
                    result, "structuredContent", None
                )
                if structured:
                    return structured
                return json.loads(
                    next(
                        block.text
                        for block in result.content
                        if getattr(block, "type", "") == "text"
                    )
                )


def knowledge_context(settings, question):
    if not settings.amazon_mcp_server_url:
        return "", ()
    try:
        data = asyncio.run(
            call_amazon(
                settings.amazon_mcp_server_url,
                settings.amazon_mcp_tool,
                {"company": "amazon", "query": question},
            )
        )
        if data.get("company") != "amazon":
            raise ValueError("Wrong company")
        allowed = {url for _, url in SOURCES.values()}
        sources = [
            s
            for s in data.get("sources", [])
            if s.get("url") in allowed and s.get("text") and s.get("retrieved_at")
        ]
        context = "\n\n".join(
            f"Source: {s['url']} (retrieved {s['retrieved_at']})\n{s['text'][:12000]}"
            for s in sources
        )
        return context, tuple(s["url"] for s in sources)
    except Exception:
        return "", ()
