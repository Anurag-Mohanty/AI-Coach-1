Role Context Agent – V2 Specification

Location: agents/skill_assessment_agent/role_context/role_context_agent.pyPurpose: Contextualizing roles beyond titles — to power intelligent AI personalization.

📍 Overview & Purpose

The Role Context Agent serves as the company-aware interpreter of vague or misleading job titles. It works in conjunction with the role_detail_agent, but its focus is distinct: while the role detail agent figures out what the user does, the role context agent asks:

“What does this role mean in this company, team, and domain?”

This agent pulls in signals from the resume, LinkedIn, and other upstream agents to map a user’s title, team, and environment to a richer understanding of scope, decision-making, structure, and potential for AI upskilling. Think of it as a semantic zoom lens on the role — one that helps every downstream agent make smarter decisions about what to recommend or skip.

It is also the first agent that introduces organizational archetyping — inferring patterns like “solo IC PM in a matrixed org” or “ops-heavy PM at a budget-strapped nonprofit.” These patterns drive not only downstream recommendations but how the platform interprets ambition, skill gaps, and upskilling readiness.

🌟 Core Objectives

The role context agent is responsible for the following:

Disambiguate TitlesInterpret vague or inflated titles (e.g., “Product Manager,” “Lead”) based on company context.

Infer Org Structure & FunctionalityUnderstand how decisions are made (centralized vs distributed), how teams collaborate (async vs sync), and what cross-functional dependencies exist.

Assess AI Enablement & ConstraintsIdentify cultural, technical, or structural blockers/enablers to adopting AI-driven tools.

Classify Role ArchetypesApply internal taxonomy like infra_ic_pm, cross-org_generalist, or ops-heavy_strategist for role modeling and benchmarking.

Guide Tone & Realism in RecommendationsFlag when to tone down aspirational recommendations or double down on foundational tooling.

📅 Inputs & Sources

The Role Context Agent operates downstream from multiple assessment agents and consumes the following fields:

Source

Fields

Purpose

Resume Agent

title, seniority, company, company_size, team_size, domain

Anchors the analysis in core role signals

LinkedIn Agent

tenure, cross_functional_density, engagement_scope

Indicates exposure and team integration

Role Detail Agent

task_clusters, effort_distribution, frequency_map

Adds behavioral and cadence-level context

Aspiration Agent (optional)

future_goals, ideal_role_flavor

Enables a comparison between current constraints and future ambitions

All incoming fields are first validated using input_evaluation.py, with fallbacks if missing.

Where data is missing or ambiguous, the agent calls on global_agent_memory.py to:

Retrieve cached versions of this user’s previous run

Pull archetypes or organizational flags from similar users or roles

📤 Outputs

The core output of the Role Context Agent is a rich JSON object that includes interpretive fields and context-aware metadata. A sample looks like:

{
  "contextualized_role_type": "Ops-heavy IC PM in enterprise SaaS",
  "org_shape_inference": "matrixed",
  "cross_functional_density": "high",
  "ops_or_strategy_bias": "execution-heavy",
  "ai_applicability_constraints": "limited due to internal tooling gaps",
  "role_archetype_tag": "infra_ic_pm",
  "upskilling_infra_quality": "moderate – external learning preferred",
  "training_access_signal": "enabled but requires initiative",
  "recommendation_tone_flag": "de-emphasize org-wide automation",
  "confidence_score": 0.87,
  "reasoning_log": "Company size + effort on operational tasks → matrixed, IC-heavy role; no evidence of strategic ownership.",
  "feeds": ["skill_delta_agent", "use_case_miss_agent", "role_ladder_agent", "meta_agent"]
}

🔄 Agent Lifecycle & Flow

Input ValidationValidate that required fields are present (title, company, domain at minimum). If not, flag and log via agent_logger.py.

Prompt ConstructionBuild a narrative prompt using the inputs, current persona context, and company norms pulled from global_agent_memory.py.

LLM InvocationCall OpenAI (or other model endpoint) with well-structured prompt. Wrap call with timed_function() to track execution time.

Output Structuring & FormattingParse response and normalize values using internal taxonomies. Score quality. Format using downstream_formatter.py.

Feedback & Self-LearningAwait thumbs-up/down feedback from users or downstream agents. If accuracy drops, call auto_adjust_prompt_if_downvoted().

Memory + CachingSave structured context output in global_agent_memory.py. Anonymized versions stored for analytics or pattern learning.

🛠️ Utility Modules Used

Utility

Function

feedback_utils.py

Capture field-level thumbs up/down and correction notes

input_evaluation.py

Detects missing inputs or ambiguous titles

agent_logger.py

Tracks run logs and failures

self_learning.py

Adjusts prompt or internal logic based on performance

trust_explainability.py

Explains why fields were inferred, including model confidence

downstream_formatter.py

Converts raw output into payloads per target agent

global_agent_memory.py

Stores past role contexts and retrieves organizational patterns

timing_utils.py

Logs how long each step took, used for performance monitoring

compliance_utils.py

Removes PII, hashes sensitive info

persona_context.py

Pulls in persona and aspiration context

dashboard_hooks.py

Reports agent health, confidence decay, prompt change rate

test_tools.py

Used in sandbox tests to simulate downstream consumption and stress tests

🖼️ UX & View Design (Modular Testing Interface)

We will build a dedicated UI page: pages/role_context_view.py

It will:

Display the contextualized role summary in plain language (via context_narrative.py)

Offer editing or confirming capabilities per field

Show inferred archetype and allow overrides

Include a chat-style message: “Here’s how we understand your role context — does this sound accurate?”

Support inline thumbs-up/down + free text correction

📊 Metrics to Track

Accuracy of archetype tagging based on downstream satisfaction

% of users who accept default context vs edit

Time taken for LLM to infer context

Confidence score trends over time

Role-type distribution health (detect over-representation of one type)

Prompt adjustment frequency (via self_learning)

🧩 Sandbox Testing Plan

We’ll build a test script in sandbox/role_context_test.py which will:

Load mocked data (resume, title, org size)

Call the agent and print outputs

Simulate payloads to Skill Delta, Use Case Miss, etc.

Log performance and confidence

🔐 Data Privacy & Compliance

Use remove_personally_identifiable_info() on all text fields before storing

Hash company names and titles

Only store structured outputs, not raw resume/LinkedIn

Consent message will be displayed (future SaaS)

✅ Summary

This Role Context Agent moves us from resume parsing to organizational intelligence — grounding every downstream recommendation in a richer understanding of what the user’s role actually means inside their company. It classifies scope, decision dynamics, and upskilling potential — and sets a powerful foundation for our personalization layer.

