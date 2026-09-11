"""Local lexical RAG over versioned, approved official Amazon documents.

The corpus contains public source text only. It never learns from chat messages.
"""

import asyncio
import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

from interviewforge.amazon_content import SOURCES

LOCK = RLock()
STOP = set(
    "a an and are as at be by for from how i in is it me my of on or our the their this to we with you your amazon explain".split()
)


def tokens(text):
    return [
        word
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if word not in STOP and len(word) > 1
    ]


def read_corpus(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("version") == 1:
            return data
    except (OSError, ValueError):
        pass
    return {"version": 1, "sources": [], "refreshed_at": None}


def valid_sources(sources):
    allowed = {url for _, url in SOURCES.values()}
    result = []
    seen = set()
    for source in sources:
        try:
            stamp = datetime.fromisoformat(source["retrieved_at"])
            text = source["text"]
            url = source["url"]
            if (
                url not in allowed
                or url in seen
                or not isinstance(text, str)
                or len(text) < 200
                or not stamp.tzinfo
            ):
                continue
            if stamp > datetime.now(timezone.utc):
                continue
            result.append(
                {
                    "url": url,
                    "title": dict((u, t) for t, u in SOURCES.values())[url],
                    "text": text[:20000],
                    "retrieved_at": stamp.isoformat(),
                    "sha256": hashlib.sha256(text[:20000].encode()).hexdigest(),
                }
            )
            seen.add(url)
        except (KeyError, TypeError, ValueError):
            continue
    return result


def refresh(settings, force=False):
    from interviewforge.ai.amazon_client import call_amazon

    with LOCK:
        corpus = read_corpus(settings.knowledge_path)
        now = datetime.now(timezone.utc)
        try:
            last = datetime.fromisoformat(corpus["refreshed_at"])
            fresh = (now - last).total_seconds() < settings.knowledge_refresh_hours * 3600
        except (ValueError, TypeError):
            fresh = False
        if fresh and not force:
            return corpus
        if not settings.amazon_mcp_server_url:
            return corpus
        try:
            data = asyncio.run(
                call_amazon(settings.amazon_mcp_server_url, "amazon_document_collection", {})
            )
            if data.get("company") != "amazon":
                return corpus
            sources = valid_sources(data.get("sources", []))
            # Atomic complete refresh: do not replace good knowledge with a partial outage.
            if len(sources) != len(SOURCES):
                return corpus
            corpus = {"version": 1, "refreshed_at": now.isoformat(), "sources": sources}
            path = settings.knowledge_path
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(path)
            return corpus
        except Exception:
            return corpus


def retrieve(corpus, query, limit=5):
    """Rank overlapping passages using query term frequency and inverse document frequency."""
    if re.search(r"\blp\b", query, re.I):
        query += " leadership principles"
    if "sde2" in query.lower() or "sde ii" in query.lower():
        query += " system design scalability reliability"
    chunks = []
    for source in valid_sources(corpus.get("sources", [])):
        words = source["text"].split()
        for start in range(0, len(words), 150):
            passage = " ".join(words[start : start + 200])
            chunks.append(
                {
                    **source,
                    "text": passage,
                    "counts": Counter(tokens(source["title"] + " " + passage)),
                }
            )
    terms = set(tokens(query))
    ranked = []
    for chunk in chunks:
        score = sum(
            (1 + math.log(chunk["counts"][term]))
            * math.log(1 + len(chunks) / (1 + sum(term in c["counts"] for c in chunks)))
            for term in terms
            if chunk["counts"][term]
        )
        if score > 0:
            ranked.append((score, chunk))
    return [chunk for _, chunk in sorted(ranked, key=lambda item: item[0], reverse=True)[:limit]]


def rag_context(settings, query):
    corpus = refresh(settings)
    chunks = retrieve(corpus, query)
    context = "\n\n".join(
        f"Source: {c['url']} | fetched: {c['retrieved_at']} | snapshot: {c['sha256'][:12]}\n{c['text']}"
        for c in chunks
    )
    if context:
        context = (
            "Use dated snapshots below only where they support the answer. They may be stale if refresh failed; never call them live or infer missing facts.\n"
            + context
        )
    return context, tuple(dict.fromkeys(c["url"] for c in chunks))


def knowledge_status(settings):
    corpus = read_corpus(settings.knowledge_path)
    sources = valid_sources(corpus.get("sources", []))
    return {
        "mode": "local lexical RAG",
        "source_count": len(sources),
        "expected_sources": len(SOURCES),
        "last_successful_refresh": corpus.get("refreshed_at"),
        "refresh_hours": settings.knowledge_refresh_hours,
        "sources": [
            {"title": s["title"], "url": s["url"], "retrieved_at": s["retrieved_at"]}
            for s in sources
        ],
        "model_training": False,
    }
