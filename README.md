# AI Coach

An AI-powered career coaching platform that helps professionals discover how AI can transform their daily work. Not a static course — a conversational coach that profiles you, reveals blind spots, and prescribes a personalized learning path.

Built for product managers and product leaders first, expanding from there.

---

## What It Does

**HOOK** — You share your resume and role. The coach mirrors back what it sees about your current work and AI usage, then asks where you want to go.

**REVEAL** — The coach surfaces 3 specific AI blind spots in your actual work — not generic advice, but friction points in your specific role at your company with your tools.

**PRESCRIBE** — You pick a blind spot. The coach builds you a personalized learning path: real resources (articles, videos, GitHub repos) sequenced in dependency order, with narration explaining why each step matters for your goal.

---

## Quick Start

### Prerequisites
- Python 3.11
- OpenAI API key (required)
- Perplexity API key (recommended — needed for content retrieval)
- YouTube API key (optional — falls back gracefully)
- GitHub token (optional — falls back gracefully)

### Setup

```bash
# Clone and enter the project
git clone <repo-url>
cd AI-Coach-1

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

Create a `.env` file at the project root:

```
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
YOUTUBE_API_KEY=...        # optional
GITHUB_TOKEN=ghp_...       # optional
```

### Run

```bash
streamlit run ui.py --server.port 3000
```

Open `http://localhost:3000` in your browser.

---

## Architecture

### Coaching Pipeline

```
User input (resume + name)
        ↓
   [parse_resume]          Extract structured profile from PDF/text
        ↓
   [analyze_role]          Infer role archetype, domain, org shape, AI constraints
        ↓
   [infer_role_detail]     Get task clusters + effort breakdown
        ↓ (checks archetype store first — skips LLM if known role)
   [infer_cultural_tone]   Calibrate coach voice to user's communication style
        ↓
   Coach mirrors observation → asks aspiration question
        ↓
   [interpret_aspiration]  Structure career goal into target role + transition type
        ↓
   [generate_use_cases]    Identify 3 AI blind spots specific to this role
        ↓ (injects archetype priors if known — LLM confirms/refines)
   User picks a use case
        ↓
   [prescribe_learning_path]
        ├─ Query planner generates role-specific search queries
        ├─ Parallel retrieval: Perplexity + YouTube + GitHub
        ├─ Reflection agent filters (seniority-aware: rejects intro content for VP+)
        ├─ Content store warm start: proven resources for this role level
        ├─ Scoring + explanation
        └─ learning_steps_agent: dependency-aware sequencing + per-resource narration
        ↓
   GPT-4o synthesizes into coaching narrative
        ↓
   Formatted learning path delivered to user
```

### Intelligence Store (Role Archetype Moat)

The platform gets smarter with each session without proportional LLM cost growth.

**Role archetypes** (`coach/intelligence/archetypes/seed.json`):
- 12 seeded archetypes covering PM and product leadership roles
- Matching: seniority (50%) + domain (35%) + org shape (15%), threshold 0.6
- Hit → skip GPT-4o role detail call, inject blind spot priors into use case generation
- Flywheel: tracks session count + use case choices per archetype

**Content intelligence** (`coach/intelligence/content/content_index.json`):
- Indexes proven resources by use case category × seniority tier
- Builds up from every PRESCRIBE session automatically
- Warm-start candidates run through reflection — same seniority filter as fresh content
- Gate: item must have 3+ sessions or 1 thumbs-up before it's surfaced as warm start

### Key Design Decisions

- **Coordinator** uses OpenAI function calling — not a hardcoded pipeline
- **Content is always fresh** — Perplexity/YouTube/GitHub searched live every session; intelligence store supplements, never replaces
- **Reflection is the personalization filter** — seniority-aware (rejects "Getting Started" content for VP+), tool-aware, skill-aware; runs on both fresh and warm-start items
- **Async agents** wrapped with `asyncio.run()` + RuntimeError fallback for Streamlit compatibility
- **User profiles** stored as JSON in `user_data/` (not committed — personal data)

---

## Project Structure

```
AI-Coach-1/
├── coach/                          # v3 coaching engine
│   ├── coordinator.py              # LLM brain with 8 tool functions
│   ├── tools/                      # Tool wrappers called by coordinator
│   │   ├── analyze_role.py
│   │   ├── infer_role_detail.py
│   │   ├── generate_use_cases.py
│   │   ├── prescribe_learning_path.py
│   │   └── ...
│   └── intelligence/               # Intelligence moat
│       ├── archetype_store.py      # Role archetype matching
│       ├── content_store.py        # Content intelligence store
│       ├── flywheel_writer.py      # Session outcome tracking
│       ├── archetypes/seed.json    # 12 seeded role archetypes
│       └── content/                # Populated at runtime
│
├── agents/                         # Agent implementations
│   ├── gap_analysis_agent/         # Blind spot identification
│   └── recommendation_agent/       # Content retrieval + learning path
│       ├── content_recommendation/ # Query → Retrieve → Reflect → Score
│       └── learning_path/          # Sequencing + narration agents
│
├── agent_core/                     # Shared infrastructure
│   ├── global_agent_memory.py      # Session memory (sync)
│   ├── persona_context.py          # Durable user context store
│   ├── content_cache.py            # Content cache with feedback tracking
│   └── session_trace.py            # Event logging
│
├── tools/                          # v2 assessment tools
│   ├── role_context_agent/
│   ├── tool_familiarity_agent/
│   └── cultural_alignment_agent/
│
├── ui.py                           # Streamlit chat UI (entry point)
├── specs/                          # Architecture docs
│   ├── v3_architecture.md          # North star spec
│   └── product_spec.md             # Full product spec
└── requirements.txt
```

---

## Status

### Complete
- **Phase A** — Coach coordinator, chat UI, user model, core assessment tools
- **Phase B** — Full HOOK → REVEAL → PRESCRIBE pipeline, content recommendation, aspiration-aware coaching, target-role bridge framing
- **Track 1 Token Optimization** — Batch reflection (12 LLM calls → 1), batched narration; ~40-50% cost reduction per PRESCRIBE
- **Phase C** — Role archetype intelligence store (12 seed archetypes, weighted matching, LLM skip for known roles, blind spot priors)
- **Phase C+** — Content intelligence store (cross-role content memory, warm-start with reflection gate)

### Planned
- **Feedback wiring** — Connect thumbs up/down UI to content store `record_feedback()`
- **Progress tracking** — Resume sessions, track modules completed
- **Phase C++** — Vector embeddings for semantic role matching (ChromaDB)
- **Supabase migration** — Replace JSON file storage

---

## Development Notes

- Run with `python3` (not `python`)
- Virtual environment at `venv/`
- API keys in `.env` at project root (not committed)
- User profiles in `user_data/` (not committed — personal data)
- Runtime logs in `logs/` (not committed)
- CLAUDE.md contains AI assistant context for Claude Code
