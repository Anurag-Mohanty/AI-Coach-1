"""
tools/resume/resume_agent.py   –  memory-free extractor v1

♦ ROLE
    Pure capability extractor for a user résumé.

♦ OUTPUT SHAPE  (must match user_current_capabilities.schema.json)
    {
        "skills":    [str, …],
        "tools":     [str, …],
        "roles":     [str, …],
        "confidence": float (0-1)
    }

The function does **not** touch GlobalAgentMemory.  
Orchestrators decide where/when to store the result.
"""

import os
from agent_core.agent_logger import log_agent_run, log_error
from agent_core.input_evaluation import evaluate_input_completeness
from agent_core.trust_explainability import generate_why_this_output_summary

from agent_core.compliance_utils import hash_input_data, log_data_usage_consent

# your existing helpers
from tools.resume.resume_parser import extract_text_from_file
from tools.resume.resume_utils import extract_all_fields

# new: schema validation helper
from services.schema_loader import validate_payload


# ---------------------------------------------------------------------------
def analyze_resume(
    user_id: str,
    session_id: str,
    resume_file: str | None = None,
    resume_text: str | None = None,
) -> dict:
    """
    Extract structured skills, tools, and roles from a résumé.
    Pure function: **no memory reads/writes**.
    """

    try:
        # 1️⃣  Parse raw text
        if resume_text:
            raw_text = resume_text
        elif resume_file:
            # Handle both file paths and file objects
            if hasattr(resume_file, 'name'):
                raw_text = extract_text_from_file(resume_file)
            else:
                raw_text = extract_text_from_file(resume_file)
        else:
            raise ValueError("Either resume_text or resume_file must be provided")

        # 2️⃣  Compliance logging (unchanged)
        _ = hash_input_data(raw_text)
        log_data_usage_consent(user_id)

        # 3️⃣  Field extraction
        extracted = extract_all_fields(raw_text)

        if not extracted:
            raise ValueError("Failed to extract fields from résumé")

        # 4️⃣  Basic completeness check (unchanged)
        required = ["title", "seniority", "tools"]
        completeness = evaluate_input_completeness(extracted, required)
        if not completeness["is_complete"]:
            raise ValueError(
                f"Missing fields: {completeness['missing_fields']}")

        # 5️⃣  Map → Current-Capabilities contract
        payload = {
            "skills":
            extracted.get("ai_keywords", []) or extracted.get("skills", []),
            "tools":
            extracted.get("tools", []),
            "roles": [extracted.get("title", "")],
            "confidence":
            0.9 if completeness["is_complete"] else 0.6,
        }

        # 6️⃣  Validate against schema  ✅
        validate_payload("user_current_capabilities.schema.json", payload)

        # 7️⃣  (Optional) Self-explain – keeps your rich prompt intact
        explanation = generate_why_this_output_summary(
            agent_name="resume_agent",
            input_summary=raw_text[:200] + "..." if len(raw_text) > 200 else raw_text,
            rules_used=required,
            model_confidence=payload["confidence"],
        )
        log_agent_run(
            agent_name="resume_agent",
            user_id=user_id,
            session_id=session_id,
            explanation=explanation,
        )

        return payload

    except Exception as exc:
        log_error("resume_agent",
                  str(exc),
                  user_id=user_id,
                  session_id=session_id)
        # Return a schema-compliant stub so downstream still works
        fallback = {"skills": [], "tools": [], "roles": [], "confidence": 0.0}
        validate_payload("user_current_capabilities.schema.json", fallback)
        return fallback
