def suggest_experiment(missed_uses, confirmed_tools, aspiration):
    """
  Suggest a personalized, lightweight AI experiment based on missed opportunities and tools.
  """
    if not missed_uses or not missed_uses.get("missed_use_cases"):
        return {
            "experiment": "None found",
            "reason": "No missed use cases identified",
            "how_to_try": "N/A"
        }

    # Pick the highest impact missed use case
    top_use = missed_uses["missed_use_cases"][0]
    task = top_use["task"]
    use_case = top_use["suggested_ai_use"]

    # Match with a simple tool if available
    fallback_tool = confirmed_tools[0] if confirmed_tools else "ChatGPT"

    return {
        "experiment":
        f"Try using {fallback_tool} to apply '{use_case}' on your '{task}' task.",
        "reason":
        f"This task is frequent and currently has no AI support.",
        "how_to_try":
        f"Start by framing your '{task}' as a prompt — e.g., 'How can I automate this using {fallback_tool}?'"
    }
