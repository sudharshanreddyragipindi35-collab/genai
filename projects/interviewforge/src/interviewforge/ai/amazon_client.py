"""Bounded MCP retrieval and source validation."""

import asyncio
import json


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
    from interviewforge.ai.rag import rag_context

    return rag_context(settings, question)
