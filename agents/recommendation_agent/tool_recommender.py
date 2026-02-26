
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def recommend_tools(parsed_resume, use_cases):
    prompt = f"""
You are an AI tooling advisor. The user is a {parsed_resume['seniority']} {parsed_resume['title']} working in the {parsed_resume['domain']} domain.
They use tools like {', '.join(parsed_resume['tools'])}.

Here are AI use cases they might try:
{use_cases}

Now suggest the best AI tools they can use for each use case.
For each one, include:
- Tool name (e.g., Notion AI, GitHub Copilot, Replit, Fireflies.ai)
- One-line description
- Why it's suitable for this user's role and use case

Return in markdown bullet format like:

1. **Tool Name** – One-line use + reason
2. ..."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI tooling advisor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating tool recommendations: {str(e)}"
