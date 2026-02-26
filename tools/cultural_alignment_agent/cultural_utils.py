# cultural_utils.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def infer_cultural_context_llm(education_list, work_history, location):
    """
    Use a lightweight LLM to infer the user's cultural context based on education, work history, and current location.
    Returns a label like 'South Asian', 'North American', 'Western European', etc.
    """
    try:
        edu_str = ", ".join([
            f"{e.get('institution', '')} ({e.get('location', '')})"
            for e in education_list
        ])
        work_str = ", ".join([
            f"{w.get('company', '')} ({w.get('location', '')})"
            for w in work_history
        ])

        prompt = f"""
Based on the user's education, work history, and location, infer their dominant cultural learning and communication context. Examples of some valid outputs (not exhaustive) include:
- South Asian
- North American
- Western European
- East Asian
- Mixed
- Unknown

please feel free to add more labels as needed.

Education: {edu_str or 'None'}
Work History: {work_str or 'None'}
Current Location: {location or 'Unknown'}

Return only the most likely cultural label. Be particularly mindful of Oceanian/Australian backgrounds when education and work history are predominantly in Australia or New Zealand. For example, someone educated and working primarily in Australian cities should be labeled as 'Australian' or 'Oceanian', not European.

Return only the most likely cultural label 
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role":
                "system",
                "content":
                "You are a cultural context inference assistant."
            }, {
                "role": "user",
                "content": prompt
            }])

        result = response.choices[0].message.content.strip()
        return result if result else "Unknown"

    except Exception:
        return "Unknown"
