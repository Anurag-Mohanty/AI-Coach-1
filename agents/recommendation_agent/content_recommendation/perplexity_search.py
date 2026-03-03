# perplexity_search.py

import os
import requests
from agent_core.timing_utils import timed_function

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/chat/completions"


# ---------------------------------------------
# Search Perplexity with a user query and context
# ---------------------------------------------
@timed_function("Perplexity Search", display=True)
def search_perplexity(query: str, context_fields: dict = {}, debug=False):
    if not PERPLEXITY_API_KEY:
        print("Skipping Perplexity search - no API key available")
        return []

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    role = context_fields.get("role", context_fields.get("seniority", "professional"))
    domain = context_fields.get("domain", "")
    missing_skills = ", ".join(context_fields.get("missing_skills", [])) or "AI basics"
    aspiration = context_fields.get("aspiration", "")
    suggested_tool = context_fields.get("suggested_tool", "")

    system_prompt = (
        "You are a learning resource curator for busy professionals learning AI. "
        "Find specific, real, public resources (tutorials, videos, courses, guides) "
        "that directly teach the skills needed for the given task. "
        "Prioritize hands-on tutorials and step-by-step walkthroughs over conceptual articles."
    )

    tool_line = f"The tool they will use: {suggested_tool}" if suggested_tool else ""
    aspiration_line = f"Their goal: {aspiration}" if aspiration else ""

    user_prompt = f"""Find the best publicly available learning resources to help someone accomplish this specific task:
"{query}"

About the learner:
- Role: {role}{f" in {domain}" if domain else ""}
- Skills they need to build: {missing_skills}
{tool_line}
{aspiration_line}

Requirements for resources:
- Must be publicly accessible (free or free preview)
- Prioritize: YouTube tutorials, official docs with examples, step-by-step blog posts, hands-on courses
- Should be actionable — the learner should be able to DO something after watching/reading
- Avoid: academic papers, generic overview articles, news pieces
- Prefer resources from 2023 onwards
"""

    body = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }

    try:
        response = requests.post(PERPLEXITY_ENDPOINT, headers=headers, json=body, timeout=30)
        print(f"[DEBUG] Perplexity response status: {response.status_code}")
        response.raise_for_status()
        data = response.json()

        # Prefer the structured search_results array — these are the actual cited sources
        # with real titles, URLs, and snippets. The content field is a markdown article
        # whose section headers were being incorrectly parsed as resource titles.
        structured = data.get("search_results", [])
        if structured:
            results = _parse_search_results(structured)
            print(f"[Perplexity] Parsed {len(results)} resources from search_results")
            return results

        # Fallback: parse the prose content text (less reliable)
        content = data["choices"][0]["message"]["content"]
        if debug:
            print("\n[Perplexity Response]\n", content)
        return _parse_content_text(content)

    except Exception as e:
        print("[Perplexity API Error]", str(e))
        return []


def _parse_search_results(search_results: list, limit: int = 8) -> list:
    """
    Parse the structured search_results array Perplexity returns.
    Each entry has: title, url, date, snippet.
    """
    results = []
    for sr in search_results[:limit]:
        url = sr.get("url", "")
        if not url:
            continue
        is_youtube = "youtube.com" in url or "youtu.be" in url
        results.append({
            "title": sr.get("title", url),
            "link": url,
            "snippet": sr.get("snippet", ""),
            "source": "Perplexity",
            "format": "Video" if is_youtube else "Article",
            "id": url,
        })
    return results


def _parse_content_text(raw_text: str, limit: int = 4) -> list:
    """
    Fallback: parse a markdown prose response for URLs.
    Only used when search_results is absent.
    """
    import re
    results = []
    chunks = re.split(r'\n\n+', raw_text)
    for chunk in chunks:
        lines = chunk.strip().split('\n')
        if len(lines) < 2:
            continue
        first_line = lines[0].strip()
        # Skip markdown headers — they're section titles, not resource names
        if first_line.startswith('#'):
            continue
        title = first_line.strip("-•* []")
        link = re.search(r'(https?://\S+)', chunk)
        snippet = lines[1] if len(lines) > 1 else ""
        if link and title:
            url = link.group(1).rstrip(")")
            results.append({
                "title": title,
                "link": url,
                "snippet": snippet,
                "source": "Perplexity",
                "format": "Video" if "youtube" in url else "Article",
                "id": url,
            })
    return results[:limit]
