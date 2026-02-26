# tone_profile_engine.py
from openai import OpenAI
import os
from .cultural_utils import infer_cultural_context_llm

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def infer_learning_tone_profile(ethnicity,
                                work_style,
                                collab_pattern,
                                tone_preference,
                                education_list=None,
                                work_history=None,
                                location=None):
    if not ethnicity:
        ethnicity = infer_cultural_context_llm(education_list or [],
                                               work_history or [], location
                                               or "")

    prompt = f"""
You are a cultural communication and learning tone profiler. Based on the user's attributes, infer the most effective tone, analogy style, and example phrases for delivering personalized coaching content.

User Details:
- Ethnicity or region: {ethnicity or 'Not specified'}
- Preferred working style: {work_style or 'Not specified'}
- Typical team dynamic: {collab_pattern or 'Not specified'}
- Preferred tone: {tone_preference or 'Not specified'}

Return a JSON object with these keys:
- tone_style (e.g., motivational, directive, warm)
- analogy_style (e.g., storytelling, business metaphors, engineering analogies)
- feedback_style (e.g., gentle nudge, blunt, step-by-step)
- tone_phrases (3 examples of how to phrase a suggestion)
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a tone profiling assistant."
            }, {
                "role": "user",
                "content": prompt
            }])

        raw = response.choices[0].message.content.strip()
        json_start = raw.find('{')
        json_str = raw[json_start:] if json_start != -1 else '{}'

        import json
        result = json.loads(json_str)
        return result

    except Exception as e:
        return {
            "tone_style":
            "directive",
            "analogy_style":
            "checklist-based",
            "feedback_style":
            "goal-oriented",
            "tone_phrases": [
                "Let’s simplify this down to steps.",
                "Here’s the fastest way to improve.",
                "Start with what matters — ignore fluff."
            ],
            "error":
            str(e)
        }


def generate_prompt_variants(topic):
    """
    Generate 3 tone-variant phrasing examples for a simple, relevant topic.
    """
    return [{
        "label":
        "Directive / Tactical",
        "text":
        f"Start by identifying the goal of the {topic}. Then define 3 concrete actions. Here’s the fastest path forward."
    }, {
        "label":
        "Story-Driven",
        "text":
        f"Imagine you’re walking into a meeting where {topic} is a pain point. Everyone’s talking past each other — until you show a working prototype that aligns vision."
    }, {
        "label":
        "Analytical / Contrastive",
        "text":
        f"Traditional approaches to {topic} focus on linear delivery. Modern methods involve async sync hybrids. Let’s compare both and find what fits."
    }]
