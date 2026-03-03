import json
import os
import re
from datetime import datetime
from typing import Optional, Tuple

USER_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "user_data")


def _ensure_dir():
    os.makedirs(USER_DATA_DIR, exist_ok=True)


def _user_file(user_id: str) -> str:
    return os.path.join(USER_DATA_DIR, f"{user_id}.json")


def _slugify(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name or "user"


def create_user_model(user_id: str, name: str) -> dict:
    now = datetime.utcnow().isoformat()
    return {
        "user_id": user_id,
        "name": name,
        "created_at": now,
        "last_active": now,
        "profile": {},
        "coaching_state": {
            "current_phase": "hook",
            "journey_template_id": None,
            "steps_completed": [],
            "next_recommended_action": None,
            "last_conversation_summary": None,
            "open_questions": [],
        },
        "knowledge_state": {},
        "preferences": {
            "communication_style": None,
            "learning_style": None,
            "tone": None,
        },
        "interaction_history": [],
        "feedback_signals": {
            "content_thumbs_up": [],
            "content_thumbs_down": [],
            "recommendations_accepted": 0,
            "recommendations_rejected": 0,
        },
    }


def load_user_model(user_id: str) -> Optional[dict]:
    _ensure_dir()
    path = _user_file(user_id)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def save_user_model(user_id: str, model: dict) -> None:
    _ensure_dir()
    model["last_active"] = datetime.utcnow().isoformat()
    with open(_user_file(user_id), "w") as f:
        json.dump(model, f, indent=2)


def delete_user(user_id: str) -> None:
    """Permanently delete all stored data for a user (for session reset)."""
    path = _user_file(user_id)
    if os.path.exists(path):
        os.remove(path)


def get_or_create_user(name: str) -> Tuple[dict, bool]:
    """Returns (user_model, is_returning_user)."""
    user_id = _slugify(name)
    existing = load_user_model(user_id)
    if existing:
        return existing, True
    model = create_user_model(user_id, name)
    save_user_model(user_id, model)
    return model, False
