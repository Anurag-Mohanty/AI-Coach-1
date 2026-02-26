import os
import json
from datetime import datetime, timezone
from openai import OpenAI
from typing import Dict, Any

from agent_core.input_evaluation import evaluate_input_completeness
from agent_core.agent_logger import log_agent_run, log_error
from agent_core.feedback_utils import capture_user_feedback
from agent_core.downstream_formatter import format_for_agent
from agent_core.trust_explainability import generate_why_this_output_summary
import sys
import traceback

from agent_core.global_agent_memory import store_memory
from agent_core.prompt_builder import build_prompt_from_context
from agent_core.llm_client import call_llm_model

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def infer_work_structure(role: str, resume: str = None, linkedin: str = None, 
                        role_context: str = None, aspiration: str = None, 
                        user_id: str = "default_user") -> dict:
    """Main interface for Role Detail Agent"""
    try:
        inputs = {
            "role": role,
            "resume": resume,
            "linkedin": linkedin,
            "role_context": role_context,
            "aspiration": aspiration,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Build prompt using template
        prompt_package = build_prompt_from_context(
            task="role_detail_analysis",
            user_context=inputs
        )

        if prompt_package.get("missing_fields"):
            log_error("role_detail_agent", f"Missing fields: {prompt_package['missing_fields']}")
            return {"error": f"Missing required inputs: {prompt_package['missing_fields']}"}

        # Call LLM using utility
        response = call_llm_model(
            prompt_package["prompt"],
            model_params={"temperature": 0.4}
        )

        full_output = json.loads(response)

        # Format for downstream agents
        downstream_payloads = {
            "skill_delta_agent": format_for_agent("skill_delta_agent", full_output),
            "domain_jump_agent": format_for_agent("domain_jump_agent", full_output),
            "role_ladder_agent": format_for_agent("role_ladder_agent", full_output)
        }

        # Generate explanation
        explanation = generate_why_this_output_summary(
            agent_name="role_detail_agent",
            input_summary="Role structure inference based on provided context",
            rules_used=["task clustering", "work pattern analysis"],
            model_confidence=0.85
        )

        # Log run
        log_agent_run("role_detail_agent", inputs, full_output)

        return {
            "full_output": full_output,
            "downstream_payloads": downstream_payloads,
            "explanation": explanation
        }

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in role_detail_agent: {error_trace}", file=sys.stderr)
        log_error("role_detail_agent", str(e))
        return {"error": f"Processing error: {str(e)}"}

def extract_focus_topic_from_role(role_details):
    """Extract a focus topic from role details for tone prompting"""
    try:
        if isinstance(role_details, dict):
            # Try to find the most relevant topic from task clusters
            if "task_clusters" in role_details:
                return role_details["task_clusters"][0]
            # Fallback to any domain info
            elif "domain" in role_details:
                return f"work in {role_details['domain']}"
    except Exception:
        pass
    
    return "explaining a concept to a team"