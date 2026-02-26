# Applying the provided changes to pass examples to the prompt building process.
import json

"""
📘 Prompt Builder Utility
Location: agent_core/prompt_builder.py

Purpose:
--------
The Prompt Builder generates high-quality, structured, and personalized LLM prompts based on declared agent tasks,
user persona, session context, and feedback considerations. It supports all agents in the system and can be exposed externally.

Primary Functions:
------------------
1. request_prompt_requirements(task):
   Returns the required/optional fields needed for that task.

2. build_prompt_from_context(...):
   Builds the actual LLM-ready prompt using user and session context, task instructions, examples, format constraints,
   and learning considerations including self-learning feedback pulled from memory.

This module supports:
- Best-practice prompting (role identity, structured outputs, tone control)
- Prompt memory + feedback loops
- Agent-agnostic design with task-specific scaffolds
- Memory-aware enrichment via prompt_considerations if present
- Future API/UX integration
"""

from agent_core.prompt_task_templates import get_task_template


def request_prompt_requirements(task):
    template = get_task_template(task)
    return {
        "required_fields":
        template.get("required_fields", []) if template else [],
        "optional_fields":
        template.get("optional_fields", []) if template else [],
        "examples_supported":
        True if template else False,
        "output_format_required":
        "output_format" in template if template else False
    }


def build_prompt_from_context(task,
                              agent_role=None,
                              task_instruction=None,
                              user_context=None,
                              memory_context=None,
                              examples=None,
                              considerations=None,
                              output_format=None):
    from copy import deepcopy

    template = get_task_template(task) or {}

    # Use template defaults if parameters not explicitly provided
    agent_role = agent_role or template.get("agent_role",
                                            "You are a helpful assistant.")
    task_instruction = task_instruction or template.get(
        "task_instruction", f"Perform task: {task}")
    output_format = output_format or template.get("output_format", None)
    base_considerations = considerations or template.get("considerations", [])

    # Check for learning-based prompt considerations inside memory context
    memory_considerations = memory_context.get("prompt_considerations",
                                               []) if memory_context else []
    merged_considerations = base_considerations + memory_considerations

    prompt_parts = []
    prompt_parts.append(f"You are {agent_role.strip()}\n")
    prompt_parts.append(f"Task: {task_instruction.strip()}\n")

    context_lines = []
    if user_context:
        context_lines.append("User Persona:")
        for k, v in user_context.items():
            context_lines.append(f"- {k}: {v}")
    if memory_context:
        context_lines.append("\nKnown Profile Context:")
        for k, v in memory_context.items():
            if k != "prompt_considerations":
                context_lines.append(f"- {k}: {v}")
    prompt_parts.append("\n".join(context_lines))

    if merged_considerations:
        prompt_parts.append("\n\nSystem Considerations:")
        for item in merged_considerations:
            prompt_parts.append(f"- {item}")

    # Use template examples if none provided
    examples = examples or template.get("examples", [])

    if examples:
        prompt_parts.append("\nExamples:")
        for ex in examples:
            prompt_parts.append(f"\nInput:\n{json.dumps(ex['input'], indent=2)}")
            prompt_parts.append(f"\nOutput:\n{json.dumps(ex['output'], indent=2)}\n")

    if output_format:
        prompt_parts.append("\nReturn output using the following format:")
        prompt_parts.append(output_format.strip())

    prompt = "\n\n".join(prompt_parts)

    print("\n=== Prompt Builder Output ===")
    print(json.dumps({
        "prompt": prompt,
        "agent_role": agent_role,
        "task_instruction": task_instruction,
        "considerations": considerations,
        "output_format": output_format
    }, indent=2))

    combined_context = {**(user_context or {}), **(memory_context or {})}
    missing = [
        f for f in template.get("required_fields", [])
        if f not in combined_context
    ]

    return {"prompt": prompt, "missing_fields": missing, "used_cache": False}