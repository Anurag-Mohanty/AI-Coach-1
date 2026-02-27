# AI Coach — Project Review, Spec & Implementation Plan

## Part 1: Honest Assessment of What Exists

### What's Built and Working (Conceptually)

You have **~70 files of agent code** across 4 layers. Here's what actually exists:

#### Layer 1: Assessment Agents (Most Complete)
| Agent | Location | Status | Notes |
|-------|----------|--------|-------|
| Resume Agent | `tools/resume/` | v2 done | Schema-validated, memory-free, clean |
| LinkedIn Agent | `tools/linkedin/` | v2 done | Memory-free, LLM-driven extraction |
| Role Context Agent | `tools/role_context_agent/` | v2 done | LLM-driven org/role inference |
| Role Detail Agent | `tools/role_detail/` | v2 done | Uses prompt_builder, downstream formatting |
| Tool Familiarity Agent | `tools/tool_familiarity_agent/` | v2 done | LLM-driven tool inference, UI confirmation |
| Cultural Alignment Agent | `tools/cultural_alignment_agent/` | v2 done | Tone profiling, learning preference |
| Aspiration Agent | `agents/skill_assessment_agent/` | v2 done | Career trajectory inference via LLM |

#### Layer 2: Gap Analysis Agents (Mostly Stub/V1)
| Agent | Location | Status | Notes |
|-------|----------|--------|-------|
| Role Ladder Agent | `agents/gap_analysis_agent/role_ladder_agent/` | v2 partial | Uses prompt_builder but has duplicate LLM call (line 64-66 calls model twice) |
| Skill Delta Agent | `agents/gap_analysis_agent/` | v1 stub | Simple set-difference, no LLM, no real analysis |
| Use Case Miss Agent | `agents/gap_analysis_agent/` | v1 stub | Keyword matching, hardcoded AI suggestions |
| Domain Jump Agent | `agents/gap_analysis_agent/` | v1 stub | Hardcoded for 3 domains (healthcare, fintech, adtech), no LLM |
| Meta Agent | `agents/gap_analysis_agent/` | v1 stub | Returns hardcoded peer patterns, no real data |

#### Layer 3: Recommendation Agents (Mixed)
| Agent | Location | Status | Notes |
|-------|----------|--------|-------|
| Use Case Generator | `agents/recommendation_agent/` | v1 | Simple LLM prompt, works but shallow |
| Tool Recommender | `agents/recommendation_agent/` | v1 | Simple LLM prompt |
| Content Recommendation Pipeline | `agents/recommendation_agent/content_recommendation/` | **Most sophisticated** | Query planner + 4 source retrievers + reflection + scoring. This is your best work. |
| Learning Path Pipeline | `agents/recommendation_agent/learning_path/` | v2 | 5 sub-agents, LLM-driven step narration |

#### Layer 4: Feedback/Follow-up (Placeholder)
| Agent | Location | Status | Notes |
|-------|----------|--------|-------|
| Follow-Up Agent | `agents/test_agent/` | v1 stub | Hardcoded nudge logic, no LLM |
| Feedback Agent | `agents/test_agent/` | v1 stub | Returns mock data, entirely placeholder |
| Experiment Agent | `agents/test_agent/` | v1 stub | Template fill, no intelligence |

#### Infrastructure (`agent_core/`)
| Module | Status | Notes |
|--------|--------|-------|
| llm_client.py | Working | GPT-4 hardcoded, simple wrapper |
| prompt_builder.py | Working | Template-driven, supports memory/learning |
| prompt_task_templates.py | Working | 4 templates defined (domain_jump, ladder, role_detail, role_context) |
| global_agent_memory.py | Working but fragile | In-memory dict, lost on restart |
| persona_context.py | Working | File-based JSON |
| agent_logger.py | Working | JSONL file logging |
| input_evaluation.py | Working but has duplicate code | Logger functions duplicated at bottom |
| feedback_utils.py | Working | File-based feedback capture |
| self_learning.py | Partial | Framework exists, mostly stubs |
| trust_explainability.py | Working | Simple explanation generator |
| compliance_utils.py | Working | PII removal, consent tracking |
| downstream_formatter.py | Working | Hardcoded agent mapping |
| timing_utils.py | Working | Decorator-based, Streamlit-aware |
| content_cache.py | Working | File-based with metadata index |
| context_utils.py | Working | Enriched context builder |

#### Schemas
- `user_current_capabilities.schema.json` — used by resume agent
- `user_gap_analysis.schema.json` — defined but not wired
- `user_target_role_profile.schema.json` — defined but not wired

---

## Part 2: The Core Problem — Why It Feels Like a Workflow

### Problem 1: Linear Pipeline, Not a Coach
`ui.py` runs every agent top-to-bottom in a fixed sequence. The user presses "Analyze Profile" and gets a wall of JSON dumps. There is:
- No conversation
- No ability to say "tell me more about X" or "I disagree with Y"
- No coaching dialogue
- No iterative refinement
- No decision points where the coach asks the user what to focus on

**This is the fundamental issue.** A coach listens, asks questions, proposes directions, adjusts based on response. Your system dumps everything at once.

### Problem 2: No Orchestrator with Agency
`skill_assessment_agent.py` attempts orchestration but it's just a `for agent in AGENT_SEQUENCE` loop. There is no:
- Intent detection — what does the user actually want right now?
- Dynamic routing — which agents are relevant given what we already know?
- State machine — what phase of coaching are we in?
- Re-entry logic — user comes back 2 weeks later, what's changed?

### Problem 3: Two Codebases, Neither Complete
- `tools/` has v2 agents (resume, linkedin, role_context, etc.) — these are clean, schema-validated, memory-free
- `agents/` has a different structure with its own copies and import paths
- `ui.py` imports from a THIRD flat structure (pre-modularization) that doesn't exist anymore
- The `pages/` directory referenced everywhere doesn't exist in the current repo

### Problem 4: Hardcoded Logic Where Intelligence Should Be
- `domain_jump_agent.py` — knows only 3 domains via if/elif
- `meta_agent.py` — returns `['Replit', 'LangChain', 'Pinecone']` for everyone
- `skill_delta_agent.py` — does `set(required) - set(current)`, no nuance
- `follow_up_agent.py` — hardcoded day-count nudges
- `feedback_agent.py` — returns mock data

### Problem 5: No Training Quality Evaluation
You specifically want: "evaluate if the training provided is actually relevant to the role." The reflection agent does basic filtering during retrieval, but there is no post-recommendation agent that:
- Evaluates training quality against the user's specific gap
- Scores whether a course will actually move the needle
- Flags low-quality or outdated content
- Validates that the training matches the role level (not too basic, not too advanced)

### Problem 6: Inconsistent Agent Contracts
- Some agents take `(user_id, session_id)` and pull from memory
- Some take raw data `(parsed_resume, aspiration_result)`
- Some are async, some sync
- `timed_function` decorator converts sync to async silently
- The `store_memory` function signature differs between usages (some call with positional args, some with keyword args)

---

## Part 3: What the System SHOULD Be

### Vision: A Conversational Multi-Agent Coach

The system should behave like a senior career coach who:

1. **Onboards you** — understands who you are from your resume/LinkedIn
2. **Asks clarifying questions** — "I see you're a Senior PM in healthcare. Are you looking to grow deeper in healthcare or switch domains?"
3. **Builds a profile** — synthesizes assessment, not dumps raw JSON
4. **Identifies gaps** — "Based on where you want to go, here are the 3 biggest gaps I see..."
5. **Proposes a plan** — "Here's a 4-week learning plan. Would you like to adjust the pace or focus?"
6. **Finds training** — retrieves actual resources and explains WHY each one matters
7. **Evaluates training quality** — "I found 8 courses but only 3 are actually worth your time. Here's why."
8. **Follows up** — "You started the LangChain course last week. How's it going? Want to try something different?"
9. **Adapts** — learns from feedback, adjusts recommendations

### Architecture: Coordinator + Specialist Agents

```
                    ┌─────────────────────┐
                    │   Coach Coordinator  │  ← The "brain" — decides what to do next
                    │   (Orchestrator)     │     based on conversation state
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼────┐  ┌───────▼──────┐  ┌──────▼───────┐
    │  Assessment   │  │ Gap Analysis │  │Recommendation│
    │  Cluster      │  │ Cluster      │  │  Cluster     │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                  │
    ┌──────┴──────┐   ┌──────┴──────┐   ┌──────┴──────┐
    │Resume       │   │Role Ladder  │   │Content Reco │
    │LinkedIn     │   │Skill Delta  │   │Learning Path│
    │Role Context │   │Use Case Miss│   │Use Case Gen │
    │Role Detail  │   │Domain Jump  │   │Tool Recomm  │
    │Tool Familiar│   │Meta Agent   │   │Training Eval│
    │Cultural     │   └─────────────┘   └─────────────┘
    │Aspiration   │
    └─────────────┘
              │
    ┌─────────▼────────────┐
    │   Session Memory     │  ← Persistent across conversation
    │   (User Profile +    │     turns, not just in-memory dict
    │    Coaching State)    │
    └──────────────────────┘
```

The **Coach Coordinator** is the key missing piece. It:
- Maintains conversation state (what phase we're in, what's been discussed)
- Decides which agent(s) to invoke based on the conversation
- Synthesizes agent outputs into coach-like responses
- Asks follow-up questions when information is incomplete
- Proposes next steps and lets the user choose

---

## Part 4: Comprehensive Spec

### 4.1 Agent Contracts (Standardized)

Every agent MUST follow this contract:

```python
class AgentResult:
    data: dict          # The structured output
    confidence: float   # 0.0 to 1.0
    explanation: str    # Why this output
    suggestions: list   # What to explore next
    needs_input: list   # Fields that are missing/weak
```

Every agent function MUST have this signature:

```python
async def run(context: CoachingContext) -> AgentResult:
    """
    context contains:
      - user_profile: dict (accumulated from all assessment agents)
      - session_state: dict (what's happened this session)
      - coaching_phase: str (onboarding | assessment | gap_analysis | planning | training | follow_up)
      - conversation_history: list (for multi-turn awareness)
      - user_preferences: dict (tone, pace, depth)
    """
```

### 4.2 Coaching Phases (State Machine)

```
ONBOARDING → ASSESSMENT → GAP_ANALYSIS → PLANNING → TRAINING → FOLLOW_UP
    │              │            │             │           │          │
    └──────────────┴────────────┴─────────────┴───────────┴──────────┘
                        (can revisit any phase)
```

**ONBOARDING**: Collect resume, LinkedIn, aspirations via conversation
**ASSESSMENT**: Run assessment agents, present synthesized profile, get corrections
**GAP_ANALYSIS**: Identify gaps, present them conversationally, ask for prioritization
**PLANNING**: Build learning plan, get user buy-in on pace/focus
**TRAINING**: Find and evaluate training content, present curated recommendations
**FOLLOW_UP**: Check progress, adjust plan, re-assess if needed

### 4.3 Coach Coordinator Spec

The Coordinator is an LLM-powered agent that:

1. **Receives user messages** (text input via chat interface)
2. **Maintains state** in a `CoachingContext` object
3. **Decides action** — which specialist agent(s) to call
4. **Synthesizes response** — takes agent outputs and generates a coaching response
5. **Tracks progress** — knows what's been done, what's pending

It does NOT replace the specialist agents. It USES them as tools.

### 4.4 Training Evaluator Agent (New)

A new agent that:
- Takes a training resource + user profile + target gap
- Evaluates: relevance (0-10), level-appropriateness (0-10), quality signals (recency, source reputation, engagement metrics), estimated time-to-value
- Returns: keep/skip recommendation with explanation
- Filters out: outdated content, wrong-level content, clickbait, generic courses

### 4.5 Session Memory (Replacing In-Memory Dict)

Replace `global_agent_memory.py` in-memory dict with:
- File-based session store (JSON files per user per session)
- Accumulated user profile that persists across sessions
- Coaching state that tracks what's been discussed and decided
- Feedback history that feeds into prompt improvement

---

## Part 5: What Needs to Change vs. What to Keep

### KEEP (These are solid)
1. `tools/resume/resume_agent.py` — clean, schema-validated, memory-free pattern
2. `tools/linkedin/linkedin_agent.py` — same clean pattern
3. `tools/role_context_agent/` — good LLM-driven analysis
4. `tools/role_detail/` — good prompt_builder usage
5. `tools/tool_familiarity_agent/` — good structure
6. `tools/cultural_alignment_agent/` — good tone profiling
7. `agents/skill_assessment_agent/aspiration_agent.py` — good career trajectory inference
8. Content recommendation pipeline (`agents/recommendation_agent/content_recommendation/`) — most sophisticated part, keep and integrate
9. Learning path pipeline (`agents/recommendation_agent/learning_path/`) — keep and integrate
10. `agent_core/prompt_builder.py` + `prompt_task_templates.py` — good pattern
11. `agent_core/compliance_utils.py` — PII handling is solid
12. `schemas/` — good schema validation pattern, needs more schemas
13. `services/schema_loader.py` — clean

### REWRITE (Logic exists but is too shallow)
1. `agents/gap_analysis_agent/skill_delta_agent.py` — needs LLM, not set difference
2. `agents/gap_analysis_agent/use_case_miss_agent.py` — needs LLM, not keyword matching
3. `agents/gap_analysis_agent/domain_jump_agent.py` — needs LLM, not hardcoded domains
4. `agents/gap_analysis_agent/meta_agent.py` — needs real peer pattern logic or LLM
5. `agents/recommendation_agent/use_case_generator_agent.py` — needs richer context
6. `agents/recommendation_agent/tool_recommender.py` — needs richer context
7. `agents/test_agent/follow_up_agent.py` — needs LLM, not hardcoded nudges
8. `agents/test_agent/experiment_agent.py` — needs LLM
9. `agents/test_agent/feedback_agent.py` — entirely placeholder, needs real implementation

### BUILD NEW
1. **Coach Coordinator** — the orchestrating brain
2. **Training Evaluator Agent** — validates training quality/relevance
3. **Chat Interface** — replace monolithic Streamlit with conversational UI
4. **Session Store** — persistent file-based memory replacing in-memory dict
5. **Standardized Agent Base** — base class/contract all agents follow
6. **Router/Dispatcher** — maps user intent to agent invocation

### DELETE / ARCHIVE
1. `ui.py` — the monolithic workflow UI (archive for reference)
2. `sandbox/to be trashed/` — already flagged for deletion
3. Duplicate code in `agent_core/input_evaluation.py` (has logger functions that duplicate `agent_logger.py`)

---

## Part 6: Implementation Plan

### Phase 0: Foundation Cleanup (Do First)
**Goal**: Clean up the codebase so we can build on a solid foundation.

1. **Standardize agent contract** — create `agent_core/base_agent.py` with `AgentResult` dataclass and `run(context)` signature pattern
2. **Fix the duplicate code** — remove logger functions from `input_evaluation.py` (they duplicate `agent_logger.py`)
3. **Consolidate agent locations** — move assessment agents from `tools/` into `agents/assessment/` for consistency (or vice versa; pick ONE convention)
4. **Fix role_ladder_agent.py** — remove the duplicate LLM call on lines 64-66
5. **Create `CoachingContext` dataclass** — the shared context object all agents will receive
6. **Create persistent session store** — `services/session_store.py` replacing in-memory dict with file-based JSON per user
7. **Add missing schemas** — linkedin analysis schema, gap analysis output schemas, role context schema

### Phase 1: Build the Coach Coordinator
**Goal**: Create the orchestrating brain that makes this feel like a coach, not a pipeline.

1. **Create `agents/coordinator/coach_coordinator.py`** — LLM-powered coordinator that:
   - Receives user message + current CoachingContext
   - Decides which phase we're in and what to do next
   - Calls specialist agents as needed
   - Synthesizes a conversational response
   - Updates coaching state

2. **Create `agents/coordinator/intent_detector.py`** — classifies user intent:
   - `provide_info` — user is sharing resume/linkedin/context
   - `ask_question` — user wants to know something
   - `give_feedback` — user is correcting or rating
   - `request_action` — user wants a plan, training, etc.
   - `navigate` — user wants to go to a different phase

3. **Create `agents/coordinator/response_synthesizer.py`** — takes raw agent outputs and generates coach-like responses (not JSON dumps)

4. **Create the chat interface** — `app.py` with a simple Streamlit chat UI that talks to the coordinator

### Phase 2: Upgrade Gap Analysis Agents
**Goal**: Replace stub logic with LLM-driven intelligence.

1. **Rewrite `skill_delta_agent.py`** — use LLM to:
   - Compare current skills (from resume/linkedin) against target role requirements
   - Assess depth of each gap (surface awareness vs. deep competency)
   - Prioritize gaps by impact on target role
   - Suggest which gaps are quickest to close vs. longest to develop

2. **Rewrite `domain_jump_agent.py`** — use LLM to:
   - Analyze transferable skills across ANY domains (not just 3 hardcoded)
   - Identify mindset shifts needed
   - Map analogous concepts between domains
   - Generate a bridge narrative

3. **Rewrite `use_case_miss_agent.py`** — use LLM to:
   - Analyze user's current workflow for AI automation opportunities
   - Score each opportunity by impact and ease
   - Suggest specific AI tools for each opportunity
   - Estimate time savings

4. **Rewrite `meta_agent.py`** — use LLM to:
   - Generate realistic peer comparisons based on role/seniority/domain
   - Identify what successful people in similar roles typically learn
   - Surface patterns from the user's profile that suggest specific paths

### Phase 3: Build Training Evaluator
**Goal**: Add the agent that evaluates whether training is actually worth the user's time.

1. **Create `agents/recommendation_agent/training_evaluator_agent.py`** — evaluates each training resource against:
   - Relevance to user's specific gap (not generic)
   - Level appropriateness (not too basic, not too advanced)
   - Content quality signals (recency, source reputation, duration)
   - Estimated time-to-value
   - Returns: keep/skip with explanation

2. **Wire into content recommendation pipeline** — after retrieval + reflection, before presenting to user

3. **Create evaluation schema** — `schemas/training_evaluation.schema.json`

### Phase 4: Upgrade Feedback & Follow-up
**Goal**: Make the coaching loop actually close.

1. **Rewrite `feedback_agent.py`** — real implementation that:
   - Captures structured feedback per recommendation
   - Routes feedback to `self_learning.py` for prompt improvement
   - Adjusts future recommendations based on what worked/didn't

2. **Rewrite `follow_up_agent.py`** — LLM-driven that:
   - Understands what the user was working on
   - Checks against timeline
   - Suggests contextual next steps (not generic nudges)
   - Can re-assess if user's goals have shifted

3. **Rewrite `experiment_agent.py`** — LLM-driven that:
   - Designs specific, time-boxed experiments
   - Provides step-by-step instructions
   - Defines success criteria
   - Connects back to the gap it's meant to close

### Phase 5: Chat Interface & Integration
**Goal**: Tie everything together in a conversational experience.

1. **Build `app.py`** — Streamlit chat interface:
   - Chat input/output
   - File upload for resume
   - Sidebar showing coaching progress
   - Ability to view/edit profile
   - Training plan view

2. **Wire coordinator to all agents** — ensure the coordinator can invoke any agent and synthesize results

3. **Implement multi-turn memory** — conversation history that the coordinator uses to maintain context

4. **Add "why this?" capability** — user can ask why any recommendation was made, coordinator routes to trust_explainability

### Phase 6: Polish & Self-Learning
**Goal**: Make the system get smarter over time.

1. **Activate self_learning.py** — currently framework-only, wire it to actual prompt improvements
2. **Implement prompt versioning** — track which prompt versions perform better
3. **Add dashboard** — admin view of agent performance, feedback trends, common gaps
4. **End-to-end testing** — test the full coaching flow from onboarding to training

---

## Part 7: File Structure After Implementation

```
AI-Coach-1/
├── app.py                              # NEW: Chat-based Streamlit entry point
├── agents/
│   ├── __init__.py
│   ├── coordinator/                    # NEW: The coaching brain
│   │   ├── coach_coordinator.py        # Main orchestrator
│   │   ├── intent_detector.py          # User intent classification
│   │   ├── response_synthesizer.py     # Agent output → coach response
│   │   └── coaching_phases.py          # State machine definitions
│   ├── assessment/                     # MOVED: from tools/
│   │   ├── resume_agent.py             # KEEP as-is
│   │   ├── resume_parser.py            # KEEP
│   │   ├── resume_utils.py             # KEEP
│   │   ├── linkedin_agent.py           # KEEP as-is
│   │   ├── role_context_agent.py       # KEEP as-is
│   │   ├── role_detail_agent.py        # KEEP as-is
│   │   ├── tool_familiarity_agent.py   # KEEP as-is
│   │   ├── cultural_alignment_agent.py # KEEP as-is
│   │   ├── tone_profile_engine.py      # KEEP
│   │   └── aspiration_agent.py         # KEEP as-is
│   ├── gap_analysis/                   # REWRITE: LLM-driven
│   │   ├── role_ladder_agent.py        # FIX (remove dupe call) + minor cleanup
│   │   ├── skill_delta_agent.py        # REWRITE with LLM
│   │   ├── use_case_miss_agent.py      # REWRITE with LLM
│   │   ├── domain_jump_agent.py        # REWRITE with LLM
│   │   └── meta_agent.py              # REWRITE with LLM
│   ├── recommendation/                 # KEEP + ADD
│   │   ├── use_case_generator_agent.py # ENHANCE with richer context
│   │   ├── tool_recommender.py         # ENHANCE with richer context
│   │   ├── training_evaluator_agent.py # NEW
│   │   ├── content_recommendation/     # KEEP as-is (your best work)
│   │   │   ├── retrieval_orchestrator.py
│   │   │   ├── query_planner_agent.py
│   │   │   ├── reflection_agent.py
│   │   │   ├── content_scorer.py
│   │   │   ├── content_recommender_agent.py
│   │   │   ├── perplexity_search.py
│   │   │   ├── youtube_retriever_agent.py
│   │   │   ├── github_retriever_agent.py
│   │   │   ├── linkedin_retriever_agent.py
│   │   │   ├── content_explainer.py
│   │   │   ├── content_segmenter.py
│   │   │   └── research_agent.py
│   │   └── learning_path/              # KEEP as-is
│   │       ├── learning_path_agent.py
│   │       ├── intro_agent.py
│   │       ├── path_summary_agent.py
│   │       ├── gap_insight_agent.py
│   │       ├── learning_steps_agent.py
│   │       └── closing_cta_agent.py
│   └── coaching/                       # REWRITE
│       ├── feedback_agent.py           # REWRITE with real implementation
│       ├── follow_up_agent.py          # REWRITE with LLM
│       └── experiment_agent.py         # REWRITE with LLM
├── agent_core/                         # KEEP + FIX
│   ├── base_agent.py                   # NEW: Standardized agent contract
│   ├── coaching_context.py             # NEW: Shared context dataclass
│   ├── llm_client.py                   # KEEP (maybe add model configurability)
│   ├── prompt_builder.py               # KEEP
│   ├── prompt_task_templates.py        # KEEP + ADD more templates
│   ├── global_agent_memory.py          # KEEP (used by session_store)
│   ├── persona_context.py              # KEEP
│   ├── agent_logger.py                 # KEEP
│   ├── input_evaluation.py             # FIX: remove duplicate logger code
│   ├── feedback_utils.py               # KEEP
│   ├── self_learning.py                # ENHANCE: wire to actual prompts
│   ├── trust_explainability.py         # KEEP
│   ├── compliance_utils.py             # KEEP
│   ├── downstream_formatter.py         # KEEP
│   ├── timing_utils.py                 # KEEP
│   ├── content_cache.py                # KEEP
│   ├── context_utils.py                # KEEP
│   └── dashboard_hooks.py              # KEEP
├── services/
│   ├── memory_store.py                 # KEEP
│   ├── session_store.py                # NEW: Persistent session management
│   └── schema_loader.py               # KEEP
├── schemas/                            # KEEP + ADD
│   ├── user_current_capabilities.schema.json
│   ├── user_gap_analysis.schema.json
│   ├── user_target_role_profile.schema.json
│   ├── linkedin_analysis.schema.json   # NEW
│   ├── training_evaluation.schema.json # NEW
│   └── coaching_state.schema.json      # NEW
├── specs/                              # KEEP
└── sandbox/                            # KEEP for testing
```

---

## Part 8: Priority Order

If you can only do some of this, here's the impact-ordered priority:

1. **Phase 1 (Coach Coordinator + Chat UI)** — This is the single biggest change. It transforms the system from a pipeline to a coach. Without this, nothing else matters.

2. **Phase 0 (Foundation Cleanup)** — Do this IN PARALLEL with Phase 1. Clean contracts, fix bugs, consolidate locations.

3. **Phase 2 (Gap Analysis Rewrites)** — These are the agents that make the coaching insightful. LLM-driven gap analysis is what makes recommendations meaningful.

4. **Phase 3 (Training Evaluator)** — This is your stated differentiator: evaluating whether training is actually worth doing.

5. **Phase 4 (Feedback/Follow-up)** — Closes the coaching loop. Important but can come after the core flow works.

6. **Phase 5 (Integration)** — Wire everything together in the chat experience.

7. **Phase 6 (Polish)** — Self-learning, dashboards, prompt versioning.

---

## Part 9: Key Design Decisions Needed

Before implementation, you should decide:

1. **LLM Provider**: Currently hardcoded to `gpt-4`. Do you want to stay OpenAI-only or add Claude/other providers? The `llm_client.py` abstraction makes this easy to change.

2. **Persistence**: File-based JSON is fine for a prototype. Do you want to move to a real database (SQLite at minimum, Supabase for SaaS)?

3. **Chat Framework**: Pure Streamlit chat, or do you want to use something like Chainlit or a custom frontend?

4. **Multi-user**: The current system has `user_id` everywhere but no authentication. Is this single-user for now?

5. **Deployment**: Currently Replit-targeted. Staying there or moving?

6. **Scope**: Do you want to keep the PM/product focus, or make this role-agnostic from the start?
