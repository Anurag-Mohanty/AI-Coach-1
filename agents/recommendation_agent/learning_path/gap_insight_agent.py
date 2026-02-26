from agent_core.agent_logger import log_agent_event
from agent_core.self_learning import learn_from_feedback
from agent_core.feedback_utils import capture_feedback
from agent_core.trust_explainability import explain_why_included
from agent_core.global_agent_memory import store_memory, retrieve_memory
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_gap_reflection(context):
    skill_delta = context.get("skill_delta", {})
    persona = context.get("persona", {})
    subtask = context.get("subtask", {})
    user_id = context.get("user_id")
    session_id = context.get("session_id")
    subtask_id = context.get("subtask_id")

    missing_skills = skill_delta.get("missing_skills", [])
    ai_enabler_gaps = skill_delta.get("ai_enabler_gaps", [])
    all_gaps = list(set(missing_skills + ai_enabler_gaps))

    if not all_gaps:
        return "You're currently well-positioned to take on this subtask with your existing skills."

    role = persona.get("role", "your current role")
    subtask_title = subtask.get("title", "this subtask")

    agent_name = "GapInsightAgent"
    function = "gap_diagnosis"

    prior_run = retrieve_memory(agent_name, user_id, session_id, subtask_id)

    system_prompt = """
    You are a skill strategy coach. Write a short diagnostic-style reflection that:
    1. Anchors the user in their current role
    2. Outlines the most important gaps to address in the context of the selected subtask
    3. Frames these gaps as learnable, practical, and directly relevant

    Keep the tone factual but supportive. Don't say "you should" or "you must." Be helpful.

    Example:
    While your background as a Senior PM provides a strong foundation, we identified a few skill gaps that could impact your ability to succeed at designing stakeholder-facing dashboards powered by GPT:
    - Prompt engineering
    - Data grounding
    - LLM orchestration
    - RAG architecture
    """

    user_prompt = f"""
    Current role: {role}
    Subtask focus: {subtask_title}
    Skill gaps identified:
    {chr(10).join([f"- {gap}" for gap in all_gaps])}
    """

    try:
        reflection = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()}
            ]
        ).choices[0].message.content

        log_agent_event("LearningPathAgent.GapInsightAgent", "Generated gap analysis successfully")

        store_memory(
            agent_name=agent_name,
            user_id=user_id,
            session_id=session_id,
            subtask_id=subtask_id,
            function=function,
            input_fields={"prompt": user_prompt},
            output_fields={"reflection": reflection.strip()}
        )

        learn_from_feedback(
            agent=agent_name,
            signal=True,
            payload={
                "input": user_prompt,
                "output": reflection.strip(),
                "type": "content_generated"
            }
        )

        explain_why_included(
            agent=agent_name,
            output_block=reflection.strip(),
            rationale="Highlights personalized skill gaps that are essential to address the subtask."
        )

        capture_feedback(
            agent=agent_name,
            content_block=reflection.strip(),
            user_rating=None
        )

        return reflection.strip()

    except Exception as e:
        log_agent_event("LearningPathAgent.GapInsightAgent", f"LLM error: {e}")
        return "You may want to revisit a few foundational skills to confidently take on this subtask."