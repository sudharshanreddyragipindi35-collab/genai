"""InterviewForge-owned MCP bridge to a fixed set of official public Amazon pages."""

import asyncio
from datetime import datetime, timezone
from html.parser import HTMLParser
from time import monotonic
from urllib.request import HTTPRedirectHandler, Request, build_opener

from mcp.server.mcpserver import MCPServer

from interviewforge.amazon_content import REPORTS, SOURCES

server = MCPServer("InterviewForge Amazon public knowledge")
CACHE = {}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class PageText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"}:
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(data.strip())


def fetch_source(key):
    if key in CACHE and monotonic() - CACHE[key][0] < 3600:
        return CACHE[key][1]
    title, url = SOURCES[key]
    with build_opener(NoRedirect).open(
        Request(url, headers={"User-Agent": "InterviewForge/0.1 public interview preparation"}),
        timeout=15,
    ) as response:
        raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("Source exceeds size limit")
    parser = PageText()
    parser.feed(raw.decode("utf-8"))
    text = " ".join(parser.parts)
    if len(text) < 200 or "Amazon" not in text:
        raise ValueError("Source did not contain usable Amazon content")
    result = {
        "title": title,
        "url": url,
        "text": text[:14000],
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }
    CACHE[key] = (monotonic(), result)
    return result


@server.tool()
async def search_amazon_company_knowledge(company: str, query: str) -> dict:
    """Read official Amazon LP, coding, interview-loop and SDE role preparation pages."""
    if company.casefold() != "amazon":
        raise ValueError("Only Amazon is supported")
    q = query.lower()
    keys = ["lp", "sde2" if "sde ii" in q or "sde2" in q else "coding"]
    if "university" in q or "sde i " in q:
        keys[1] = "sde1"
    results = await asyncio.gather(
        *(asyncio.to_thread(fetch_source, key) for key in keys), return_exceptions=True
    )
    sources = [item for item in results if isinstance(item, dict)]
    return {
        "company": "amazon",
        "sources": sources,
        "status": "retrieved" if sources else "unavailable",
    }


@server.tool()
def amazon_reported_coding_questions(role: str) -> dict:
    """Return the reviewed Amazon interview-report registry, not live company tags."""
    if role not in REPORTS:
        raise ValueError("Unsupported role")
    return {
        "company": "amazon",
        "role": role,
        "problems": REPORTS[role],
        "evidence": "community reports; no official confirmation",
    }


if __name__ == "__main__":
    server.run(transport="streamable-http", host="127.0.0.1", port=3001)
