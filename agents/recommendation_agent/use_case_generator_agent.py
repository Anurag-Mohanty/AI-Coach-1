
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_use_cases(parsed_resume):
    prompt = f"""
You are an AI productivity coach. The user is a {parsed_resume['seniority']} {parsed_resume['title']} in the {parsed_resume['domain']} domain. 
They use tools like {', '.join(parsed_resume['tools'])}.

Suggest 3 high-impact AI use cases they can try — specific to their role, domain, and tools. Use concise, actionable phrasing.

Example format:
1. [Use case 1]
2. [Use case 2]
3. [Use case 3]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI productivity coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating use cases: {str(e)}"
