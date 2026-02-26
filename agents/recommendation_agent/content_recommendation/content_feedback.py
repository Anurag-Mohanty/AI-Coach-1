# content_feedback.py

from agent_core.feedback_utils import thumbs_up_down
from agent_core.self_learning import learn_from_feedback

# ----------------------------------------
# 👍👎 Record user feedback on content item
# ----------------------------------------
def record_feedback(content_id: str, was_helpful: bool, metadata: dict = None):
    """
    Args:
        content_id (str): Unique ID for the content item (e.g., YouTube ID, GitHub ID)
        was_helpful (bool): True if user found the content useful
        metadata (dict): Optional context to pass for learning (e.g. use case, tools)
    """
    # Step 1: Basic feedback logging
    thumbs_up_down(content_id, was_helpful)

    # Step 2: Optional adaptive learning signal
    if metadata:
        learn_from_feedback(agent="Content Recommender", signal=was_helpful, payload={
            "content_id": content_id,
            "meta": metadata
        })
