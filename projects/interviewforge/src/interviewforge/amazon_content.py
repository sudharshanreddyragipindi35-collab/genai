"""Reviewed source registry and original teaching exercises for Amazon preparation."""

SOURCES = {
    "lp": (
        "Amazon Leadership Principles",
        "https://www.amazon.jobs/content/en/our-workplace/leadership-principles",
    ),
    "coding": (
        "Amazon software development topics",
        "https://www.amazon.jobs/content/en/how-we-hire/interview-prep/software-development-topics",
    ),
    "sde1": (
        "Amazon university SDE assessment preparation",
        "https://www.amazon.jobs/content/en/how-we-hire/university/sde-oa",
    ),
    "sde2": (
        "Amazon SDE II preparation",
        "https://www.amazon.jobs/content/en/how-we-hire/sde-ii-interview-prep",
    ),
    "loop": (
        "Amazon interview loop",
        "https://www.amazon.jobs/content/en/how-we-hire/interview-loop",
    ),
}
# Explicitly linked problems from first-person reports, reviewed during implementation.
REPORTS = {
    "SDE I": [
        {
            "title": "Intersection of Two Arrays II",
            "slug": "intersection-of-two-arrays-ii",
            "difficulty": "Easy",
            "report_url": "https://leetcode.com/discuss/post/1719034/amazon-sde1-dublin-ireland-january-2022-offer/",
            "reported_date": "2022-01",
            "match_type": "explicit problem link",
        },
        {
            "title": "LRU Cache",
            "slug": "lru-cache",
            "difficulty": "Medium",
            "report_url": "https://leetcode.com/discuss/post/1719034/amazon-sde1-dublin-ireland-january-2022-offer/",
            "reported_date": "2022-01",
            "match_type": "similar cache variant, linked by author",
        },
    ],
    "SDE II": [
        {
            "title": "LRU Cache",
            "slug": "lru-cache",
            "difficulty": "Medium",
            "report_url": "https://leetcode.com/discuss/post/5862916/",
            "reported_date": "unknown",
            "match_type": "named problem in first-person report",
        },
    ],
}
LESSONS = {
    "coding": (
        "Coding foundations and problem solving",
        "coding",
        "Clarify input size, duplicates, ordering, and failure cases before choosing a structure. Compare a direct solution with a hash map or sorted approach. State time and space costs, write readable Python, then dry-run empty inputs and repeated values.",
        "Explain how a Counter preserves duplicate counts when intersecting two arrays. Show a small dry run before writing code.",
    ),
    "lp": (
        "Leadership Principles and STAR evidence",
        "lp",
        "Read all principles in the official source. Build a story bank around customer impact, ownership, investigation, quality, disagreement, and delivery. For each story separate the situation, your responsibility, your own actions, measurable result, and what you learned. Never invent achievements or metrics.",
        "Draft a story about a customer problem you owned. Explain which evidence changed your decision, the trade-off you made, and how you measured the outcome.",
    ),
    "lld": (
        "Low-level design and maintainable Python",
        "coding",
        "Turn requirements into interfaces and invariants. Separate storage, eviction policy, and client behavior. Explain composition, dependency injection, testing seams, and error handling. Start with one working design before adding abstractions.",
        "Design a cache API with get and put. State capacity and update invariants; explain how a dictionary and linked list cooperate.",
    ),
    "design": (
        "System design: requirements to trade-offs",
        "sde2",
        "Clarify functional requirements and traffic assumptions. Estimate load, define APIs and storage, then trace a request. Discuss consistency, caching, retries, failure recovery, observability, and cost. Explain alternatives and why your design meets the stated constraints.",
        "Design a metrics collection service: explain ingestion, aggregation, retention, percentile calculation, overload behavior, and late events. This is an original rehearsal informed by reported interview themes.",
    ),
    "genai": (
        "GenAI engineering extension",
        "coding",
        "This is optional job-specific enrichment, not a universal Amazon SDE interview requirement. Learn retrieval, embeddings, prompt design, grounded answers, evaluation sets, latency, cost, and prompt-injection boundaries. Choose retrieval before fine-tuning when the problem is changing factual knowledge.",
        "Design a Python support assistant. Specify the retrieval corpus, source citations, offline evaluation, unsafe-input handling, and a fallback when evidence is missing.",
    ),
    "mock": (
        "Interview rehearsal and reflection",
        "loop",
        "Rehearse without relying on an IDE. Explain assumptions and alternatives aloud, test your solution, then answer a behavioral follow-up using an authentic example. Afterward record one weakness and a concrete revision task.",
        "Run a coding explanation followed by a STAR story. Ask the coach to critique clarity and evidence; this is practice feedback, not an Amazon hiring score.",
    ),
}
