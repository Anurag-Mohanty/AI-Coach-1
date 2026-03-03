# research_agent.py (Perplexity-powered, now includes format classification)

from agent_core.global_agent_memory import store_memory_sync, get_memory
from .perplexity_search import search_perplexity

# -----------------------------------
# Classify content format from URL
# -----------------------------------
def classify_format(url):
    if "github.com" in url:
        return "Code Notebook"
    elif "youtube.com" in url:
        return "Video"
    elif "medium.com" in url or "dev.to" in url:
        return "Article"
    elif "reddit.com" in url or "quora.com" in url:
        return "Q&A Thread"
    elif "linkedin.com" in url:
        return "Post"
    elif "stackoverflow.com" in url:
        return "StackOverflow Answer"
    else:
        return "Web Resource"

# -----------------------------------
# Main entry with Perplexity + memory
# -----------------------------------
async def run_research_agent(subtask, context, user_id="anon_user", session_id="default_session", print_debug=False):
    agent_name = "research_agent"
    subtask_id = subtask[:40].replace(" ", "_")

    # Check memory first
    prior = get_memory(user_id, session_id).get(subtask_id)
    if prior:
        print("[Memory] Reusing previous research result")
        return prior.get("output_fields", {}).get("results", [])

    # Run Perplexity search instead of Bing
    print("\n🔍 Running Perplexity search...")
    results = search_perplexity(subtask, context_fields=context, debug=print_debug)

    # Add format classification to each result
    for item in results:
        item["format"] = classify_format(item.get("link", ""))

    # Store to global memory
    store_memory_sync(agent_name, user_id, session_id, subtask_id, "content_discovery",
                      {"subtask": subtask}, {"results": results})

    return results