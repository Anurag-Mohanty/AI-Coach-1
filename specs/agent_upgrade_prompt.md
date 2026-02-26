ou are helping me upgrade a set of intelligent agents from V1 to V2. Each agent serves a defined, modular role in a self-evolving AI coaching platform, with clear upstream/downstream dependencies and responsibilities — similar to how humans operate in high-functioning teams.

These agents use structured input, LLM-powered reasoning, shared context, and self-learning mechanisms to deliver personalized, intelligent coaching recommendations.

🧠 Project Architecture
You have access to:

Full V1 agent code

The system repo, architecture spec, prompt builder, UI modules

Shared utilities (agent_core/)

Modular frontends in pages/

Centralized prompt management (prompt_builder.py)

Shared persona context, memory, and feedback loops

Each agent upgrade is done in its own thread, following the 10-part framework below. Every upgrade must include not just logic and UI, but also a clearly defined prompting identity and a reusable, testable prompt template.

✅ AGENT V2 UPGRADE FRAMEWORK
1. ✅ Goal Clarity
What is this agent uniquely responsible for?

Define the agent’s distinct mission within the system.
Example: “Diagnoses skill gaps by comparing current vs. aspirational archetype, and generates a structured skill delta vector.”

2. ✅ Input Quality & Context
What structured inputs are required, where do they come from, and how are they used?

Accept inputs from other agents + global_agent_memory

Use input_evaluation.py to validate completeness

Clearly describe each field:

Source agent

Purpose

Example

Optionality

3. ✅ Output Usefulness
What does this agent produce, and how should it be formatted?

Return LLM-parseable JSON with clean field names

Use downstream_formatter.py to shape for consumers

Include:

confidence

source

explanation

LLM_reasoning_path (when needed)

4. ✅ Downstream Compatibility
Which agents consume this output, and what do they expect?

Identify and list each consumer

Ensure outputs are shaped and named accordingly

Support agents like:
learning_path_agent, experiment_agent, tool_recommender, meta_agent, etc.

5. ✅ Feedback & Learning
How does the agent learn and improve over time?

Capture thumbs_up/down, corrections with feedback_utils.py

Use self_learning.py to:

Log learning signals

Trigger prompt template upgrades

Auto-adjust prompts on repeated rejection

Cache reusable prompt improvements for similar subtasks

6. ✅ User Interaction Awareness
How should the user contribute to, correct, or refine this output?

Show top 3–5 structured options

Accept fallback freeform input (validated)

Store selections via helpers like store_user_selected_delta()

Track edits in session_state and global_agent_memory

7. ✅ Success Metrics
How do we evaluate this agent’s performance?

📈 Field usage downstream

👍👎 Feedback ratio

🎯 Correction frequency

💡 Prompt reuse from learning

🧠 Confidence/explanation match with user expectations

8. ✅ Validation of Freeform Input
What if the user writes their own skill gap or insight?

Validate via LLM

Add source: user_input, valid: True, confidence: float

Optionally store for future training or prompt improvements

Route through:
process_custom_input_field()

9. ✅ Utilities & Logging
Which shared tools must be used?

agent_logger.py — all activity + trace logs

global_agent_memory.py — persistent context

feedback_utils.py — structured feedback loop

self_learning.py — prompt adaptation

input_evaluation.py — input coverage and quality check

trust_explainability.py — reasoning trace

persona_context.py — tone, style, and maturity

downstream_formatter.py — output shape enforcement

timing_utils.py — performance monitoring

10. ✅ UI Separation
What should the frontend look like?

Modular page: pages/{agent_name}_view.py

Supports:

Output preview

Structured + freeform input

Inline feedback

State sync via st.session_state

Enable downstream visibility: “What will other agents see from here?”

📣 CENTRAL PROMPTING STRATEGY (Required in V2)
All agents must define their LLM identity using:

➤ prompt_builder.py
The agent must register:

agent_role: A narrative summary of what this agent is meant to do
e.g., “You are a diagnostic agent that compares user skills to target role expectations, and generates a structured skill delta vector with narrative insight.”

agent_tasks: The subtasks or behaviors it needs to fulfill
e.g., ["Identify missing skills", "Evaluate underused strengths", "Score AI readiness"]

Optional: task_level_templates: if specific subtasks need separate logic

🧱 Prompt Template Design (Required as part of upgrade)
During the upgrade, you must:

Design the LLM prompt template for this agent (if one does not exist)

Include:

Context injection block ({{structured_input}})

Example output JSON ({{example_output}})

Persona tone ({{persona_context}})

Store it in prompt_templates/agent_name_template.txt

Optionally register with self_learning.py for runtime reuse and updates

📘 The prompt should be reusable, fallback-tolerant, and context-rich.

🔁 Prompt Evolution & Reuse
All prompt failures or negative feedback should be routed to:

auto_adjust_prompt_if_downvoted()

suggest_prompt_improvements()

Improved templates should be cached using:

cache_and_reuse(subtask, improved_prompt)

Agents may inherit successful prompt strategies from others via prompt_registry.yaml

🛠️ FINAL OUTPUTS (Once Framework Is Done)
You will generate:

🧭 Product Spec (Markdown)

Mission, inputs/outputs, use cases, prompt logic

Implementation plan

🧠 Agent Logic

agents/{agent_name}/{agent_name}_agent.py

Uses full utilities, prompt builder, prompt cache

🧩 Modular Helpers

For user input validation, prompt evolution, custom field ingestion

🖼️ UI View

pages/{agent_name}_view.py with structured interface

🧾 Prompt Template

prompt_templates/{agent_name}_template.txt

Must include context injection, example output, instructions, tone