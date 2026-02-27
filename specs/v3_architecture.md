# AI Coach v3 — Architecture & Philosophy

## Core Thesis

Users don't know what they don't know about AI. They won't self-direct through an assessment. The system must **draw them into a guided coaching journey** that feels like talking to a smart friend, not filling out a form.

Every interaction builds the moat: role knowledge gets richer, journey templates get validated, content gets curated, and the next user in a similar role gets a better, cheaper experience.

## Design Principles

### 1. Guided Discovery, Not Self-Service
- The user's job is to **react and correct**, never to navigate or decide
- The coach decides what to explore next, what to reveal, what to recommend
- Minimum viable input: a resume OR a one-sentence role description
- Everything else is inferred, presented, and refined through conversation

### 2. Start-Stop-Resume Journey
- A user can close their browser mid-conversation and come back days later
- The coach remembers everything: what was discussed, what was recommended, what was tried
- Each return starts with: "Welcome back. Last time we talked about X. Since then..."
- Progress is visible: the user can see where they are in their coaching journey

### 3. Growth Through Micro-Tests
- The coach periodically checks understanding with lightweight knowledge checks
- Not formal quizzes — conversational: "Before we move on, quick question..."
- Results feed back into the user model: did they retain? did they apply?
- Growth is tracked and shown: "You've gone from 2/10 to 6/10 on prompt engineering"

### 4. Every User Enriches the Platform (The Flywheel)
- When a user in role X validates a recommendation, that signal strengthens it for the next user in role X
- Journey paths that work get promoted; paths that don't get deprioritized
- Content that gets positive feedback rises; content that gets skipped drops
- Role-AI mappings get refined with every new user profile
- The system gets cheaper to run because it caches and reuses validated knowledge

---

## Agentic Architecture

### The Coach Coordinator (The Brain)

The coordinator is an LLM with a system prompt that encodes the coaching methodology. It is NOT a state machine or pipeline. It reasons about what to do next.

```
┌──────────────────────────────────────────────────┐
│              COACH COORDINATOR                    │
│                                                   │
│  System prompt encodes:                           │
│  - Coaching methodology (phases, transitions)     │
│  - Personality (warm, direct, encouraging)        │
│  - Decision logic (what to explore next)          │
│                                                   │
│  Has access to:                                   │
│  - user_model (everything known about this user)  │
│  - session_state (current phase, last action)     │
│  - tools (pure functions it can call)             │
│  - knowledge (RAG over role/tool/content DB)      │
│                                                   │
│  On each turn:                                    │
│  1. Reads user message + user_model + phase       │
│  2. Decides: respond directly, call a tool,       │
│     or transition to a new phase                  │
│  3. Generates response in coaching voice          │
│  4. Updates user_model with new information       │
└──────────────────────┬───────────────────────────┘
                       │
          ┌────────────┼────────────────┐
          ▼            ▼                ▼
    ┌──────────┐ ┌──────────┐   ┌──────────────┐
    │  TOOLS   │ │   RAG    │   │  USER MODEL  │
    │ (extract,│ │(knowledge│   │  (persistent │
    │  analyze,│ │  search) │   │   memory)    │
    │  score)  │ │          │   │              │
    └──────────┘ └──────────┘   └──────────────┘
```

### Tools (Pure Functions, No State)

Tools are called by the coordinator when it needs structured data. They take input, return output, no side effects.

| Tool | Input | Output | When Used |
|---|---|---|---|
| `parse_resume` | file (PDF/DOCX/TXT) | structured profile (skills, roles, tools, experience) | Phase 1: user uploads resume |
| `parse_linkedin` | profile text/URL | AI signals, interests, activity | Phase 1: user provides LinkedIn |
| `analyze_role` | title, company, domain | role context, archetype, org shape, AI applicability | Phase 1: after profile extraction |
| `analyze_role_detail` | role context | task clusters, effort distribution, AI opportunity density | Phase 2: when coach reveals blind spots |
| `assess_skill_gaps` | current capabilities, target role | missing skills, priority, gap severity | Phase 2-3: personalized gap analysis |
| `find_ai_tools` | role, gaps, task clusters | tool recommendations with rationale | Phase 3-4: specific recommendations |
| `search_content` | topic, user level, preferences | curated articles, videos, courses | Phase 4: learning path |
| `generate_use_cases` | role context, gaps | 3-5 specific AI use cases for their role | Phase 2: reveal moments |
| `check_knowledge` | topic, expected level, user history | micro-assessment question + scoring | Phase 4-5: growth checks |
| `infer_cultural_tone` | profile signals | communication style preferences | Phase 1: calibrate coach voice |

### RAG / Knowledge Layer (The Moat)

Three knowledge stores, all queryable via embedding search:

**Store 1: Role-AI Intelligence** (core IP)
```json
{
  "role_archetype": "product_manager_b2b_saas",
  "seniority": "mid",
  "common_tasks": ["competitive analysis", "PRD writing", "stakeholder alignment"],
  "ai_opportunities": [
    {
      "task": "competitive analysis",
      "current_effort_pct": 25,
      "ai_reduction_pct": 70,
      "recommended_tools": ["perplexity", "chatgpt"],
      "validated_by_n_users": 47,
      "avg_satisfaction": 4.2
    }
  ],
  "typical_gaps": ["prompt engineering", "workflow automation", "data analysis with AI"],
  "proven_journey_template_id": "pm_b2b_mid_v3"
}
```
- Seeded initially from expert knowledge + LLM generation
- Enriched every time a user in this archetype validates/rejects a recommendation
- Becomes the lookup table that makes coaching instant for common roles

**Store 2: Tool & Content Library**
```json
{
  "tool": "cursor",
  "category": "AI code editor",
  "good_for_roles": ["pm_technical", "founder", "data_analyst"],
  "learning_curve": "medium",
  "free_tier": true,
  "content": [
    {"type": "video", "url": "...", "quality_score": 0.89, "votes": 23},
    {"type": "article", "url": "...", "quality_score": 0.72, "votes": 8}
  ]
}
```
- Curated tool database with role-relevance mappings
- Content attached to tools/skills, scored by user feedback
- Stale content auto-deprioritized by age + negative signals

**Store 3: Journey Templates**
```json
{
  "template_id": "pm_b2b_mid_v3",
  "for_archetype": "product_manager_b2b_saas",
  "phases": [
    {"name": "quick_win", "focus": "chatgpt_for_prd", "typical_duration_days": 3},
    {"name": "skill_build", "focus": "prompt_engineering_basics", "typical_duration_days": 7},
    {"name": "tool_adopt", "focus": "cursor_or_copilot", "typical_duration_days": 14},
    {"name": "workflow", "focus": "ai_integrated_sprint_planning", "typical_duration_days": 21}
  ],
  "completion_rate": 0.34,
  "avg_satisfaction": 4.1,
  "n_users_completed": 12
}
```
- Pre-built paths for common role archetypes
- Validated by usage data: which paths actually get completed?
- New users in a known archetype get a warm-start journey, not a cold assessment

### User Model (Persistent Memory)

One document per user, updated after every interaction:

```json
{
  "user_id": "u_abc123",
  "created_at": "2025-04-01",
  "last_active": "2025-04-15",

  "profile": {
    "name": "Sarah",
    "role": "Senior Product Manager",
    "company_type": "B2B SaaS, Series C",
    "domain": "fintech",
    "seniority": "IC4",
    "years_experience": 8,
    "skills": ["stakeholder management", "PRDs", "analytics"],
    "tools_known": ["jira", "figma", "amplitude"],
    "ai_tools_known": ["chatgpt_basic"],
    "source": "resume"
  },

  "coaching_state": {
    "current_phase": "personalize",
    "journey_template_id": "pm_b2b_mid_v3",
    "current_step": 2,
    "steps_completed": ["quick_win_chatgpt"],
    "next_recommended_action": "try cursor for PRD drafting",
    "last_conversation_summary": "Discussed prompt engineering basics. Sarah found chain-of-thought useful. Wants to try it for competitive analysis.",
    "open_questions": ["Does her company allow AI tool installation?"]
  },

  "knowledge_state": {
    "prompt_engineering": {"level": 3, "last_assessed": "2025-04-10", "trend": "improving"},
    "ai_tool_landscape": {"level": 2, "last_assessed": "2025-04-08", "trend": "stable"},
    "workflow_automation": {"level": 1, "last_assessed": null, "trend": null}
  },

  "preferences": {
    "communication_style": "direct, minimal jargon",
    "learning_style": "hands-on, short sessions",
    "session_frequency": "2x per week",
    "tone": "encouraging but not patronizing"
  },

  "interaction_history": [
    {"date": "2025-04-01", "phase": "hook", "summary": "Uploaded resume. Coach identified fintech PM profile.", "tools_used": ["parse_resume", "analyze_role"]},
    {"date": "2025-04-03", "phase": "reveal", "summary": "Showed 3 AI use cases for fintech PM. Sarah was most interested in competitive analysis automation.", "tools_used": ["generate_use_cases"]},
    {"date": "2025-04-08", "phase": "personalize", "summary": "Discussed prompt engineering. Did micro-assessment: scored 3/5.", "tools_used": ["check_knowledge"]}
  ],

  "feedback_signals": {
    "content_thumbs_up": ["article_xyz", "video_abc"],
    "content_thumbs_down": ["course_def"],
    "recommendations_accepted": 4,
    "recommendations_rejected": 1
  }
}
```

---

## Coaching Phases (The Funnel)

### Phase 1: HOOK (First 60 seconds)
**Goal**: User feels understood. Zero friction.

- Entry: upload resume OR type "I'm a [role] at a [company]"
- Coach immediately mirrors back: "Here's what I see about you..."
- Shows 2-3 things it inferred (role archetype, likely daily tasks, seniority)
- Asks: "Did I get this right?" (user corrects or confirms)
- Tools called: `parse_resume` or `analyze_role`, `infer_cultural_tone`

### Phase 2: REVEAL (2-3 minutes)
**Goal**: User feels curiosity. "I didn't know that."

- Coach reveals 1-2 AI blind spots specific to their role
- "Most [role] professionals spend ~X% of time on [task]. AI can cut that by Y%."
- Shows a concrete before/after example
- Doesn't ask the user to do anything yet — just plants seeds
- Tools called: `generate_use_cases`, `analyze_role_detail`

### Phase 3: PERSONALIZE (2-3 minutes)
**Goal**: Coach has enough context to be specific.

- 2-3 targeted conversational questions (not a form):
  - "When you do [inferred task], what's the most tedious part?"
  - "Have you tried any AI tools? Even just ChatGPT?"
  - "What would a win look like for you this month?"
- Answers refine the user model and select/customize a journey template
- Tools called: `assess_skill_gaps`, `find_ai_tools`

### Phase 4: PRESCRIBE (ongoing)
**Goal**: User takes action. One step at a time.

- "Here's your first win: try [specific tool] for [specific task]. Here's how..."
- Provides a specific, 5-minute exercise
- Links to one curated resource (not a list of 10)
- Next session: "How did it go?" → adjust path based on response
- Tools called: `search_content`, `check_knowledge`

### Phase 5: GROW (ongoing, returning sessions)
**Goal**: Retention, deepening, measurable progress.

- Each return session: "Welcome back. Last time you tried X. Let's see how it went."
- Micro-assessments: "Quick question before we continue..."
- Progress visualization: "You've grown from beginner to intermediate in prompt engineering"
- Gradually introduces more advanced concepts and tools
- Tools called: `check_knowledge`, `assess_skill_gaps` (re-assessment)

### Phase Transitions

The coordinator decides when to transition. It's not time-based — it's signal-based:

| From | To | Signal |
|---|---|---|
| Hook | Reveal | User confirmed or corrected profile |
| Reveal | Personalize | User expressed interest ("tell me more") or asked a question |
| Personalize | Prescribe | Coach has enough context for a specific recommendation |
| Prescribe | Grow | User tried the recommended action (or enough time has passed) |
| Any | Any | User asks something that belongs in a different phase |

---

## The Flywheel: How Every User Builds the Moat

```
User in Role X completes journey
        │
        ▼
Journey template for Role X gets validated
(completion rate, satisfaction, which steps worked)
        │
        ▼
Content recommendations get scored
(which articles/videos actually helped?)
        │
        ▼
Role-AI mappings get refined
(which AI opportunities are real vs. theoretical?)
        │
        ▼
Next user in Role X gets a better, faster, cheaper experience
(warm-start from validated template, pre-scored content, proven tools)
        │
        ▼
More users complete → more signal → better templates
        │
        ▼
        ... (flywheel spins)
```

### Specific Flywheel Mechanics

1. **Role Intelligence Enrichment**: Every `parse_resume` → `analyze_role` result that gets user-confirmed adds to the role archetype knowledge base. After 50 confirmed PMs, we know exactly what a PM's day looks like.

2. **Journey Template Validation**: Track which steps users complete vs. skip vs. abandon. A/B test different step orderings. After 100 users through a template, we know the optimal path.

3. **Content Quality Scoring**: Every thumbs-up/down, every "I tried this and it worked/didn't" feeds back to content scores. After 200 ratings, the content library is self-curating.

4. **Tool Recommendation Validation**: "We recommended Cursor for PRD writing. 73% of PMs who tried it rated it 4+/5." This makes future recommendations evidence-based, not LLM-hallucinated.

5. **Knowledge Calibration**: Micro-assessment results across users calibrate difficulty. If 90% of mid-level PMs get question X right, it's too easy for that level.

---

## Build Order

### Phase A: Foundation (Build First)
Get a working conversational coach that can do Phase 1-2 of the funnel.

1. **User Model Store** — persistent JSON/DB per user with profile, state, history
2. **Coach Coordinator** — LLM-based conversation planner with system prompt encoding coaching methodology
3. **Chat UI** — Streamlit chat interface (not pages/forms)
4. **Tool: parse_resume** — refactored from existing, returns structured profile
5. **Tool: analyze_role** — refactored from existing, returns role context
6. **Tool: generate_use_cases** — refactored from existing, returns AI opportunities

With these 6 pieces, a user can: upload resume → get profiled → hear their first "aha" insight. That's the hook.

### Phase B: Personalization (Build Second)
Complete the funnel through Phase 4.

7. **Tool: assess_skill_gaps** — refactored from existing gap agents
8. **Tool: find_ai_tools** — refactored from existing tool recommender
9. **Tool: search_content** — refactored from existing retrieval pipeline
10. **Journey Templates** — initial set for 5-10 common role archetypes
11. **Session Resume Logic** — coordinator reads user model on return, summarizes where they left off

### Phase C: Growth & Moat (Build Third)
Add retention and flywheel mechanics.

12. **Tool: check_knowledge** — micro-assessment generator and scorer
13. **Progress Tracking** — knowledge_state updates, trend visualization
14. **Feedback Collection** — thumbs up/down on every recommendation, stored to user model
15. **Flywheel Writes** — every validated signal writes back to role intelligence, content scores, journey templates
16. **Role Intelligence Seeding** — initial knowledge base for top 10 role archetypes

---

## Tech Decisions

| Decision | Choice | Rationale |
|---|---|---|
| LLM | OpenAI GPT-4 (existing) | Already integrated, good enough for v1 |
| UI | Streamlit chat (st.chat_message) | Already in stack, fast to build, sufficient for v1 |
| User Model Store | JSON files initially → Supabase later | Start simple, migrate when scaling |
| Knowledge Store / RAG | JSON files + in-memory search initially → vector DB later | Don't over-engineer until content volume demands it |
| Session Management | Streamlit session_state + file persistence | Native to Streamlit, works for single-user testing |
| Tool Calling | OpenAI function calling / tool_use | Native LLM capability, clean interface |

---

## What We're NOT Building (Yet)

- Multi-user auth / login (Phase 4 of original roadmap)
- Payment / tiers (Phase 4)
- Real-time external API calls to LinkedIn/YouTube (mock/cache for now)
- Admin dashboard
- Voice / multimodal input
- Mobile app
