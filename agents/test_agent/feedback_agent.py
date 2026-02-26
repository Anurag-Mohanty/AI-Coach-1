def capture_user_feedback(recommendations,
                          experiment_result,
                          follow_up_data=None):
    """
  Captures user feedback about the usefulness of the recommendations and experiment.
  """
    feedback = {}

    # Placeholder logic for now — real version would collect this via UI prompts
    feedback['recommendation_feedback'] = {
        'was_useful': True,
        'reason': "Helped narrow down AI tools quickly"
    }

    feedback['experiment_feedback'] = {
        'attempted': True,
        'success_level': "partial",  # could be: success / partial / fail
        'issues': "Tool was too complex to onboard quickly"
    }

    feedback[
        'follow_up_notes'] = follow_up_data or "User has not returned for follow-up yet."

    feedback['summary'] = (
        "User found initial recommendation helpful but struggled with onboarding. "
        "Needs lighter starter toolkits or simpler walkthroughs.")

    return feedback
