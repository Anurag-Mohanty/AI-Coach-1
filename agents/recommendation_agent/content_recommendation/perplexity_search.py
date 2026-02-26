# perplexity_search.py

import os
import requests
from agent_core.timing_utils import timed_function # Added import

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/chat/completions"


# ---------------------------------------------
# Search Perplexity with a user query and context
# ---------------------------------------------
@timed_function("Perplexity Search", display=True) # Added timing decorator
def search_perplexity(query: str, context_fields: dict = {}, debug=False):
    if not PERPLEXITY_API_KEY:
        print("Skipping Perplexity search - no API key available")
        return []
        
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = "You are an AI content discovery assistant. Your job is to return real, public training resources (articles, videos, code repos, tutorials) that help users perform tasks related to AI and automation in their job."

    user_prompt = f"""
What are the best publicly available resources to help with the following task:
"{query}"

User context:
- Domain: {context_fields.get('domain', 'N/A')}
- Tools: {', '.join(context_fields.get('tool_familiarity', [])) or 'None'}
- Missing Skills: {', '.join(context_fields.get('missing_skills', [])) or 'None'}
- Seniority: {context_fields.get('seniority', 'N/A')}

Return links to resources that:
- Are public and accessible
- Come from trusted sources (YouTube, GitHub, Medium, LinkedIn, etc.)
- Include tutorials, demos, or walkthroughs
- Are simple enough for a beginner learning AI for their job
"""

    body = {
        "model": "sonar",
        "messages": [{
            "role": "system",
            "content": system_prompt
        }, {
            "role": "user",
            "content": user_prompt
        }],
        "stream":
        False
    }

    try:
        response = requests.post(PERPLEXITY_ENDPOINT,
                               headers=headers,
                               json=body,
                               timeout=30)
        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response body: {response.text}")
        response.raise_for_status()
        data = response.json()
        content = data['choices'][0]['message']['content']

        if debug:
            print("\n[Perplexity Response]\n", content)

        return parse_perplexity_results(content)
    except Exception as e:
        print("[Perplexity API Error]", str(e))
        return []


# ---------------------------------------------
# Parse Perplexity text response into structured content items
# ---------------------------------------------
def parse_perplexity_results(raw_text: str, limit: int = 4):
    import re
    results = []
    chunks = re.split(r'\n\n+', raw_text)
    for chunk in chunks:
        lines = chunk.strip().split('\n')
        if len(lines) < 2:
            continue
        title = lines[0].strip("-• ")
        link = re.search(r'(https?://\S+)', chunk)
        snippet = lines[1] if len(lines) > 1 else ""
        if link:
            results.append({
                "title": title,
                "link": link.group(1),
                "snippet": snippet,
                "source": "Perplexity",
                "format": "Article",
                "id": link.group(1)
            })
    return results