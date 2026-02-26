## 1. 🎯 Purpose

The **Prompt Builder** is a foundational utility that enables intelligent agents — and eventually human users — to generate world-class prompts for interacting with large language models (LLMs). Rather than hardcoding prompt templates within each agent, this utility allows agents to **declare their intent** and receive a prompt that is:

- Grounded in available context
- Tuned to the user’s style, goals, and tone
- Structured for predictable and useful responses
- Adaptable to feedback
- Cached for performance
- Ready for internal use or external access

The Prompt Builder replaces every instance of `prompt = f"""..."""` scattered across agents with a single **reusable, testable, and improvable engine**.

---

## 2. 💡 Strategic Rationale

As your system scales across agents (Ladder, Learning Path, Experiment, etc.), each agent needs to prompt an LLM differently — but in a **principled, consistent way**. Right now:

- Many agents have **redundant or conflicting prompt logic**
- Prompt quality is **not centrally managed or evaluated**
- There's **no easy way to debug or revise** prompt strategy
- You **can’t reuse** high-performing prompts outside the agent context

With the Prompt Builder, you move toward **declarative agents**:

> “Here’s what I want to do — give me the best prompt possible.”
> 

---

## 3. 🧠 How It Works (Agent Interaction Model)

Imagine you're the Role Ladder Agent. Instead of building the prompt yourself, you say:

```python
python
CopyEdit
# Step 1: Ask what information is needed
reqs = request_prompt_requirements(task='ladder_inference')

# Step 2: Provide whatever context you have
prompt_pkg = build_prompt_from_context(
    task="ladder_inference",
    agent_role="You are a senior career strategist.",
    task_instruction="Place the user on a normalized IC/manager ladder.",
    user_context=persona_context,
    memory_context=session_context,
    output_format="JSON with inferred_ladder_level, next_logical_level, ...",
    examples=[...],  # optional
    considerations=["Avoid resume inflation", "Use company type as signal"]
)

# Step 3: Run the LLM
llm_response = call_llm_model(prompt_pkg['prompt'])

```

If required fields were missing, `prompt_pkg["missing_fields"]` will tell the agent what it still needs. This makes **every agent self-aware and flexible**, even when upstream data is partial.

---

## 4. 🔧 Core Functions

### `request_prompt_requirements(task: str) -> dict`

Returns a dictionary of required/optional fields for that task.

```json
json
CopyEdit
{
  "required_fields": ["current_title", "company_type", "years_experience"],
  "optional_fields": ["team_size", "persona_tone"],
  "examples_supported": true,
  "output_format_required": true}

```

---

### `build_prompt_from_context(...) -> dict`

```python
python
CopyEdit
def build_prompt_from_context(
    task: str,
    agent_role: str,
    task_instruction: str,
    user_context: dict = None,
    memory_context: dict = None,
    examples: list = None,
    considerations: list = None,
    output_format: str = None
) -> dict

```

Returns:

```json
json
CopyEdit
{
  "prompt": "You are a career strategist...",
  "missing_fields": ["org_type"],
  "used_cache": false}

```

---

## 5. 📚 Example: Role Ladder Agent

Let’s walk through how the **Role Ladder Agent** uses this in practice.

### Agent → Prompt Builder: Intent-First Dialogue

Instead of passing all inputs up front, the **Role Ladder Agent starts with intent**:

```python
python
CopyEdit
from agent_core.prompt_builder import request_prompt_requirements

# Step 1: I need a prompt for this task
requirements = request_prompt_requirements(task="ladder_inference")

```

---

### 🔁 Prompt Builder → Agent: “Here’s what I need”

```json
json
CopyEdit
{
  "task": "ladder_inference",
  "required_fields": ["current_title", "company_type", "years_experience", "target_role_archetype"],
  "optional_fields": ["persona_tone", "team_size", "resume_highlights"],
  "examples_supported": true,
  "output_format_required": true}

```

This lets the Role Ladder Agent **respond intelligently**:

### Agent Intent Declaration

**Role Ladder Agent** calls the prompt builder like this:

```python
python
CopyEdit
from agent_core.prompt_builder import build_prompt_from_context

prompt_package = build_prompt_from_context(
    task="ladder_inference",
    agent_role="You are a senior career strategist with expertise in org-level leveling and promotion readiness.",
    task_instruction="Infer the user’s true position on a normalized IC/managerial ladder and the next logical step.",
    user_context=user_context,
    memory_context=memory_context,
    examples=past_prompt_examples,
    considerations=["Avoid over-indexing on inflated titles", "Favor realism over optimism"],
    output_format="""
    JSON with:
    - inferred_ladder_level
    - next_logical_level
    - progression_velocity
    - ladder_alignment_flag
    - normalization_explanation
    - management_signal
    """
)

```

---

### Prompt Builder Response

```json
json
CopyEdit
{
  "prompt": "You are a senior career strategist specializing in IC vs Manager ladder leveling across startups and tech companies...",
  "missing_fields": ["org_type", "domain"],
  "used_cache": false}

```

If `missing_fields` is not empty, the Role Ladder Agent can:

- Trigger a lookup via `input_evaluation.detect_missing_context()`
- Log an alert
- Ask the user for clarification (if UI-exposed)

---

### Agent Response Handling

**If missing fields**:

```python
python
CopyEdit
if prompt_package["missing_fields"]:
    log_agent_event("role_ladder_agent", f"Missing context: {prompt_package['missing_fields']}")
    # Later: trigger memory retrieval or fallback handling

```

**If prompt is valid**:

```python
python
CopyEdit
llm_response = call_llm_model(prompt_package["prompt"])

```

---

### Optional: Auto-Improvement via Self Learning

If the **output from the LLM** based on this prompt is later downvoted:

- `feedback_utils` logs thumbs-down
- `self_learning.track_thumbs_up_rate("role_ladder_agent", "inferred_ladder_level")`
- `prompt_builder` learns to inject:

    > “Avoid assigning IC2 to users with 3+ years unless scope is explicitly narrow.”
    > 

---

## 📍 Implication: Replace This...

Agents like Role Ladder and Role Detail currently have hardcoded blocks like:

```python
python
CopyEdit
prompt = f\"\"\"
You are a strategist. The user is a {title} at {company}. Analyze their role and return:
- inferred_level
- next_level
...etc.
\"\"\"

```

...with a modular request:

```python
python
CopyEdit
prompt_package = build_prompt_from_context(...)

```

This **centralizes all prompting** and enables prompt re-use across:

- Resume rewrite
- Career advice
- Skill path planning
- Tool recommendations

---

## ✅ System Design Benefit

- ✳️ Agents become declarative: *“Here’s what I want to do”*
- ✅ Prompt Builder becomes intelligent: *“Here’s what I need to help you do it well”*
- 🔄 Feedback loops can fine-tune future prompts without touching the agent code
- 🔌 Easy to expose as a **URL-based standalone prompt API**

```python
python
CopyEdit
provided_context = collect_context(fields=requirements["required_fields"])
prompt = build_prompt_from_context(
    task="ladder_inference",
    agent_role="...",
    task_instruction="...",
    user_context=user_context,
    memory_context=provided_context,
    output_format="..."
)

```

---

## 🤖 Prompt Builder as a Thinking Partner

| Phase | Behavior |
| --- | --- |
| 1️⃣ Agent declares a task | “I want to map a user’s role to a ladder level.” |
| 2️⃣ Prompt Builder replies | “I can help. I’ll need X, Y, and Z to do it well.” |
| 3️⃣ Agent responds with what it has | If something’s missing, the agent logs it, fetches it, or defaults |
| 4️⃣ Prompt Builder returns a prompt | Optimized, contextual, and complete |
| 5️⃣ Later: feedback refines prompts | “Next time, avoid recommending IC2 if user is a VP in a startup” |

---

## 🔧 Updated Functions in Prompt Builder

```python
python
CopyEdit
def request_prompt_requirements(task: str) -> dict:
    # Returns what is required for optimal prompt generation

def build_prompt_from_context(...):  # Full builder as discussed

```

### Step A: Intent

It declares:

> “I want to infer the user's ladder level.”
> 

### Step B: What’s Needed

The Prompt Builder replies:

```json
json
CopyEdit
{
  "required_fields": ["current_title", "company_type", "years_experience", "target_role_archetype"]
}

```

The agent provides what it has. Maybe it's missing `org_type`.

### Step C: Prompt Builder Output

```json
json
CopyEdit
{
  "prompt": "You are a senior career strategist... Return JSON with: inferred_ladder_level, progression_velocity, ...",
  "missing_fields": ["org_type"]
}

```

### Step D: Agent Executes Prompt

```python
python
CopyEdit
if prompt_pkg["missing_fields"]:
    log_agent_event("role_ladder", f"Missing: {prompt_pkg['missing_fields']}")

```

---

## 6. ✨ Prompt Engineering Best Practices Used

| Principle | How it's embedded |
| --- | --- |
| ✅ Role grounding | Agent declares identity (`agent_role`) |
| ✅ Instruction clarity | Explicit task (`task_instruction`) |
| ✅ Context personalization | Context is merged from persona and memory |
| ✅ Format control | Agents define output schemas |
| ✅ Reflection-first prompting | “Explain before outputting” added if needed |
| ✅ Hallucination mitigation | Nudges like “don’t guess” or “return null” included |
| ✅ Few-shot learning | Optional `examples` field supports this |
| ✅ Self-learning refinement | System learns from downvotes and adapts prompt suggestions over time |

---

## 7. 🔁 Learning Loop

- If an agent’s prompt result leads to bad output…
- ...the agent logs feedback via `feedback_utils`
- ...this is picked up by `self_learning` module
- ...the Prompt Builder incorporates it as a `consideration`:

    > “Avoid suggesting IC2 for users with VP titles.”
    > 

This turns every failed prompt into training data for future improvement.

---

## 8. 🌐 External Exposure

You can expose this as a service.

### REST API

```
bash
CopyEdit
POST /prompt
{
  "task": "resume_booster",
  "user_context": { ... },
  "memory_context": { ... },
  "task_instruction": "...",
  ...
}

```

Returns:

```json
json
CopyEdit
{
  "prompt": "...",
  "missing_fields": [...],
  "used_cache": false}

```

### Optional: Web UI

Use Streamlit or Flask to let users:

- Pick a task
- Upload or enter profile info
- Receive a high-quality prompt

---

## 9. 🚀 Future Enhancements

| Feature | Description |
| --- | --- |
| 🔄 Prompt revision engine | Suggest better prompts from failures |
| 🧪 A/B testing of prompts | Compare effectiveness over time |
| 📊 Prompt leaderboard | See which agents consistently produce high-accuracy results |
| 📥 Example retriever | Pulls best prompts as examples |
| 📦 Prompt snippets | Modular reusable clauses (“Avoid hallucination”, “Return JSON only”) |