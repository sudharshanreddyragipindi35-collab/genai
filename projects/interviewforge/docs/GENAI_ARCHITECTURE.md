# GenAI and machine learning architecture

## Architecture decision

InterviewForge will use the Python Deep Agents SDK on the LangGraph runtime for complex, multi-step coaching and interview workflows. Deep Agents provides planning, specialist delegation, context management, durable execution, streaming and human review patterns. Simple generation stays behind a smaller model gateway so every request does not pay agent overhead.

The initial supervisor coordinates a knowledge verifier, learning strategist, code reviewer and evaluation critic. A dedicated interview conductor is added in Phase 4. Each specialist receives the smallest context and tool set needed for its task. Agent tools return typed, bounded results and enforce candidate ownership before data reaches a model.

These concepts are internal implementation details. The candidate product exposes an Amazon coach and evidence-backed preparation features, not an architecture showcase.

## Generation path

1. Classify mode and enforce authorization and assessment restrictions.
2. Load a compact candidate-state snapshot with explicit provenance.
3. Retrieve approved knowledge using metadata constraints, lexical search and vector similarity.
4. Rerank candidates and reject stale, conflicting or unsupported evidence.
5. Run a direct structured model call or durable agent graph according to task complexity.
6. Validate output schema, citations, policy constraints and disclosure level.
7. Persist a trace containing graph, prompt, model and evidence versions, latency, usage and verifier outcome.
8. Update learning state only through deterministic evidence services.

## GenAI concepts

- Tool calling and structured outputs for typed hints, probes, feedback and citations.
- Hybrid RAG with PostgreSQL full-text search, pgvector embeddings, metadata filters and reranking.
- Context engineering with candidate snapshots, progressive source loading, conversation summaries and token budgets.
- Short-term thread state plus durable memory for explicit preferences and verified candidate facts.
- Multi-agent delegation with human review for company-content publication and other high-impact updates.
- Model routing between extraction/classification, tutoring/reasoning and embedding/reranking models.
- Semantic caching only where user state, content versions and privacy boundaries make reuse safe.
- Prompt/model versioning, trace correlation, cost/latency budgets and provider fallback behavior.
- Controls for prompt injection, retrieval poisoning, hidden-test leakage and tool misuse.

## Machine learning concepts

Begin personalization with transparent evidence-weighted mastery and spaced repetition. Record correctness, difficulty, response time, hint use, recency and repeated exposure. Once enough lawful, representative data exists, compare calibrated models such as Bayesian knowledge tracing, item-response models and supervised ranking for next-task recommendation.

Offline validation uses candidate-level and time-aware splits so attempts from the same person or future behavior do not leak across training and validation. Evaluate calibration, ranking quality, subgroup performance and drift. A learned model ships only when it improves over the interpretable baseline and retains an explanation path. Readiness is never a raw LLM probability.

## Evaluation program

Maintain versioned golden datasets for grounded company answers, hint quality, code feedback, interview probing, rubric consistency and refusal behavior. Measure retrieval recall, citation support, faithfulness, task completion, hint leakage, structured-output validity, latency and cost. Critical access and leakage cases are hard release gates. Subjective quality combines rubric-based model evaluation with periodic human review.

Production traces redact unnecessary candidate data. Evaluation datasets require consent and de-identification. Prompt and model changes run against the baseline before release, with provider and content versions recorded.

## Boundaries

Agents never execute candidate code in the API process, read hidden tests, modify scores, unlock interview stages, publish company content or bypass authorization. Deep Agents filesystem and execution tools are not exposed to candidate-facing agents without an isolated backend and explicit permission policy. Retrieved instructions remain untrusted data.

The Amazon boundary is enforced three times: a deterministic input guard rejects named non-Amazon requests before generation; the MCP adapter hard-codes `company=amazon`; and returned structured MCP data is rejected unless its company is Amazon. The supervisor prompt repeats the restriction as defense in depth.

The integration is optional during the local UI preview. Install it with `uv sync --extra agents --locked` when beginning real model integration. Building the factory does not call a model; invocation requires a configured provider key and tool-calling model.
