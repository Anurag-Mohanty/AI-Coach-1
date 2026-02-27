# AI Coach — Project Context for Claude

## What This Project Is

An AI-powered career coaching platform that helps professionals (starting with product managers) discover how AI can transform their daily work. It's NOT a static course — it's a conversational coach that profiles you, reveals blind spots, and prescribes personalized learning paths.

**Owner**: Non-developer founder building with AI assistance. Keep code clean, explain trade-offs, don't assume dev knowledge.

## Current State (as of Feb 2025)

### What Exists (v1/v2 — built on Replit)
- **232 files** across agents, tools, UI pages, specs, and sandbox tests
- **Assessment Agents** (most complete): Resume, LinkedIn, Role Context, Role Detail, Tool Familiarity, Cultural Alignment, Aspiration — all v2, schema-validated
- **Gap Analysis Agents** (mostly stubs): Role Ladder (partial v2), Skill Delta, Use Case Miss, Domain Jump, Meta Agent — mostly hardcoded logic
- **Recommendation Agents** (mixed): Content Recommendation Pipeline (most sophisticated — query planner + 4 source retrievers + reflection + scoring), Learning Path Pipeline (v2, 5 sub-agents), Use Case Generator, Tool Recommender
- **Infrastructure** (`agent_core/`): LLM client (OpenAI GPT-4), prompt builder, templates, logging, feedback, caching, compliance
- **UI**: Streamlit — currently a linear pipeline (`ui.py` runs agents top-to-bottom), NOT conversational

### The Fundamental Problem
The current system is a **workflow tool**, not a **coach**. It dumps assessment results all at once. There is no conversation, no iterative refinement, no coaching dialogue. The v3 architecture (see `specs/v3_architecture.md`) redesigns this completely.

### What Needs to Be Built (v3)
The v3 vision transforms this from a pipeline into a **guided coaching conversation**:

1. **Coach Coordinator** — An LLM-based brain that decides what to do next (not a hardcoded pipeline)
2. **Chat UI** — Replace page-based Streamlit with `st.chat_message` conversational interface
3. **User Model** — Persistent memory per user (profile, coaching state, knowledge state, preferences, history)
4. **Tools as Functions** — Refactor existing agents into pure function tools the coordinator can call
5. **Coaching Phases**: Hook → Reveal → Personalize → Prescribe → Grow (see `specs/v3_architecture.md`)
6. **Flywheel** — Every user interaction enriches the platform for future users in similar roles

### Build Order (from v3 spec)
**Phase A (Foundation)**: User Model Store → Coach Coordinator → Chat UI → parse_resume tool → analyze_role tool → generate_use_cases tool
**Phase B (Personalization)**: assess_skill_gaps → find_ai_tools → search_content → Journey Templates → Session Resume
**Phase C (Growth & Moat)**: check_knowledge → Progress Tracking → Feedback Collection → Flywheel Writes

## Key Specs & Docs
- `specs/v3_architecture.md` — The north star. Read this first.
- `specs/product_spec.md` — Full product spec with agent inventory
- `specs/review_and_implementation_plan.md` — Honest assessment of what exists and what needs work
- `specs/system_architecture.md` — System architecture details

## Tech Stack
- **Language**: Python 3.11
- **UI**: Streamlit (chat-based for v3)
- **LLM**: OpenAI GPT-4 (via `agent_core/llm_client.py`)
- **Content Retrieval**: Perplexity API, YouTube Transcript API, GitHub API, Google API
- **Storage**: JSON files initially → Supabase later
- **Run command**: `streamlit run ui.py --server.port 3000`

## Environment Variables Needed
- `OPENAI_API_KEY` — Required for all LLM calls
- `PERPLEXITY_API_KEY` — For content search (optional, can mock)
- `YOUTUBE_API_KEY` / `GOOGLE_API_KEY` — For content retrieval (optional, can mock)
- `GITHUB_TOKEN` — For GitHub content retrieval (optional, can mock)

## Project Structure
```
AI-Coach-1/
├── agent_core/          # Shared utilities (LLM client, prompt builder, logging, etc.)
├── agents/              # Agent implementations
│   ├── gap_analysis_agent/    # Gap analysis (mostly stubs)
│   ├── recommendation_agent/  # Recommendations + content pipeline
│   └── skill_assessment_agent/ # Skill assessment orchestrator
├── tools/               # v2 assessment tools (resume, linkedin, role_context, etc.)
├── pages/               # Streamlit page views
├── sandbox/             # Test scripts
├── schemas/             # JSON schemas for agent I/O contracts
├── specs/               # Architecture docs and specs
├── ui.py                # Current entry point (v1 linear pipeline)
└── requirements.txt     # Python dependencies
```

## Development Notes
- When running locally: `pip install -r requirements.txt && streamlit run ui.py`
- The `PYTHONPATH` should include the project root for imports to work
- Many agents in `agents/` reference import paths from the Replit environment — may need path fixes for local dev
- The `.replit` file contains workflow configs from the Replit environment (not needed locally)
