
from agents.recommendation.retrieval_orchestrator import run_retrieval_orchestrator

test_subtask = "Convert Tableau dashboards into executive summaries using GPT-4"
test_context = {
    "tool_familiarity": ["GPT-4", "Tableau"],
    "missing_skills": ["prompt engineering", "automation workflows"],
    "domain": "Healthcare",
    "seniority": "Senior Product Manager"
}

# Run the orchestrator with debug output
curated_items, reflection_log, queries = run_retrieval_orchestrator(
    test_subtask,
    test_context,
    user_id="test_user",
    session_id="test_session",
    print_debug=True,
    return_queries=True
)

# Print results
print("\n🔍 Generated Queries:")
for q in queries:
    print(f"- {q}")

print("\n📚 Curated Items:")
for item in curated_items:
    print(f"\nTitle: {item.get('title')}")
    print(f"Source: {item.get('source')}")
    print(f"Link: {item.get('link')}")

print("\n💭 Reflection Log:")
for entry in reflection_log:
    print(f"\nQuery: {entry.get('query')}")
    print(f"Title: {entry.get('title')}")
    print(f"Reflection: {entry.get('reflection')}")
