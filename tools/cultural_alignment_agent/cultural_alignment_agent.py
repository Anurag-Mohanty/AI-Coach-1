
import os
import json
from openai import OpenAI
from agent_core.agent_logger import log_agent_run, log_error
from agent_core.feedback_utils import capture_user_feedback
from agent_core.global_agent_memory import store_memory
from agent_core.input_evaluation import evaluate_input_completeness
from agent_core.trust_explainability import generate_why_this_output_summary
from agent_core.downstream_formatter import format_for_agent
from .tone_profile_engine import infer_learning_tone_profile

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_cultural_alignment_agent(user_id, session_id, context_inputs):
    agent_name = "cultural_alignment_agent"
    try:
        if not isinstance(context_inputs, dict):
            raise ValueError("Context inputs must be a dictionary")

        required_fields = [
            "ethnicity", "work_style", "collab_pattern", "tone_preference"
        ]
        evaluation = evaluate_input_completeness(context_inputs, required_fields)

        # Ensure all inputs are strings
        for field in required_fields:
            if field in context_inputs and not isinstance(context_inputs[field], str):
                context_inputs[field] = str(context_inputs[field])

        tone_profile = infer_learning_tone_profile(
            context_inputs.get("ethnicity", ""),
            context_inputs.get("work_style", ""),
            context_inputs.get("collab_pattern", ""),
            context_inputs.get("tone_preference", "")
        )

        if not isinstance(tone_profile, dict):
            raise ValueError("Invalid tone profile format")

        output = {
            "cultural_profile_tag": 
            f"{tone_profile.get('tone_style', 'balanced')} {context_inputs.get('collab_pattern', 'async')} communicator",
            "working_style_summary":
            f"Prefers {context_inputs.get('work_style', 'goal-focused')} execution with a {tone_profile.get('tone_style', 'balanced')} tone.",
            "cultural_delta":
            context_inputs.get("cultural_delta", "Wants a shift toward more expressive collaboration."),
            "org_fit_flags":
            context_inputs.get("org_fit_flags", "Prefers async-flat orgs"),
            "learning_tone_profile": tone_profile,
            "tone_example_phrases": tone_profile.get("tone_phrases", [])
        }

        formatted_output = format_for_agent(agent_name, output)
        output_fields = {
            "tone_style": tone_profile.get("tone_style", ""),
            "cultural_profile_tag": output.get("cultural_profile_tag", "")
        }
        store_memory(agent_name, user_id, session_id, "tone_inference",
                     context_inputs, formatted_output, output_fields=output_fields)
        log_agent_run(agent_name, context_inputs, formatted_output)

        explain = generate_why_this_output_summary(
            agent_name,
            str(context_inputs),
            rules_used=["cultural tone modeling", "learning preference theory"],
            model_confidence="medium-high")
        formatted_output["explanation"] = explain

        return formatted_output

    except Exception as e:
        log_error(agent_name, str(e))
        return {
            "error": str(e),
            "fallback": "Unable to generate tone profile at this time."
        }

def handle_user_feedback(agent_name,
                         content_id,
                         thumbs,
                         corrections=None,
                         notes=None):
    capture_user_feedback(thumbs, corrections, notes)
    return {"status": "feedback recorded"}
