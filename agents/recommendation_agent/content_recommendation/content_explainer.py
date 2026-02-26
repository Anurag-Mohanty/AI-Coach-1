
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_explanation(item, use_case, skill_gaps):
    """Generate explanation using LLM"""
    title = item.get("title", "")
    snippet = item.get("snippet", "")
    format = item.get("format", "")
    source = item.get("source", "")

    prompt = f"""
You're an intelligent content coach helping a Senior PM in healthcare upskill for real-world tasks.
Explain why the following {format.lower()} from {source} is useful for the use case: "{use_case}"
The user is missing skills in: {', '.join(skill_gaps)}

---
Content Title: {title}
Content Snippet: {snippet}
---
Write a short, human-like recommendation blurb explaining what the user will learn and why it's relevant.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("LLM Explanation Error:", e)
        return "This resource may be relevant, but we couldn't generate a detailed explanation."
