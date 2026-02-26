# feedback_utils.py
# Located in: /agent_core/
"""
📋 Feedback Utilities
----------------------
Purpose: Capture, store, and analyze user feedback for any agent output.
Helps agents learn from corrections, thumbs up/down, or open-text notes.

Used by:
- Resume Agent → thumbs up on parsed title
- Role Detail Agent → correction on task clusters
- Tool Recommender → thumbs down on irrelevant tools

"""

import json
import os
from datetime import datetime

def capture_user_feedback(thumbs=None, corrections=None, notes=""):
    return {
        "timestamp": str(datetime.utcnow()),
        "thumbs_up": thumbs or [],
        "corrections": corrections or {},
        "notes": notes
    }


def store_feedback_locally(agent_name, feedback_dict, folder="logs"):
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{agent_name}_feedback.jsonl")
    with open(filename, "a") as f:
        f.write(json.dumps(feedback_dict) + "\n")


def summarize_feedback_trends(agent_name, folder="logs"):
    filename = os.path.join(folder, f"{agent_name}_feedback.jsonl")
    if not os.path.exists(filename):
        return {}
    feedback_list = []
    with open(filename, "r") as f:
        for line in f:
            feedback_list.append(json.loads(line.strip()))
    thumbs_count = sum(len(fb.get("thumbs_up", [])) for fb in feedback_list)
    correction_count = sum(
        len(fb.get("corrections", {})) for fb in feedback_list)
    return {
        "total_entries": len(feedback_list),
        "thumbs_up_fields": thumbs_count,
        "correction_fields": correction_count
    }

def capture_feedback(agent: str, content_block: str, user_rating: bool = None):
    """Record feedback about agent output"""
    feedback_dir = "logs"
    os.makedirs(feedback_dir, exist_ok=True)

    feedback = {
        "timestamp": str(datetime.utcnow()),
        "agent": agent,
        "content": content_block,
        "rating": user_rating
    }

    filename = os.path.join(feedback_dir, f"{agent}_feedback.jsonl")
    with open(filename, "a") as f:
        f.write(json.dumps(feedback) + "\n")

def thumbs_up_down(content_id: str, was_helpful: bool):
    """Record thumbs up/down feedback for a content item"""
    feedback_dir = "logs"
    os.makedirs(feedback_dir, exist_ok=True)

    feedback = {
        "timestamp": str(datetime.utcnow()),
        "content_id": content_id,
        "helpful": was_helpful
    }

    filename = os.path.join(feedback_dir, "content_feedback.jsonl")
    with open(filename, "a") as f:
        f.write(json.dumps(feedback) + "\n")