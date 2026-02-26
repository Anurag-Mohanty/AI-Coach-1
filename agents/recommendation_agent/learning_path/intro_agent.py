from agent_core.agent_logger import log_agent_event
from agent_core.self_learning import learn_from_feedback
from agent_core.feedback_utils import capture_feedback
from agent_core.trust_explainability import explain_why_included
from agent_core.global_agent_memory import store_memory, retrieve_memory
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_intro(context):
    persona = context.get("persona", {})
    aspiration = context.get("aspiration", {})
    use_case = context.get("use_case", {})
    subtask = context.get("subtask", {})
    user_id = context.get("user_id")
    session_id = context.get("session_id")
    subtask_id = context.get("subtask_id")

    agent_name = "IntroAgent"
    function = "narrative_intro"

    prior_run = retrieve_memory(agent_name, user_id, session_id, subtask_id)

    system_prompt = """
    You are an AI onboarding coach helping a user begin their personalized learning journey.
    Write a short, precise introduction (1–2 lines) that:
    1. Anchors the user in their current role and aspiration
    2. Highlights the specific subtask they are about to develop
    3. Frames the learning path as a personalized, strategic step

    Use a confident, mentor-style tone. Do not make it fluffy or formal. Stay grounded.

    Example:
    Based on your current role as a Senior PM in healthcare, and your aspiration to join Google as a Data Platform PM, we’ve focused on a key subtask critical to that transition: designing stakeholder-facing dashboards powered by GPT.
    """

    user_prompt = f"""
    Current role: {persona.get("role")} in {persona.get("domain")}, impact level: {persona.get("impact_scale")}
    Aspiration: {aspiration.get("aspiration_category")} to become a {aspiration.get("target_role_archetype")} {f'at {aspiration.get("target_company")}' if aspiration.get("target_company") else ''}
    Selected use case: {use_case.get("title")}
    Subtask focus: {subtask.get("title")}
    """

    try:
        intro = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()}
            ]
        ).choices[0].message.content

        log_agent_event("LearningPathAgent.IntroAgent", "Generated intro successfully")

        store_memory(
            agent_name=agent_name,
            user_id=user_id,
            session_id=session_id,
            subtask_id=subtask_id,
            function=function,
            input_fields={"prompt": user_prompt},
            output_fields={"intro": intro.strip()}
        )

        learn_from_feedback(
            agent=agent_name,
            signal=True,
            payload={
                "input": user_prompt,
                "output": intro.strip(),
                "type": "content_generated"
            }
        )

        explain_why_included(
            agent=agent_name,
            output_block=intro.strip(),
            rationale="Provides a personal, role-aware introduction into the learning path."
        )

        capture_feedback(
            agent=agent_name,
            content_block=intro.strip(),
            user_rating=None
        )

        return intro.strip()

    except Exception as e:
        log_agent_event("LearningPathAgent.IntroAgent", f"LLM error: {e}")
        return "We’ve aligned your current role, aspirations, and selected subtask to start your personalized learning path."
