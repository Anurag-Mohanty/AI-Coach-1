from agent_core.agent_logger import log_agent_event
from agent_core.input_evaluation import validate_inputs
from agent_core.compliance_utils import validate_learning_path
from agent_core.global_agent_memory import get_context

from .intro_agent import generate_intro
from .path_summary_agent import generate_path_summary
from .gap_insight_agent import generate_gap_reflection
from .learning_steps_agent import generate_learning_steps
from .closing_cta_agent import generate_closing_cta

async def recommend_learning_path(user_id, session_id):
    context = get_context(user_id, session_id)
    context["user_id"] = user_id
    context["session_id"] = session_id
    subtask_id = context.get("subtask", {}).get("id", "default_subtask")
    context["subtask_id"] = subtask_id

    if not validate_inputs([context]):
        return {"error": "Missing or invalid input fields"}

    log_agent_event("LearningPathAgent", "Started learning path generation")

    try:
        intro = (await generate_intro(context)).strip()
        summary = (await generate_path_summary(context)).strip()
        gaps = (await generate_gap_reflection(context)).strip()

        # Updated: learning_steps_data includes subtask-contextual sequencing and narration
        learning_steps_data = await generate_learning_steps(context, return_structured_output=True)
        steps = learning_steps_data.get("narrative", "").strip() if isinstance(learning_steps_data, dict) else learning_steps_data.strip()

        cta = (await generate_closing_cta(context)).strip()

        output = {
            "intro_text": intro,
            "path_summary": summary,
            "gap_analysis": gaps,
            "learning_steps": steps,
            "closing_cta": cta,
            "learning_modules": context.get("content", {}).get("curated_training", []),
            "learning_path_type": context.get("aspiration", {}).get("aspiration_category", "AI Fluency"),
            "module_reasoning_map": {},
            "pacing_guidance": "1 module every 2–3 days",
            "confidence_level": "High",
            "persona_profile": context.get("persona", {})
        }

        if not validate_learning_path(output.get("learning_modules", [])):
            output["warning"] = "Generated path failed compliance checks."

        log_agent_event("LearningPathAgent", "Completed learning path generation")

        return output

    except Exception as e:
        log_agent_event("LearningPathAgent", f"Agent error: {e}")
        return {
            "error": "Failed to generate learning path.",
            "intro_text": "",
            "path_summary": "",
            "gap_analysis": "",
            "learning_steps": "",
            "closing_cta": ""
        }
