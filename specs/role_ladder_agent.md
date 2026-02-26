ROLE LADDER AGENT — V2 SPEC (REWRITTEN W/ NARRATIVE)
🧭 Agent Purpose (Narrative + Role)
The Role Ladder Agent anchors a user within a normalized, aspiration-aware career progression ladder, based on the scope, signals, and trajectory inferred from their actual work experience — not just titles.

But this isn’t about vanity metrics or titles. This agent provides a ground truth compass that downstream agents can use to decide:

What skill gaps are realistic

What type of learning paths are most appropriate

What experiments make sense at this point in the user’s growth

How far the user is from a promotion or domain jump

It is never shown to the user directly. Instead, it powers the Gap Analysis Agent’s backend engine — which eventually summarizes the entire delta into a user-facing diagnostic.

This agent is also tasked with ladder equivalency, if the user intends to shift into a new field (from IC PM → IC Designer, or IC to Manager, or Startup → Enterprise). This is resolved silently in the background using aspiration context + org type normalization.

1. 🎯 Goal Clarity
Place the user within a normalized, cross-org, cross-domain ladder structure — aligned with where they are, not what their resume says — so downstream agents can assess readiness, growth, and gaps without being biased by inflated titles or ambiguous scope.

This supports the overall system goal of personalized, realistic, and high-utility recommendations by resolving the ambiguity of current-level positioning.

2. 📥 Inputs (Structured from Global Agent Memory)
No agent should query raw sources. This agent retrieves structured, clean memory inputs previously stored via other agents.


Input Source (via global_agent_memory)	Key Fields Used	Purpose
resume_agent	job_title, team_size, impact_scale, domain, leadership_signals	Actual scope of user’s work
linkedin_agent	career_trajectory, title_consistency, endorsement_signals	Trajectory and external validation
role_context_agent	org_type, org_size, cross_functional_exposure	Normalize the meaning of the job title
role_detail_agent	task_clusters, effort_distribution, ai_depth	What they actually do day to day
aspiration_agent	target_archetype, switching_domains, desired_ladder_path	To adjust mapping in case of field switch
The agent calls get_context() and merge_contexts() from global_agent_memory.py to build its full input state.

3. 📤 Outputs (Stored in Global Agent Memory)
These outputs are not shown to the user, but get written back to memory for use in:

Gap Analysis Agent (primary consumer)

Skill Delta Agent (benchmark setting)

Learning Path Agent (complexity calibration)

Experiment Agent (growth opportunity design)


Field	Description	Use
inferred_ladder_level	Normalized current level (e.g., IC3, IC5, M1)	Skill Delta + Experiment Agent
next_logical_level	What they should be preparing for (e.g., IC4 → IC5)	Gap Analysis
seniority_score	Composite score (0–100) based on depth, breadth, maturity	Learning Path Agent
progression_velocity	“Stalled”, “Moderate”, or “Accelerated”	Experiment Agent
ladder_alignment_flag	Whether aspiration matches current track	Gap + Meta Agent
normalization_explanation	Notes on org-title conversion, e.g., “VP in banking org = IC3 in product”	Meta Agent + Explainability
management_signal	Binary inference about whether user is on a manager path	Used for manager-specific suggestions
All outputs are tagged using downstream_formatter.tag_downstream_fields() and stored via:

python
Copy
Edit
global_agent_memory.store_memory(
    agent_name="role_ladder_agent",
    user_id=user_id,
    session_id=session_id,
    subtask_id="ladder_inference",
    function="inference_and_mapping",
    input_fields=input_context,
    output_fields=tagged_output
)
4. 🧩 Relevance to Platform Goals
This agent directly supports:

✅ Learning Path Agent → By tailoring cognitive load, abstraction, and skill modules

✅ Skill Delta Agent → To compare current vs. target skill set

✅ Experiment Agent → To suggest stretch tasks (e.g., mentor, lead initiative)

✅ Gap Analysis Agent → Core element for understanding readiness

✅ Meta Agent → For comparing peer growth

This enables diagnostic intelligence, not cosmetic labeling.

5. 🧠 Agent Behavior & Architecture
🔧 Main Function:
python
Copy
Edit
def infer_ladder_position(context):
    # Pull in merged memory
    # Normalize job titles with org_type
    # Resolve ladder level via LLM
    # Return structured tagged output
🔧 LLM Prompt Includes:
Org-type context (startup, bank, consultancy, FAANG, etc.)

Resume and task details

Aspiration adjustments

Time-based movement patterns

Uses model-specific prompt templates via:
prompt_builder.build_prompt('ladder_inference', context)

🔧 Logging:
agent_logger.log_agent_run()

timing_utils.track_time()

trust_explainability.generate_why_this_output_summary() for audit

6. 📊 Feedback Loop
We do NOT expose this agent directly for user input.

Instead:

All agent outputs are evaluated by the Gap Analysis Agent

If the summary generated is flagged as “off” by the user, that triggers feedback review across subagents like this one

If needed, self_learning.auto_adjust_prompt_if_downvoted() is called

7. 🧱 Utilities Used

Utility	Role
global_agent_memory	Get merged context, store outputs
agent_logger	Track success/failures
downstream_formatter	Tag outputs for reuse
trust_explainability	Add “why we inferred IC3 instead of VP”
timing_utils	Track time spent per inference
feedback_utils	Log and store corrections (if triggered from gap agent)
8. ⛓️ No User Interaction
✅ Everything here is backend-only
✅ No Streamlit UI for this agent
✅ Outputs only appear in Gap Analysis Agent’s final summary
✅ All correction, if any, is centralized at the Gap Summary level

🧪 Testing Strategy
Sandbox tests simulate various resume + org-type inputs to test normalization

Unit test: “Founder at 4-person startup” → IC3

Unit test: “VP at banking firm” → IC2–3

Domain switch test: Product IC to Design IC → Adjusts via aspiration archetype

✅ Final Deliverables After Approval
role_ladder_agent.py — clean, modular, no prompt inline

ladder_prompt_template.txt — reusable prompt for LLM

helper_normalization.py — shared function for VP/Founder normalization

NO UI VIEW — output is stored silently in memory

Tests: sandbox/test_role_ladder.py