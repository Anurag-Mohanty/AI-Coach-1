
from agents.recommendation.perplexity_search import search_perplexity

test_query = """What are the best publicly available resources to help with the following task:
Prompt engineering to convert Tableau KPIs to stakeholder summaries"""

test_context = {
    "tool_familiarity": ["GPT-4", "Tableau"],
    "missing_skills": ["prompt chaining"],
    "domain": "Healthcare",
    "seniority": "Senior Product manager"
}

results = search_perplexity(test_query, test_context, debug=True)
print("\nResults:")
for r in results:
    print(f"\nTitle: {r.get('title')}")
    print(f"Link: {r.get('link')}")
    print(f"Snippet: {r.get('snippet')}")
