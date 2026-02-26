# AI Skill Coaching Platform — Product Specification

## 🎯 Product Vision
A hyper-aware, self-learning AI coaching system that helps product managers become AI-native — not through static courses, but through personalized, contextual, feedback-driven recommendations and experiments.

This system is made up of modular agents that:
- Analyze resumes, LinkedIn profiles, and role contexts
- Detect skill gaps and opportunities
- Recommend learning paths, tools, and real-world experiments
- Learn from every interaction (feedback, usage, success)
- Coordinate with other agents to ensure consistency and intelligence across the stack

## 🔗 Guiding Principles
- **Hyper-personalization:** Every user’s journey is different, and the system reflects that
- **Agentic architecture:** Every agent has a clear purpose, input/output contract, and learning loop
- **Self-improvement:** Agents learn from user feedback and peer patterns
- **Explainability:** Users can always ask, "Why this?" and get a clear answer
- **Actionable > theoretical:** The system should guide users to do, not just learn

## 🧱 System Architecture

### Core Pillars

- **Skill Assessment Agent (parent)**
    - **Resume Agent** ✅
    - **LinkedIn Agent** ✅
    - **Role Detail Agent** ✅
    - **Role Context Agent** ⏳
    - **Tool Familiarity Agent** ⏳
    - **Cultural Alignment Agent** ⏳
    - **Aspiration Agent** ⏳

- **Gap Analysis Agent (parent)**
    - **PM Ladder Mapper Agent** ⏳
    - **Skill Delta Agent** ⏳
    - **Use Case Miss Agent** ⏳
    - **Domain Jump Agent** ⏳
    - **Meta Agent** ⏳

- **Recommendation Agent (parent)**
    - **Use Case Generator Agent** ⏳
    - **Tool Recommender Agent** ⏳
    - **Learning Path Agent** ⏳
    - **Experiment Agent** ⏳
    - **Follow-Up Agent** ⏳
    - **Agent Orchestrator** ⏳

- **User Dashboard + Admin Dashboard** ⏳

## 🧠 Agent Intelligence Framework (10 Points)

All agents must follow this self-awareness and evolution framework:

1. **Purpose & Scope** — what it does and doesn’t do
2. **Output Design** — ideal structure, formatting, clarity, reuse
3. **Learning & Self-Improvement** — feedback, corrections, peer patterns
4. **User Interaction** — editable previews, thumbs up/down, corrections
5. **Downstream Integration** — schema contracts between agents
6. **Multimodality & Intelligence Extenders** — voice, images, DB lookups
7. **Metrics** — usage, output quality, impact
8. **Configurability** — lean mode, debug mode, learning mode
9. **Edge Cases & Fallbacks** — if data is missing or malformed
10. **Data Ethics & Privacy** — anonymization, opt-out, GDPR compliance

## 🚦 Roadmap by Phase

- **✅ Phase 1: Foundation (Complete)**
    - Resume Agent v2
    - LinkedIn Agent v2
    - Modular folder and UI structure
    - main.py orchestration starter

- **🚧 Phase 2: Productization & Intelligence (In Progress)**
    - /agent_core utility module system (10 core utilities) ✅
    - Role Detail Agent v2 — modularized with utilities, structured output, editable UI ✅
    - Feedback systems and downstream preview across agents ⏳
    - Shared user context store ⏳

- **🔭 Phase 3: Differentiation Engine**
    - Real content API hooks (YouTube, Replit, etc.)
    - Bookmarking and progress tracking
    - Meta Agent peer signal feedback
    - Smart follow-up agent
    - Experiment scoring and history

- **☁️ Phase 4: SaaSification & Moat**
    - Google login, secure storage
    - Hosted backend (FastAPI + Supabase/Firebase)
    - Stripe integration (free vs. pro vs. team)
    - Moat definition: feedback flywheel, persona-based learning, self-tuning agents

## 🔐 Data & Compliance Strategy
- No PII stored without consent
- Resume/LinkedIn stored in vector or structured form (not raw)
- Opt-out + forget-my-data buttons
- Feedback logs for agent learning
- Clear consent screen before data ingestion

## 🔄 Self-Learning Goals (All Agents)
- Improve accuracy via feedback
- Adapt language/tone to user style
- Learn which paths work for whom
- Share signals across agents to reinforce or challenge conclusions
