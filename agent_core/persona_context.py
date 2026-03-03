# persona_context.py
# Located in: /agent_core/
"""
🧬 Persona Memory / Shared Context
----------------------------------
Purpose: Maintain a shared understanding of user profile, goals, preferences,
and key context across all agents in the system.

Used by:
- Aspiration Agent → stores target role, timeline, domain switch
- Resume/LinkedIn Agent → updates company, title, region
- Cultural Agent → uses tone & region
- Meta Agent → runs personalized benchmark comparisons

"""

import os
import json
from datetime import datetime

CONTEXT_FILE = "logs/user_persona_context.json"


def get_user_context(user_id):
    if not os.path.exists(CONTEXT_FILE):
        return {}
    with open(CONTEXT_FILE, "r") as f:
        full_data = json.load(f)
        return full_data.get(user_id, {})


def update_shared_context(user_id, new_payload):
    os.makedirs("logs", exist_ok=True)
    context_data = {}
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r") as f:
            context_data = json.load(f)

    user_context = context_data.get(user_id, {})
    user_context.update(new_payload)
    context_data[user_id] = user_context

    with open(CONTEXT_FILE, "w") as f:
        json.dump(context_data, f, indent=2)


def infer_missing_context(user_context):
    missing = []
    required_keys = ["role", "company_size", "goal", "region"]
    for key in required_keys:
        if key not in user_context:
            missing.append(key)
    return missing


def clear_user_context(user_id: str) -> None:
    """Remove a specific user's persona context (for session reset)."""
    if not os.path.exists(CONTEXT_FILE):
        return
    with open(CONTEXT_FILE, "r") as f:
        data = json.load(f)
    data.pop(user_id, None)
    with open(CONTEXT_FILE, "w") as f:
        json.dump(data, f, indent=2)


def notify_agents_of_major_context_shift(user_id, change_fields):
    return {
        "user_id": user_id,
        "alert": f"Context shift detected: {', '.join(change_fields)}",
        "timestamp": str(datetime.utcnow())
    }
