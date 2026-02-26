"""
📚 Self-Learning Utility
Location: agent_core/self_learning.py

Purpose:
--------
This module manages structured feedback signals from agents and users,
and translates those into long-term learning that can be re-used across sessions.
It exposes interpreted feedback (like prompt considerations) to enhance future prompt building,
and retains raw correction signals for evaluation or dashboard usage.

Functions:
----------
- learn_from_feedback(...): logs agent-specific feedback events
- track_thumbs_up_rate(...): tracks success/failure on field-level interactions
- get_correction_signal_summary(...): returns raw correction counts by field
- generate_prompt_considerations_from_feedback(...): interprets feedback via prompt_builder + LLM
- get_prompt_considerations(...): retrieves prompt considerations from memory to inject into prompts
- evaluate_field_health_for_prompting(...): flags weak fields based on thumbs-up rate
"""

from agent_core.global_agent_memory import store_memory, get_context
from agent_core.prompt_builder import build_prompt_from_context
from agent_core.llm_client import call_llm_model
from collections import defaultdict


def learn_from_feedback(agent, user_id, input_fields, signal=True, payload=None):
    store_memory(agent_name=agent,
                 user_id=user_id,
                 session_id=None,
                 subtask_id="raw_feedback_event",
                 function="feedback_log",
                 input_fields=input_fields,
                 output_fields={
                     "thumbs_up": signal,
                     "details": payload
                 })


def track_thumbs_up_rate(agent_name, field_name):
    # Placeholder: returns mock score
    # Later: track % of thumbs-up responses per field across time
    return 0.82


def evaluate_field_health_for_prompting(agent_name):
    # Returns human-readable recommendation if weak field detected
    signals = get_correction_signal_summary(agent_name)
    low_confidence = [f for f, count in signals
                      if count >= 3]  # arbitrary threshold
    messages = [
        f"Prompt update recommended for '{f}' — frequent correction signals."
        for f in low_confidence
    ]
    return messages


def get_correction_signal_summary(agent_name):
    # Stub — replace with lookup from logs or memory
    mock = {
        "role_detail_agent": [("task_clusters", 4),
                              ("effort_distribution", 2)],
        "aspiration_agent": [("realism_score", 3)]
    }
    return mock.get(agent_name, [])


def generate_prompt_considerations_from_feedback(agent_name, user_id,
                                                 session_id):
    context = get_context(user_id, session_id)
    raw_feedback = context.get("raw_feedback_event", {})

    prompt_pkg = build_prompt_from_context(
        task="feedback_interpretation",
        agent_role="You are an AI self-learning strategist.",
        task_instruction=
        "Convert structured agent feedback into 2–3 prompt considerations",
        memory_context={
            "agent": agent_name,
            "feedback": raw_feedback
        },
        output_format=
        "Return a list of short, actionable considerations (as bullet points) to improve future prompts."
    )

    llm_response = call_llm_model(prompt_pkg["prompt"],
                                  model_params={"temperature": 0.2})
    interpreted = [
        line.strip("- • ") for line in llm_response.strip().split("\n")
        if line.strip()
    ]

    store_memory(agent_name=agent_name,
                 user_id=user_id,
                 session_id=session_id,
                 subtask_id="feedback_nudges",
                 function="self_learning_evaluator",
                 output_fields={"prompt_considerations": interpreted})

    return interpreted


async def get_prompt_considerations(agent_name, user_id, session_id=None):
    context = await get_context(user_id, session_id)
    return context.get("prompt_considerations", [])