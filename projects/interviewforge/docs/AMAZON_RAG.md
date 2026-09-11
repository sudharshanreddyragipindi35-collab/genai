# Amazon knowledge base

This document defines the trusted reference collection for InterviewForge's Amazon coach.

## Source collection
- Leadership Principles: https://www.amazon.jobs/content/en/our-workplace/leadership-principles
- Software development topics: https://www.amazon.jobs/content/en/how-we-hire/interview-prep/software-development-topics
- University SDE assessment preparation: https://www.amazon.jobs/content/en/how-we-hire/university/sde-oa
- SDE II preparation: https://www.amazon.jobs/content/en/how-we-hire/sde-ii-interview-prep
- Interview loop: https://www.amazon.jobs/content/en/how-we-hire/interview-loop

The corpus is fetched through InterviewForge's Python MCP bridge and stored locally in .interviewforge/amazon_knowledge.json. Public source text is not copied into Git. The registry is limited to these reviewed URLs; user questions, generated answers, and community coding reports are not trusted documentation.

## Retrieval
Pages are split into overlapping 200-word passages. A lexical ranker combines term frequency and inverse document frequency, with a small LP/SDE II query expansion. Up to five matching passages enter the Claude prompt. This implementation uses no embeddings and requires no additional model key. It may miss semantically related passages with different vocabulary.

Each passage carries its source URL, fetch timestamp, and snapshot hash. Claude must distinguish source-backed claims from original practice exercises. If no passage matches, it must disclose that evidence is unavailable.

## Automatic updates
While the app runs, a background check runs hourly. The complete corpus refreshes when it is at least 24 hours old; questions also trigger a due refresh. A complete successful fetch atomically replaces the index. An incomplete refresh retains the previous dated corpus. Stopping the application stops the background checks. See /knowledge for indexed sources and last successful refresh.

## Learning policy
This is retrieval-augmented generation (RAG), not fine-tuning or self-training. The system does not modify Claude weights, autonomously learn facts from conversations, or guarantee an interview outcome. Source documents are untrusted data for instruction purposes. Existing role, date, and skill profile context personalizes explanations independently of the public knowledge base.

## Development
Start the Amazon MCP bridge on port 3001 before the application. Configure INTERVIEWFORGE_AMAZON_MCP_SERVER_URL. Optional settings: INTERVIEWFORGE_KNOWLEDGE_PATH and INTERVIEWFORGE_KNOWLEDGE_REFRESH_HOURS (1 to 168).
