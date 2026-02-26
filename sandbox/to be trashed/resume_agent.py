from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_resume(resume_text):
    prompt = f"""
You are a resume analyzer AI helping product managers upskill in AI. Analyze the following resume and extract the following fields:

1. **title**: Current job title (e.g., "Principal Product Manager")
2. **seniority**: Seniority level (IC, Lead, Director, VP, etc.)
3. **company**: Most recent company name
4. **company_size**: Size of company in people or ARR (estimate if not stated)
5. **domain**: Domain/industry (e.g., healthcare, e-commerce, fintech)
6. **region**: Country or region the user is based in (if detectable)
7. **team_scope**: Size or scope of teams led (e.g., "led 12-person cross-functional team")
8. **cross_functional**: Other teams interacted with (e.g., Eng, Design, Ops)
9. **ai_keywords**: AI-related terms, tools, or responsibilities (e.g., "GPT", "prompt tuning", "Copilot", "LangChain")
10. **tools**: Technologies or tools used (e.g., SQL, Jira, PEGA)
11. **achievements**: Key career achievements, especially with numbers or impact

Return your answer as a JSON dictionary with exactly these keys. Be concise, accurate, and return only valid JSON.

Resume:
\"\"\"
{resume_text}
\"\"\"
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume parsing engine. Return valid, well-formatted JSON with no explanation text."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
        )

        raw_response = response.choices[0].message.content.strip()
        parsed_json = json.loads(raw_response)
        return json.dumps(parsed_json)

    except Exception as e:
        return json.dumps({"error": str(e)})
