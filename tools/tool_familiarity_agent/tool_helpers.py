from agent_core.global_agent_memory import store_memory
from agent_core.feedback_utils import capture_user_feedback
from .tool_input_validator import validate_tool_input
from typing import Dict, List, Tuple


def store_user_selected_tools(user_id: str, session_id: str,
                              selected_tools: Dict[str, List[str]],
                              depth_estimates: Dict[str, str]) -> None:
    """
    After user confirms tool familiarity and depth, store selections in memory.
    """
    payload = {
        "tools_confirmed": list(selected_tools.keys()),
        "tools_by_function": selected_tools,
        "tool_depth_estimate": depth_estimates,
    }
    store_memory("tool_familiarity_agent", user_id, session_id,
                 "tool_confirmation", {}, payload)


def process_custom_tool_input(tool_name: str) -> Tuple[bool, str]:
    """
    Validate user-entered tool names to ensure they are real tools (not languages, not vague terms).
    Returns (is_valid: bool, corrected_tool: str)
    """
    is_valid, corrected_tool = validate_tool_input(tool_name)
    return is_valid, corrected_tool


def capture_tool_feedback(user_id: str,
                          session_id: str,
                          category: str,
                          thumbs_up: bool,
                          notes: str = "") -> None:
    """
    Capture thumbs up/down feedback on each functional tool cluster.
    """
    feedback_payload = {
        "category": category,
        "thumbs_up": thumbs_up,
        "notes": notes,
    }
    capture_user_feedback(agent_name="tool_familiarity_agent",
                          feedback_dict=feedback_payload)
    # Optionally, could also integrate learning signal based on feedback later
