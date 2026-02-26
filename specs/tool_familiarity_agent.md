Tool Familiarity Agent — V2 Spec
Purposeful, Narrative-Driven Edition

🎯 1. Product Vision
Modern AI-driven careers demand fluency with tools, not just skills.
In an AI upskilling journey, tool familiarity is a proxy for adaptability, curiosity, and readiness.

The Tool Familiarity Agent serves as the platform’s window into a user's real-world workflows:

What tools do they rely on?

How comfortable are they with modern AI-enhanced tools?

Where are the gaps that could limit their growth?

Rather than passively accepting what's on a resume, this agent proactively investigates:
it infers, guides, and validates a user's tooling comfort — across categories relevant to their role, environment, and aspirations.

🛤️ 2. Why This Matters
Without understanding tooling behavior:

Learning paths risk suggesting impractical or irrelevant material.

Skill delta analysis becomes blind to workflow-based gaps.

AI maturity scoring becomes shallow or misleading.

The Tool Familiarity Agent anchors the system in the user’s true working reality — enabling smarter, sharper, hyper-personalized coaching.

🔥 3. Core Responsibilities

Responsibility	Purpose
Aggregate	Gather explicit and implicit tool signals from structured inputs.
Infer	Based on role norms and context, predict likely tool usage clusters.
Contextualize	Adjust suggestions based on domain, tech comfort, org environment.
Validate	Actively guide the user through confirming, editing, or rejecting inferences.
Structure	Produce clean, tagged outputs ready for downstream consumption.
Learn	Capture user feedback to continuously refine future prompts and outputs.
📥 4. Inputs
Not just what the user said — but what their world suggests.


Source	Fields Consumed	Purpose
global_agent_memory	Aggregated structured signals	Canonical ingestion point
persona_context.py	domain, tech_comfort, ai_openness	Adjust inference prompts
role_context_agent	role_family, task_clusters, org_shape, ops_bias	Role-driven tool cluster norms
All inputs are pre-evaluated for clarity and quality using input_evaluation.py.

📤 5. Outputs
Each output isn't just "data" — it’s a coaching insight.
Outputs reveal how well-equipped the user is for the future of their work.


Output Field	Purpose
tools_confirmed	What the user directly acknowledges they know/use
tools_by_function	A mental map of their workflow tools
ai_tools_detected	Their proximity to AI-native environments
tool_depth_estimate	Surface-level vs. expert usage signals
tool_maturity_score	A single north-star metric of tool-readiness
tool_practitioner_profile	High-level categorization for coaching ("Minimalist", "Power User")
functional_gap_areas	Blind spots in workflows (e.g., no analytics tooling)
tool_inference_notes	Confidence markers and cautions
analytics_ready_events	Event hooks for future tool adoption insights
🛠️ 6. System Design & Implementation Plan
Narrative thread:
We respect the user's past, infer their present, and open doors to their future.

6.1 Data Gathering Layer
Build a single coherent user context first, before any assumptions.

Pull from global_agent_memory.

Enrich with persona_context.

Validate completeness.

6.2 Inference & Augmentation Layer
We propose, but let the user decide.

Prompt LLM with full enriched context.

Cluster tools by function (e.g., Roadmapping, Research, Delivery).

Propose common tools per function.

Tag AI-native tools separately.

Estimate surface/deep familiarity based on context signals.

6.3 User Interaction Layer
Turn assumptions into active conversation.

Present function clusters with suggested tools.

Ask: "Which of these tools have you used recently?"

Allow user to add tools (with LLM validation for realism).

Capture depth of usage: "Surface knowledge", "Daily user", "Expert".

Subtle guidance: Educate users softly if they enter non-tools (e.g., programming languages).

6.4 Feedback & Logging Layer
Every user correction is a gift to the system.

Capture thumbs up/down per cluster.

Capture manual edits, new tools.

Log feedback into feedback_utils.py.

Update learning signals into self_learning.py.

6.5 Output Structuring Layer
What we pass downstream must be clear, confident, and clean.

Structure final outputs with downstream_formatter.py.

Save structured memory into global_agent_memory.

🖥️ 7. UI (tool_familiarity_view.py)
Narrative:
Make tool selection feel empowering — not tedious.


Feature	Design Rationale
Show function categories (e.g., Roadmapping, Prototyping)	Mental models are faster than free-form recall
Suggest tools under each	Educates while inviting participation
Checkboxes for tool familiarity	Low-friction confirmation
Add your own tool	Foster ownership
Capture depth estimate	Shows sophistication
Subtle nudges if input is off (e.g., not a tool)	Preserve user dignity
Use st.session_state to pass structured selections downstream.

📊 8. Tool Analytics Vision
Every interaction becomes future intelligence:

Which tools are sticky?

Which functions have the most gaps?

How does AI tool adoption change over time?

Our first priority is coaching;
Our second priority is learning from patterns.

✅ Output event hooks for future analytics database (optional in V2).

⚙️ 9. Key Utilities
agent_logger.py

global_agent_memory.py

persona_context.py

input_evaluation.py

feedback_utils.py

self_learning.py

downstream_formatter.py

timing_utils.py

New: tool_input_validator.py (validate user-entered tools)

🌟 Final Why
In a world flooded with AI tools, those who navigate workflows deftly will lead.
This agent ensures we are building leaders, not just learners.

This isn't just about what tools someone has used —
It’s about how they think about work, adopt innovations, and future-proof themselves.