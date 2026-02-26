Aspiration Agent V2 – Final Spec with Strategic Narrative
🧠 Narrative: Why This Agent Matters
The Aspiration Agent is the starting point for ambition. While resumes tell us where someone’s been, and skill scores show how they perform today, aspiration defines the direction. But people don’t always articulate their future clearly — sometimes they feel FOMO, uncertainty, or a vague need to grow. Others dream big, but without realism. Some aren’t sure what’s possible.

That’s where this agent comes in.

The challenge:
How do we reliably extract, validate, and structure a future trajectory for each user — even if they don’t know how to describe it themselves?

The opportunity:
By understanding where someone could or wants to go, we unlock:

The delta between now and that goal (for gap analysis)

The direction for learning and experimentation

The context for whether tools and content are relevant

The persona archetype that ties users to others like them

This agent becomes the platform’s north star compass. Every other agent aligns to this.

🎯 Functional Vision
The Aspiration Agent V2 will:

Detect latent goals, even if the user is vague

Suggest realistic trajectories grounded in resume + role context

Validate user-selected goals and refine them into structured fields

Power downstream agents by outputting consistent, tagged aspiration metadata

Learn and evolve through structured feedback from users and system signals

📥 Input Sources

Source	Fields	Purpose
User Input	Freeform + goal checklist	Initial motivation capture
Resume Agent	Title, domain, tools, leadership	Understand current scope and realism anchor
LinkedIn Agent	Posts, endorsements, roles	Sense recent growth vectors
Role Detail Agent	Tasks, impact scale	Cross-check actual work vs ambition
Persona Context	Past goals, context clusters	Tailor aspirations based on profile
Cultural Agent	Environment fit	Optional filters (e.g., prefers innovation or remote)
📤 Output Fields
json
Copy
Edit
{
  "target_role_archetype": "IC4 - Senior Product Manager",
  "aspiration_category": "Grow in domain + begin leadership",
  "role_delta_summary": "Needs AI upskilling and team coordination experience",
  "domain_shift_signal": false,
  "risk_of_misalignment": "No leadership signals in resume",
  "aspiration_cluster": "AI-focused mid-career PMs",
  "realism_score": 0.87,
  "reflective_prompt": "Would you consider switching to platform product leadership?",
  "user_confirmed": true
}
🔁 Downstream Consumers (Updated + Clarified)

Agent	What it uses	Why it needs it
Skill Delta Agent	target_role_archetype	Calculates the gap between now and the aspirational benchmark
Role Ladder Agent	target_role_archetype + aspiration_category	Places user on IC or people management track (not just IC leveling)
Domain Jump Agent	domain_shift_signal	Detects cross-industry jumps, flags support needs
Use Case Generator Agent	aspiration_category + target_role_archetype	Generates likely scenarios the user should be solving
Use Case Miss Agent	aspiration_cluster + domain_shift_signal	Detects gaps in current behavior given future goals
Tool Recommender Agent	target_role_archetype	Suggests tools commonly used in that target role
Learning Path Agent	aspiration_category + realism_score	Builds content paths from the user’s current state to their future self
Experiment Agent	aspiration_category + motivation_summary	Recommends projects aligned to the goal (e.g., leadership → cross-team project)
Meta Agent	aspiration_cluster	Clusters users by shared aspiration type and shows peer pathways
Resume Agent (Feedback Loop)	risk_of_misalignment	Suggests edits to better reflect the user's future ambition
🔐 Data Handling & Utilities

Utility	Role
global_agent_memory.py	Store all outputs with user/session for use elsewhere
persona_context.py	Update long-term trajectory, cluster, aspiration
agent_logger.py	Log inputs, decisions, runtime
input_evaluation.py	Detect vague or unrealistic goals
feedback_utils.py	Track user corrections and thumbs
self_learning.py	Auto-adjust prompt if output is consistently off
trust_explainability.py	Show why a suggestion was made
timing_utils.py	Time each operation for UI feedback and debug
downstream_formatter.py	Normalize all outputs and flag key fields
📐 UI Design (Aspirational View – Optional)
Summary of current context

“Why are you here?” – Choose 1–3 motivations (FOMO, reskilling, career leap, etc.)

Suggested career paths (based on profile) – Select 1–2 or write your own

See “trajectory preview” – what’s missing, what’s needed

Editable fields with explainability tags

Confirmation prompt: “Is this the direction you want to go?”

📊 Success Criteria

Metric	What it means
User Acceptance Rate	% of users who accept suggested or structured aspiration
Downstream Usage Rate	% of agents successfully using this agent’s output
Feedback Correction Rate	% of outputs that required editing (target: low)
Cluster Confidence Match	Alignment of user to high-confidence peer cluster
Gap Delta Coverage	% of output fields used in gap or role modeling logic
🛠️ Implementation Plan
Phase 1: Core Foundation
Finalize prompt logic with fuzzy input handling

Use resume + role + linkedin to ground “realistic next steps”

Create structured JSON output and write to global memory

Tag for downstream use

Phase 2: Suggestion + Reflection
Use LLM to generate realistic goals based on current profile

Add reflective_prompt and multiple goal choices

Store and update persona context

Phase 3: Feedback + UI Integration
Build feedback loop (thumbs, corrections)

Log data via feedback_utils, self_learning

Optional: UI view (aspiration_view.py) for review, edit, preview