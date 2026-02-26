DOMAIN JUMP AGENT — PRODUCT SPEC (V2)
✅ 1. Mission / Goal Clarity
🎯 Mission:
The Domain Jump Agent determines how transferable a user’s skills, mindsets, and experiences are from their current domain to a new target domain or industry. It provides bridge-level insight that enables the coaching system to correctly reposition the user's capabilities, identify critical knowledge or mindset gaps, and curate the most relevant learning paths or experimental tasks.

Why this matters:
Without this agent, domain shifts are treated as linear promotions or flat comparisons — leading to either mismatched learning paths, irrelevant tool suggestions, or failure to recognize useful transferable experience. This agent ensures users aren’t forced to start from scratch when they switch domains, and also prevents false positives by flagging real gaps that need to be bridged.

✅ 2. Input Quality & Context
📥 Inputs Required:
Field	Source	Purpose
current_domain	Resume Agent	Anchor the user’s current industry or function
target_domain	Aspiration Agent	Defines the intended future domain
tools_used, project_keywords, impact_scale	Resume Agent	Help infer functional capabilities
skills_from_resume, skills_from_linkedin	Skill Assessment Agent	Raw skill inventory
use_cases_by_domain, skills_by_use_case	Use Case Generator Agent	Define expectations for the target domain
persona_context	Persona Context Module	Adjust tone and seniority language

All inputs validated through input_evaluation.py to ensure coverage and completeness.

Why this matters:
We can’t rely on a resume alone to judge domain readiness. Context from aspirational goals, extracted skills, and domain-specific expectations are essential to make a cross-functional, intelligent evaluation.

✅ 3. Output Usefulness
📤 Primary Output:
json
Copy
Edit
{
  "transferable_skills": [...],                 // Skills that will carry over
  "domain_specific_gaps": [...],                // Tools, workflows, or terminology that must be learned
  "bridge_insight_summary": "...",              // Narrative explaining the overlap and transition strategy
  "suggested_mindset_shifts": [...]             // Cognitive or cultural shifts expected in the new domain
}
Why this matters:
These outputs are machine-usable by downstream agents and narrative-ready for human interpretability. They feed learning path selection, experiment generation, and skill delta detection without bloated scoring or hard-to-validate metrics.

✅ 4. Downstream Compatibility
🔁 Feeds Into:
Agent	Field Consumed	Outcome
Skill Delta Agent	transferable_skills, domain_specific_gaps	Compare against expected target skills
Learning Path Agent	domain_specific_gaps, suggested_mindset_shifts	Curate bridging modules
Experiment Agent	bridge_insight_summary	Generate test scenarios for domain exposure
Tool Recommender	domain_specific_gaps	Suggest target domain tools
Meta Agent	Read-only for difficulty benchmarking	Map patterns across users
Gap Analysis Agent	All	Determine whether domain jump contributes to gap severity

Why this matters:
The outputs are not isolated — they activate critical downstream workflows that shape the user’s entire transition journey.

✅ 5. Feedback & Learning
📚 Feedback Loop:
No direct UI thumbs-up/down

Indirect feedback routed through Skill Delta Agent (e.g., if the transferable skills or gaps aren’t useful, the delta will reject or down-rank them)

Tracked via self_learning.py and logged using feedback_utils.py

Why this matters:
This agent doesn’t face the user — but the system still learns if the outputs are respected by downstream agents. If not, the prompt and matching logic must adapt.

✅ 6. User Interaction
No standalone UI for this agent

Outputs surfaced only in the Gap Summary view

For dev testing only: pages/domain_jump_view.py may exist

Why this matters:
This is a system-level utility, not a user-facing coach. Its job is to equip the other agents, not talk to the user.

✅ 7. Success Metrics
Metric	Purpose
# of domain-related skills identified	Are we actually finding reusable strengths?
% of these used by Skill Delta	Are they accepted downstream?
# of domain-specific gaps fed to Learning Path	Are gaps clear and actionable?
% of user profiles flagged as low-transferability	Are we flagging risky jumps early?

Why this matters:
The goal isn’t engagement — it’s enabling better learning path design, risk detection, and skill targeting.

✅ 8. Prompting Strategy
Will be registered via prompt_builder.py with:

agent_role:
"You are a cross-domain diagnostic agent that evaluates the transferability of a user’s skills and experiences from their current domain to a target domain, identifies reusable strengths, flags domain-specific gaps, and articulates bridge strategies.”

agent_tasks:

python
Copy
Edit
[
  "Identify transferable skills based on resume and context",
  "Detect domain-specific gaps using skill expectations",
  "Summarize strategic insight for making the leap",
  "Suggest mindset shifts required to adapt"
]
Prompt template file: prompt_templates/domain_jump_template.txt
Will include:

{{structured_input}}

{{persona_context}}

{{example_output}}

Fallback/default rules

Why this matters:
Without a well-shaped LLM prompt, this agent will either:

Fail to make analogical leaps

Over- or under-state gaps

Ignore nuance between “function” and “domain”

✅ 9. Utilities
This agent will use:

agent_logger.py

input_evaluation.py

self_learning.py

global_agent_memory.py

feedback_utils.py

trust_explainability.py

downstream_formatter.py

persona_context.py

Why this matters:
We ensure traceability, quality enforcement, learning, and formatting — consistent with the broader architecture.

✅ 10. UI & Test Harness
❌ No production UI

✅ Optional: pages/domain_jump_view.py for internal testing

Outputs integrated into Gap Summary Panel (fed by Gap Analysis Agent)