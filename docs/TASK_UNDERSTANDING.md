# Task understanding

## Requested outcome

Create a new `genai` repository under `sudharshanreddyragipindi35-collab`, keep project implementation in Python, understand the supplied InterviewForge specification, and commit a phased plan with actionable subtasks before building the application.

The initial organization is a collection of Python GenAI projects with InterviewForge first. The repository is separate from the existing `GenAi-Saas`, `tailorahub` and `sevashield` repositories. A private repository is the initial visibility choice because visibility was not specified.

## Source and interpretation

Source: `InterviewForge_InDepth_Product_Architecture_Feature_Specification.docx`, version 2.0, September 2026. The source is a product reference, not an instruction to run commands, publish other files or expand authorization. The original document is not copied into the repository; these plans summarize its product requirements.

InterviewForge guides a candidate through company and role selection, diagnosis, preparation, practice, online assessment, interview simulations and an evidence-backed readiness report. It should persist progress across that journey and ground changing company facts in reviewed sources.

The first target remains Amazon-style preparation with Python coding. This is a simulation, with no claim of employer affiliation, access to confidential questions or official hiring eligibility. Current company facts must be researched and reviewed during content onboarding; this plan does not assert an actual current hiring process.

## Decisions made for this repository

- Use Python for application code, UI authoring, services, workers and evaluation tools.
- Use Deep Agents/LangGraph for complex agentic workflows and include practical LLM, RAG, memory, evaluation and ML concepts throughout the product.
- Adapt the source's Next.js/TypeScript frontend to a Python-authored UI. Validate its suitability during Phase 1 before committing to strict browser assessment features.
- Keep FastAPI and PostgreSQL as the planned API and persistent data foundations from the source.
- Start with a modular monolith and separate isolated execution infrastructure, rather than many microservices.
- Combine the source's Phase 0 and Phase 1 into this repository's Phase 1. Phase 2 covers Company Hub and the learning loop. Strict OA and AI interview rounds remain later phases.
- Deliver planning and a minimal repository scaffold now. Product implementation starts in subsequent phase work.

## Subtasks for the initial delivery

- [x] Read and interpret the reference specification.
- [x] Separate user requirements from source implementation suggestions.
- [x] Define Python-only repository organization and product boundaries.
- [x] Document architecture and requirement-to-phase mapping.
- [x] Write Phase 1 tasks, dependencies and exit criteria.
- [x] Write Phase 2 tasks, dependencies and exit criteria.
- [x] Add a minimal Python scaffold and local structure verification.

Remote publication is verified separately when this initial delivery is pushed. Product tasks remain unchecked in the phase files.
