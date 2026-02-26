# input_evaluation.py
# Located in: /agent_core/
"""
🧪 Input Evaluation Utilities
-----------------------------
Purpose: Help agents assess the quality and completeness of the input they receive.
Useful for feedback loops to Resume Agent, LinkedIn Agent, or Aspirations.
Used by:
- Role Detail Agent → detects vague or missing task clusters
- Skill Delta Agent → identifies missing target role
- Meta Agent → compares clarity across user personas

"""


def evaluate_input_completeness(output_dict, required_fields):
    missing_fields = [
        field for field in required_fields if not output_dict.get(field)
    ]
    return {
        "missing_fields": missing_fields,
        "is_complete": len(missing_fields) == 0
    }


def detect_missing_context(context_dict):
    weak_signals = []
    if not context_dict.get("role"):
        weak_signals.append("Missing role title")
    if not context_dict.get("resume"):
        weak_signals.append("No resume uploaded")
    if not context_dict.get("aspiration"):
        weak_signals.append("Missing future goal")
    return {
        "weak_context_signals":
        weak_signals,
        "signal_strength":
        "low"
        if len(weak_signals) >= 2 else "medium" if weak_signals else "high"
    }


def score_input_clarity(input_dict):
    score = 1.0
    if not input_dict.get("task_clusters"):
        score -= 0.3
    if not input_dict.get("effort_distribution"):
        score -= 0.3
    if not input_dict.get("skill_tags"):
        score -= 0.3
    return round(score, 2)

import os
import json
import os
from datetime import datetime

def log_agent_run(agent_name, user_id=None, session_id=None, inputs=None, outputs=None, explanation=None, folder="logs"):
    """Log an agent's execution with inputs and outputs"""
    os.makedirs(folder, exist_ok=True)
    entry = {
        "timestamp": str(datetime.utcnow()),
        "user_id": user_id,
        "session_id": session_id,
        "inputs": inputs,
        "outputs": outputs,
        "explanation": explanation
    }
    filename = os.path.join(folder, f"{agent_name}_runs.jsonl")
    with open(filename, "a") as f:
        f.write(json.dumps(entry) + "\n")

def log_error(agent_name, error_message, user_id=None, session_id=None, folder="logs"):
    """Log an error that occurred during agent execution"""
    os.makedirs(folder, exist_ok=True)
    entry = {
        "timestamp": str(datetime.utcnow()),
        "user_id": user_id,
        "session_id": session_id,
        "error": error_message
    }
    filename = os.path.join(folder, f"{agent_name}_errors.jsonl")
    with open(filename, "a") as f:
        f.write(json.dumps(entry) + "\n")

def log_agent_event(agent_name, event_message, folder="logs"):
    """Log an agent event with a message"""
    os.makedirs(folder, exist_ok=True)
    entry = {
        "timestamp": str(datetime.utcnow()),
        "event": event_message
    }
    filename = os.path.join(folder, f"{agent_name}_events.jsonl")
    with open(filename, "a") as f:
        f.write(json.dumps(entry) + "\n")