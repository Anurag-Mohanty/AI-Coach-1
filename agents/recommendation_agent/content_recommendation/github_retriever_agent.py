# github_retriever_agent.py (LLM-enhanced)

import requests
import os
from openai import OpenAI
from agent_core.timing_utils import timed_function # Added import

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
GITHUB_API_URL = "https://api.github.com/search/repositories"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("Warning: GITHUB_TOKEN not found in environment variables")

GITHUB_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def generate_github_query(focused_subtask, context):
    role = context.get("role", "")
    prompt = f"""
Generate 3 GitHub search queries to find repos, templates, guides, or tools relevant to this task.

Task: {focused_subtask}
Role: {role}
Tools they use: {', '.join(context.get('tool_familiarity', []))}
Skills they need: {', '.join(context.get('missing_skills', []))}

Return only short search terms, one per line. Do NOT restrict to Python.
Focus on things that would help a professional learn or apply AI to this task:
- Prompt templates and example workflows
- Tools, integrations, or frameworks for the task
- Starter kits or how-to guides
- Avoid academic papers or pure ML research repos

Examples of good queries: "ai roadmap prioritization template", "chatgpt product manager prompts", "ai market research automation"
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150
        )
        return [q.strip() for q in response.choices[0].message.content.split("\n") if q.strip()]
    except Exception as e:
        print("Query generation failed:", e)
        return [focused_subtask]

@timed_function("GitHub Retrieval", display=True)
async def search_github_for_task(focused_subtask, context, max_results=5):
    if not GITHUB_TOKEN:
        print("Skipping GitHub search - no token available")
        return []

    queries = generate_github_query(focused_subtask, context)
    all_results = []

    for query in queries:
        # Simplify query and expand search scope
        params = {
            "q": f"{query} in:name,description,readme",
            "sort": "stars",
            "order": "desc",
            "per_page": 5
        }
        print(f"Searching GitHub with query: {query}")
        try:
            response = requests.get(GITHUB_API_URL, headers=GITHUB_HEADERS, params=params)
            print(f"GitHub API Response Status: {response.status_code}")
            print(f"GitHub API Response: {response.json()}")
            if response.status_code != 200:
                print("GitHub search failed:", response.status_code, response.text)
                continue

            data = response.json()
            items = data.get('items', [])
            print(f"GitHub API Results: {len(items)} items found")

            processed_items = []
            for item in items:
                processed_items.append({
                    'title': item.get('name', ''),
                    'link': item.get('html_url', ''),
                    'description': item.get('description', ''),
                    'type': 'GitHub',
                    'source': 'GitHub'
                })
            all_results.extend(processed_items)

        except Exception as e:
            print("Error during GitHub search:", e)
            continue

    return all_results