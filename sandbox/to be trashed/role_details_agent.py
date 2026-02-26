
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def infer_work_structure(role, resume=None, linkedin=None, role_context=None, aspiration=None):
    """
    Infers a structured view of the user's typical work activities, frequencies, and where AI could help.

    Returns a JSON-like dict with:
    - task_clusters
    - effort_distribution
    - frequency_map
    - ai_opportunity_density
    """

    # Compose prompt
    prompt = f"""
    You are an expert in productivity mapping and AI opportunity identification.

    Based on the following information:
    - Role: {role}
    {"- Resume: " + resume if resume else ""}
    {"- LinkedIn: " + linkedin if linkedin else ""}
    {"- Role Context: " + str(role_context) if role_context else ""}
    {"- Aspiration: " + aspiration if aspiration else ""}

    Please analyze the user's work and return the following as a JSON object:
    1. "task_clusters": Main types of tasks grouped by function or theme.
    2. "effort_distribution": % effort spent on each cluster (approx).
    3. "frequency_map": How often each task cluster occurs (e.g. daily, weekly, quarterly).
    4. "ai_opportunity_density": How much AI automation can help each task cluster.

    Return only the JSON.
        """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a structured work modeling assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        result = response.choices[0].message.content.strip()
        return result

    except Exception as e:
        # Fallback
        return {
            "task_clusters": {},
            "effort_distribution": {},
            "frequency_map": {},
            "ai_opportunity_density": {},
            "error": str(e)
        }
