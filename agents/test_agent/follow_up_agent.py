
from datetime import datetime


def follow_up_agent(last_used_tools, last_used_date, feedback_summary=None):
    today = datetime.today().date()
    days_since_last_use = (today - last_used_date).days

    # Nudge logic
    if days_since_last_use > 30:
        nudge = "It's been a while. Want to try something fresh with AI?"
    elif days_since_last_use > 14:
        nudge = "Let's continue building momentum — ready for your next step?"
    else:
        nudge = "You're on a roll! Let's keep going."

    # Tool suggestion
    if last_used_tools and len(last_used_tools) > 0:
        updated_recommendation = f"Try combining {last_used_tools[0]} with a visual tool like Gemini Studio."
    else:
        updated_recommendation = "Let's start with a simple AI tool like ChatGPT or Gemini."

    # Feedback response
    feedback_action = ""
    if feedback_summary:
        if "confusing" in feedback_summary.lower():
            feedback_action = "We'll keep your next step more focused."
        elif "helpful" in feedback_summary.lower():
            feedback_action = "Glad it helped! We'll go one step deeper."
        else:
            feedback_action = "Adjusting based on your feedback."

    return {
        "days_since_last_action": days_since_last_use,
        "nudge": nudge,
        "updated_recommendation": updated_recommendation,
        "feedback_response": feedback_action
    }
