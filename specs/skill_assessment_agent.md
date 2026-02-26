SkillAssessmentAgent V2 Spec

🎯 Narrative and Purpose

The Skill Assessment Agent is not just a data aggregator — it’s the conductor of the entire onboarding experience. It sets the tone for the platform’s intelligence, responsiveness, and understanding of the user. By orchestrating and synthesizing outputs from various assessment-focused child agents, it offers:

A seamless, guided experience that builds trust and forward momentum.

A clear summary of who the user is today — professionally, behaviorally, and aspirationally.

A persistent, structured skill profile that downstream agents use for learning paths, gap analysis, recommendations, and future personalization.

Business Purpose: SkillAssessmentAgent controls the user’s initial product journey. It unifies all early insights, validates agent coverage, and ensures readiness for subsequent phases. It also reduces user cognitive load by turning raw AI outputs into a coherent story.

✅ Goal Clarity

Aspect

Details

Primary Goal

Orchestrate, validate, and synthesize outputs from foundational skill-related child agents into a structured, persistent skill_profile.

Scope

Uses data stored in global_agent_memory from each child agent — does not do any parsing/inference itself.

User Role

Presents the user with a clear, summarized profile and allows them to correct/adjust parts of it.

System Role

Feeds downstream agents with reliable, tagged, versioned skill data.

🧾 Input Quality & Context

Inputs are retrieved from global_agent_memory.py (not called live):

Source Agent

Data Pulled

ResumeAgent

Title, domain, company, tools, AI relevance

LinkedInAgent

Verified skills, endorsements, role timeline

AspirationAgent

Future role goals, interests, leadership vs IC preference

CulturalAlignmentAgent

Work style preferences, communication fit

RoleDetailAgent

Tasks, workflows, AI opportunity level

RoleContextAgent

Scope, maturity stage, strategic positioning

ToolFamiliarityAgent

Tool exposure + proficiency

All retrieved data is validated for structure and completeness via input_evaluation.py.

📤 Output Usefulness (User + System)

Consumer

Purpose

GapAnalysisAgent

Uses current skill profile to detect missing skills vs aspirations.

SkillDeltaAgent

Measures proficiency delta to target level.

MetaAgent

Compares with anonymized peer profiles.

User (via UI)

Sees clean, readable summary of background, strengths, and areas to improve.

Output structure formatted via downstream_formatter.py

Payload includes source_agent, confidence_score, version, timestamp

Stored persistently for future use, review, and rerun

🔁 Downstream Compatibility

Versioned JSON structure (v1.0, v2.0, etc.)

Consistent field names and tags

Rich metadata included for each block (e.g., tool, aspiration, skill, etc.)

🔄 Feedback & Learning (Per-Agent Loop)

Captures user feedback (thumbs up/down, field edit)

Feedback routed back to specific upstream agents via feedback_utils.py

Triggers self_learning.py logic to improve agent-specific prompts, data quality, etc.

Example: User downvotes "LLM" exposure → Signal sent to ResumeAgent for resume parsing refinement.

🧠 Experience Flow (Orchestration + Progression)

Child agent insights are collected and shown in this order:

Resume Upload (ResumeAgent)

LinkedIn Import (LinkedInAgent)

Career Aspiration (AspirationAgent)

Work Style/Culture (CulturalAlignmentAgent)

Daily Role Details (RoleDetailAgent)

Org/Scope Context (RoleContextAgent)

Final Summary View (SkillAssessmentAgent)

Each step runs async (where possible)

Show progressive insights in UI as steps complete

Tee up downstream agents (e.g., gap, learning) in background as summary is shown

📈 Success Metrics

Metric

Target

Profile Coverage (Fields filled)

>90%

Feedback Positivity (avg thumbs up)

>85%

Downstream Agent Acceptance Rate

>90% without revalidation needed

Perceived Onboarding Flow Rating

>4.5/5 via user NPS follow-up

🧾 Validation of Freeform Input

User-edited fields are re-validated via LLM prompt

Use persona_context.py to set tone for prompting

Examples and suggestions returned via chat applet for self-correction

🔧 Utilities & Logging

agent_logger.py

input_evaluation.py

global_agent_memory.py

feedback_utils.py

self_learning.py

trust_explainability.py

persona_context.py

timing_utils.py

downstream_formatter.py

🖼 UI Design & Flow (skill_assessment_view.py)

Stepwise, frictionless UI (resume → LinkedIn → aspiration → ... → summary)

Each stage allows preview + corrections

Inline feedback buttons

Live LLM chat applet for clarification, suggestions, rewording

Session state used to store partial progress

Tone matched to user persona using persona_context

🧩 A2A and Scalability Readiness

Every field wrapped in {"agent_origin": X, "data": {...}}

Version metadata included

Retry logic for missing/invalid child agent data

Async support for running multiple assessments in parallel

Optional schema manifest exposure for cross-platform coordination

📦 Deliverables

agents/skill_assessment/skill_assessment_agent.py

agents/skill_assessment/skill_assessment_helpers.py

pages/skill_assessment_view.py

New utilities if needed (e.g., orchestration manager)

