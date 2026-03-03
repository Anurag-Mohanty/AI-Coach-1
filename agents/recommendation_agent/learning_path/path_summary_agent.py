from agent_core.agent_logger import log_agent_event
from agent_core.self_learning import learn_from_feedback
from agent_core.feedback_utils import capture_feedback
from agent_core.trust_explainability import explain_why_included
from agent_core.global_agent_memory import store_memory_sync, get_memory
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_path_summary(context):
    use_case = context.get("use_case", {})
    subtask = context.get("subtask", {})
    reflection_summary = context.get("content", {}).get("reflection_summary")
    aspiration = context.get("aspiration", {})
    user_id = context.get("user_id")
    session_id = context.get("session_id")
    subtask_id = context.get("subtask_id")

    agent_name = "PathSummaryAgent"
    function = "narrative_generation"

    # Optionally check prior memory (for future use)
    prior_run = get_memory(user_id, session_id).get(subtask_id)

    system_prompt = """
    You are an AI career guide explaining how a specific learning path connects to a user's broader goals.
    Write 2–3 clear sentences that:
    1. Connect the subtask to the broader use case
    2. Explain why this particular path is crucial for their target role
    3. Show how it builds critical capabilities needed in their aspired position

    Focus on relevance and connection to goals, not summarizing the content.

    Example:
    Building GPT-powered dashboards is a foundational skill for your target role as an AI PM at Google. This path teaches you to turn AI outputs into decision-ready visuals — a core expectation for leading AI product teams. Mastering this will demonstrate both technical AI fluency and your ability to make AI outputs actionable for stakeholders.
    """

    user_prompt = f"""
    Use case: {use_case.get("title")} (cluster: {use_case.get("cluster")})
    Subtask: {subtask.get("title")}
    Description: {subtask.get("description")}
    Reflection agent insight: {reflection_summary}
    Aspiration: {aspiration.get("aspiration_category")} → {aspiration.get("target_role_archetype")} at {aspiration.get("target_company")}
    """

    try:
        summary = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()}
            ]
        ).choices[0].message.content

        log_agent_event("LearningPathAgent.PathSummaryAgent", "Generated path summary successfully")

        store_memory_sync(agent_name, user_id, session_id, subtask_id, function,
                          {"prompt": user_prompt}, {"summary": summary.strip()})

        learn_from_feedback(
            agent=agent_name,
            signal=True,
            payload={
                "input": user_prompt,
                "output": summary.strip(),
                "type": "content_generated"
            }
        )

        explain_why_included(
            agent=agent_name,
            output_block=summary.strip(),
            rationale="Connects the subtask to business impact and role-specific outcomes."
        )

        capture_feedback(
            agent=agent_name,
            content_block=summary.strip(),
            user_rating=None
        )

        return summary.strip()

    except Exception as e:
        log_agent_event("LearningPathAgent.PathSummaryAgent", f"LLM error: {e}")
        return "This subtask supports your selected use case and builds a skill set relevant to your growth path."
