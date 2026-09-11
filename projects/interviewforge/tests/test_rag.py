from datetime import datetime, timezone

from interviewforge.ai.rag import read_corpus, refresh, retrieve
from interviewforge.amazon_content import SOURCES
from interviewforge.config import Settings


def corpus():
    return {
        "company": "amazon",
        "sources": [
            {
                "url": url,
                "title": title,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "text": (
                    (
                        "Leadership principles ownership customer obsession trust "
                        if key == "lp"
                        else "coding algorithms scalability design "
                    )
                    * 30
                ),
            }
            for key, (title, url) in SOURCES.items()
        ],
    }


def test_retrieval_ranks_lp_evidence():
    result = retrieve(corpus(), "Explain LP ownership and customer obsession")
    assert result
    assert result[0]["url"] == SOURCES["lp"][1]
    assert retrieve(corpus(), "xylophone") == []


def test_refresh_is_persistent_and_reuses_fresh_index(tmp_path, monkeypatch):
    calls = []

    async def fake(*args):
        calls.append(args)
        return corpus()

    monkeypatch.setattr("interviewforge.ai.amazon_client.call_amazon", fake)
    settings = Settings(
        _env_file=None, knowledge_path=tmp_path / "rag.json", amazon_mcp_server_url="http://local"
    )
    first = refresh(settings)
    assert len(first["sources"]) == 5
    assert read_corpus(settings.knowledge_path)["sources"] == first["sources"]
    refresh(settings)
    assert len(calls) == 1

    async def broken(*args):
        return {"company": "amazon", "sources": []}

    monkeypatch.setattr("interviewforge.ai.amazon_client.call_amazon", broken)
    assert refresh(settings, force=True) == first
