
from agent_core.agent_logger import log_agent_event
from agent_core.self_learning import learn_from_feedback
from agent_core.feedback_utils import capture_feedback
from agent_core.trust_explainability import explain_why_included
from agent_core.global_agent_memory import store_memory, retrieve_memory
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_closing_cta(context):
    subtask = context.get("subtask", {})
    subtask_title = subtask.get("title", "this subtask")
    user_id = context.get("user_id")
    session_id = context.get("session_id")
    subtask_id = context.get("subtask_id")

    agent_name = "ClosingCTAAgent"
    function = "call_to_action"

    prior_run = retrieve_memory(agent_name, user_id, session_id, subtask_id)

    system_prompt = """
    You are a personalized learning coach. Write a single-sentence closing message to the user that:
    1. Encourages the user to begin
    2. Reinforces the importance of starting with the first step
    3. Ties it back to the selected subtask

    Keep it crisp and confident — don't oversell. Avoid exclamation marks. No filler.

    Example:
    Start with the first module above — it lays the foundation for progressing through designing stakeholder-facing dashboards powered by GPT with confidence.
    """

    user_prompt = f"Subtask focus: {subtask_title}"

    try:
        cta = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()}
            ]
        ).choices[0].message.content

        log_agent_event("LearningPathAgent.ClosingCTAAgent", "Generated closing CTA successfully")

        store_memory(
            agent_name=agent_name,
            user_id=user_id,
            session_id=session_id,
            subtask_id=subtask_id,
            function=function,
            input_fields={"prompt": user_prompt},
            output_fields={"cta": cta.strip()}
        )

        learn_from_feedback(
            agent=agent_name,
            signal=True,
            payload={
                "input": user_prompt,
                "output": cta.strip(),
                "type": "content_generated"
            }
        )

        explain_why_included(
            agent=agent_name,
            output_block=cta.strip(),
            rationale="Motivates user to start their learning journey on the selected subtask."
        )

        capture_feedback(
            agent=agent_name,
            content_block=cta.strip(),
            user_rating=None
        )

        return cta.strip()

    except Exception as e:
        log_agent_event("LearningPathAgent.ClosingCTAAgent", f"LLM error: {e}")
        return f"Start with the first module — it lays the foundation for progressing through {subtask_title}."
