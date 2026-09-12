# Implemented technologies and GenAI skills

This inventory describes the current local application, rather than every capability provided by its dependencies.

| Skill / technology | Implementation evidence | Current scope |
| --- | --- | --- |
| LangChain / Claude | [coach.py](../src/interviewforge/ai/coach.py) | LangChain Anthropic adapter invokes Claude with retrieved evidence and candidate context |
| Deep Agents / LangGraph | [deep_agent.py](../src/interviewforge/ai/deep_agent.py) | Supervisor and four specialist definitions; delegation is model-selected, not guaranteed on every request |
| Prompt engineering | [prompts.py](../src/interviewforge/ai/prompts.py) | Versioned supervisor and specialist instructions for evidence, scope and readable answers |
| RAG / information retrieval | [rag.py](../src/interviewforge/ai/rag.py) | Local document chunks and lexical ranking; no embedding model or vector database yet |
| MCP server development | [amazon_server.py](../src/interviewforge/ai/amazon_server.py) | Retrieves allowlisted public Amazon documents through an owned Python MCP bridge |
| MCP client integration | [amazon_client.py](../src/interviewforge/ai/amazon_client.py), [leetcode_mcp.py](../src/interviewforge/ai/leetcode_mcp.py) | Application-managed retrieval before generation and exact problem lookup |
| Domain scope controls | [amazon_scope.py](../src/interviewforge/ai/amazon_scope.py) | Deterministic named-company guard plus Amazon-specific prompts |
| Personalization / progress | [roadmap.py](../src/interviewforge/roadmap.py) | Role, experience and time-based plans with local saved progress |
| Python web application | [app.py](../src/interviewforge/app.py) | FastAPI, Jinja2, Pydantic settings and Markdown rendering |

## How a coaching request runs

1. Apply the Amazon scope guard.
2. Retrieve relevant passages from the local Amazon corpus, refreshing via MCP when due.
3. Combine evidence with the question and applicable candidate context.
4. Invoke the Deep Agents supervisor using LangChain's Claude adapter.
5. Allow the supervisor to delegate to configured specialists when useful.
6. Render the answer; save generated deep lessons when requested.

MCP retrieval is currently orchestrated by application code. It is not exposed as dynamically selected tools to the supervisor. The candidate roadmap and unlock decisions are also controlled by application logic.

Deep Agents uses LangChain building blocks and the LangGraph runtime, as described in the [official Deep Agents documentation](https://docs.langchain.com/oss/python/deepagents/overview). The app uses this runtime through `create_deep_agent`; it does not yet define a separate custom `StateGraph`.

## Further work

Custom checkpointed LangGraph workflows, durable conversation memory, vector/hybrid retrieval, reranking, production tracing, scored evaluations and learned mastery models remain future work. Installing a library does not enable these features automatically.

Knowledge refresh updates the retrieval corpus. It does not fine-tune Claude or train a model on conversations. SQLAlchemy/PostgreSQL configuration is present, but candidate progress currently uses local JSON storage. The optional OpenAI adapter is declared as a dependency; the live coaching path uses Anthropic.
