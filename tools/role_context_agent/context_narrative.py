# context_narrative.py
# ----------------------
# This utility uses LLM prompting to convert structured JSON outputs from the Role Context Agent
# into a concise, user-facing bullet-point summary that feels informative and grounded.
# It avoids emotional tone and focuses on context-specific signals to guide downstream logic.
# It checks and stores narrative output using global agent memory so it can be reused across sessions.

import os
from openai import OpenAI
from agent_core.global_agent_memory import retrieve_memory, store_memory

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EXAMPLE_INPUT = {
    "contextualized_role_type": "Mid-to-senior IC PM with strong platform ownership",
    "org_shape_inference": "matrixed",
    "cross_functional_density": "very high",
    "ops_or_strategy_bias": "balanced with execution tilt",
    "ai_applicability_constraints": "moderate – constrained by regulatory and compliance complexity",
    "role_archetype_tag": "platform_compliance_ic",
    "upskilling_infra_quality": "high – access to internal L&D but requires self-direction",
    "training_access_signal": "needs manager approval, but budget exists",
    "recommendation_tone_flag": "focus on automation at team-level first",
    "collaboration_style": "hybrid",
    "work_setting": "hybrid",
    "impact_scope": "org-wide",
    "decision_making_maturity": "distributed"
}

EXAMPLE_OUTPUT = (
    "Based on the available context, we’ve inferred the following characteristics about your role:\n"
    "- You likely operate in a matrixed organization with distributed decision-making and org-wide impact.\n"
    "- Your cross-functional exposure appears high, with a collaboration style that leans hybrid.\n"
    "- The nature of your responsibilities suggests a balance between strategy and execution, with compliance shaping AI applicability.\n"
    "- Upskilling pathways exist but may require self-navigation or leadership support."
)

def get_or_generate_role_context_narrative(context: dict, user_id: str = "default_user", session_id: str = "default_session") -> str:
    try:
        cached = retrieve_memory(
            agent_name="role_context_agent",
            user_id=user_id,
            session_id=session_id,
            subtask_id="narrative"
        )
        if cached:
            return cached.get("narrative", "")

        prompt = f"""
You are an AI role analyst.
Your task is to summarize the user's inferred role context in a concise, fact-based format.
DO NOT use emotional language or compliments. Focus on context, not job tasks.
Avoid duplication with role detail outputs (e.g., tasks, responsibilities).
Respond with:
- One short intro sentence ("Based on the available context...")
- Then 3 to 4 specific bullet points that reflect the user's organizational reality (structure, exposure, bias, enablement)
Use the example to guide tone, length, and style.

Example Input:
{EXAMPLE_INPUT}

Example Output:
{EXAMPLE_OUTPUT}

Now generate the same for this user:
{context}

Respond only with the full paragraph block. Do not use markdown.
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You generate structured, objective bullet-style summaries from org context inferences."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        narrative = response.choices[0].message.content.strip()

        store_memory(
            agent_name="role_context_agent",
            user_id=user_id,
            session_id=session_id,
            subtask_id="narrative",
            function=prompt,
            input_fields=context,
            output_fields={"narrative": narrative}
        )

        return narrative

    except Exception:
        return "We encountered an issue generating your role context summary. Please review your inputs."
