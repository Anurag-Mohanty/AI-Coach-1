import os
import json
from typing import Dict, List, Tuple

import openai

from agent_core.agent_logger import log_agent_run, log_error
from agent_core.input_evaluation import validate_inputs
from agent_core.feedback_utils import capture_user_feedback
from agent_core.global_agent_memory import store_memory, retrieve_memory
from agent_core.persona_context import get_user_context
from agent_core.downstream_formatter import format_for_agent
from agent_core.timing_utils import timed_function
from agent_core.trust_explainability import generate_why_this_output_summary

from .tool_input_validator import validate_tool_input

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@timed_function("tool_familiarity_agent")
def infer_tool_familiarity(user_id: str, session_id: str) -> Dict:
    """
    Main Tool Familiarity Agent Logic
    """
    try:
        # 1. Retrieve full context from global memory
        context = retrieve_memory("global", user_id, session_id, subtask_id=None)
        persona = get_user_context(user_id)

        # 2. Validate critical inputs
        validate_inputs(context)

        # 3. Build LLM prompt
        enriched_prompt = build_prompt(context, persona)

        # 4. Call LLM to infer tool clusters
        inferred_tools = call_llm_for_tools(enriched_prompt)

        # 5. Format output
        structured_output = format_outputs(inferred_tools, context, persona)

        # 6. Store output to memory
        store_memory("tool_familiarity_agent", user_id, session_id, "tool_inference", "infer_tool_familiarity", context, structured_output)

        # 7. Log agent run
        log_agent_run("tool_familiarity_agent", context, structured_output)

        return structured_output

    except Exception as e:
        log_error("tool_familiarity_agent", str(e))
        raise e


def build_prompt(context: dict, persona: dict) -> str:
    """
    Build enriched prompt with role, domain, tools, and persona tone
    """
    title = context.get("title", "Professional")
    domain = persona.get("domain", "General")
    tech_comfort = persona.get("tech_comfort", "Moderate")
    tools_used = context.get("tools_used", [])

    base_tools = ', '.join(tools_used) if tools_used else "None explicitly mentioned"

    # Extract dynamic task clusters
    task_clusters = context.get("task_clusters", [
        "General Productivity", "Project Management", "Collaboration", "Analytics"
    ])
    work_functions_list = "\n".join([f"   - {wf}" for wf in task_clusters])

    prompt = f"""
You are an AI Workflow Tool Analyst.
Your goal is to infer a user's familiarity with modern productivity and AI-enhanced tools based on their role, work environment, and self-described technical comfort.

Context:
- Role Title: {title}
- Domain: {domain}
- Tech Comfort Level: {tech_comfort}
- Explicit Tools Mentioned: [{base_tools}]

Tasks:
1. Propose tools grouped by these dynamically inferred work functions:
{work_functions_list}
2. Mark tools that are AI-native or AI-augmented.
3. Estimate usage depth for each tool:
   - "Surface" (Heard of it / seen it)
   - "Regular" (Uses it occasionally in workflows)
   - "Expert" (Uses it heavily or customizes it)
4. Score overall tool maturity by the percentage of AI-native tools vs traditional tools.

Return your answer strictly as a JSON dictionary like:
{{
  "tools_by_function": {{
    "WorkFunction1": ["Tool A", "Tool B"],
    "WorkFunction2": ["Tool C"]
  }},
  "ai_tools_detected": ["Tool A", "Tool C"],
  "initial_tool_depth_estimate": {{
    "Tool A": "surface",
    "Tool B": "regular",
    "Tool C": "expert"
  }}
}}
    """
    return prompt


def call_llm_for_tools(prompt: str) -> dict:
    """
    Calls OpenAI GPT to infer tools from prompt
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a tool analysis assistant. Return only a valid JSON object with exactly these keys: tools_by_function (dict mapping function names to tool name lists), ai_tools_detected (list of tool names), and initial_tool_depth_estimate (dict mapping tool names to depth strings)."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )
        raw_response = response.choices[0].message.content.strip()
        parsed = json.loads(raw_response)
        print("LLM Response:", parsed)  # Debug output
        return parsed
    except Exception as e:
        print(f"Error in LLM call: {str(e)}")
        return {
            "tools_by_function": {
                "Project Management": ["Jira", "Confluence"],
                "Data Analysis": ["Tableau"],
                "Design": ["Figma"]
            },
            "ai_tools_detected": ["Tableau", "Figma"],
            "initial_tool_depth_estimate": {
                "Jira": "expert",
                "Confluence": "regular",
                "Tableau": "regular",
                "Figma": "surface"
            }
        }


def format_outputs(inferred_tools: dict, context: dict, persona: dict) -> dict:
    """
    Post-process LLM response into final agent output format
    """
    # Extract from context
    tools_used = context.get("tools_used", [])

    # Get inferred data or use defaults
    tools_by_function = inferred_tools.get("tools_by_function", {})
    ai_tools_detected = inferred_tools.get("ai_tools_detected", [])
    initial_tool_depth_estimate = inferred_tools.get("initial_tool_depth_estimate", {})

    # Ensure we have valid data based on context
    if not tools_by_function or not any(tools_by_function.values()):
        # Use tools from context if available
        if tools_used:
            tools_by_function = {"Current Tools": tools_used}
            ai_tools_detected = [t for t in tools_used if t in ["Tableau", "Figma", "ChatGPT", "GitHub Copilot"]]
            initial_tool_depth_estimate = {t: "regular" for t in tools_used}
        else:
            # Fallback defaults
            tools_by_function = {
                "Project Management": ["Jira", "Confluence"],
                "Data Analysis": ["Tableau"],
                "Design": ["Figma"]
            }
            ai_tools_detected = ["Tableau", "Figma"]
            initial_tool_depth_estimate = {
                "Jira": "expert",
                "Confluence": "regular", 
                "Tableau": "regular",
                "Figma": "surface"
            }

    # Calculate tool maturity score
    total_tools = sum(len(tools) for tools in tools_by_function.values())
    ai_score = int((len(ai_tools_detected) / max(1, total_tools)) * 100)

    # Determine practitioner profile
    if ai_score >= 60:
        practitioner_profile = "Power User"
    elif ai_score >= 30:
        practitioner_profile = "Pragmatic"
    else:
        practitioner_profile = "Minimalist"

    functional_gap_areas = [func for func, tools in tools_by_function.items() if not tools]

    output = {
        "tools_confirmed": [],  # Will be populated by UI confirmation
        "tools_by_function": tools_by_function,
        "ai_tools_detected": ai_tools_detected,
        "tool_depth_estimate": initial_tool_depth_estimate,
        "tool_maturity_score": ai_score,
        "tool_practitioner_profile": practitioner_profile,
        "functional_gap_areas": functional_gap_areas,
        "tool_inference_notes": [],
        "analytics_ready_events": []
    }
    return {"output": output}


def store_user_selected_tools(user_id: str, session_id: str, selected_tools: dict, depth_estimates: dict) -> None:
    """
    After UI confirmation, store final user selections into memory
    """
    payload = {
        "tools_confirmed": list(selected_tools.keys()),
        "tools_by_function": selected_tools,
        "tool_depth_estimate": depth_estimates,
    }
    store_memory("tool_familiarity_agent", user_id, session_id, "tool_confirmation", {}, payload)


def process_custom_tool_input(tool_name: str) -> Tuple[bool, str]:
    """
    Validate and clean up a user-entered tool input
    """
    is_valid, corrected_tool = validate_tool_input(tool_name)
    return is_valid, corrected_tool