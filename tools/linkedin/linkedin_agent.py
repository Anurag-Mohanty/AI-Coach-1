
"""
tools/linkedin/linkedin_agent.py – memory-free LinkedIn profile analyzer v1

♦ ROLE
    Pure LinkedIn profile analyzer for extracting AI interests and engagement signals.

♦ OUTPUT SHAPE  (should match a schema - we'll need to create one)
    {
        "ai_interests": [str, ...],
        "activity_level": str,  # "low/medium/high"
        "cross_signals": [str, ...],
        "influencers": [str, ...],
        "content_themes": [str, ...],
        "confidence": float (0-1)
    }

The function does **not** touch GlobalAgentMemory.  
Orchestrators decide where/when to store the result.
"""

import json
import re
from agent_core.agent_logger import log_agent_run, log_error
from agent_core.input_evaluation import evaluate_input_completeness
from agent_core.trust_explainability import generate_why_this_output_summary
from agent_core.compliance_utils import hash_input_data, log_data_usage_consent
from agent_core.llm_client import call_llm_model
from services.schema_loader import validate_payload


def remove_pii(text):
    """Basic cleanup: strip emails, phone numbers, etc."""
    text = re.sub(r'\S+@\S+', '[email]', text)
    text = re.sub(r'\+?\d[\d\- ]{8,}', '[phone]', text)
    return text.strip()


def analyze_linkedin_profile(
    user_id: str,
    session_id: str,
    profile_text: str
) -> dict:
    """
    Analyze a LinkedIn profile (raw or exported) to extract AI signals and interests.
    Pure function: **no memory reads/writes**.
    """
    
    try:
        # 1️⃣ Clean the input text
        if not profile_text or not profile_text.strip():
            raise ValueError("Profile text cannot be empty")
            
        cleaned_text = remove_pii(profile_text)

        # 2️⃣ Compliance logging
        _ = hash_input_data(cleaned_text)
        log_data_usage_consent(user_id)

        # 3️⃣ Build the prompt
        prompt = f"""
You are an AI career assistant. From the LinkedIn text below, extract:

1. AI-related interests or topics (like LLMs, AI safety, machine learning, data science)
2. Engagement level (posting, commenting, liking) → low/medium/high
3. Cross-signals (e.g., follows OpenAI, engages with AI content, shares AI articles)
4. AI influencers followed (e.g., Andrew Ng, Andrej Karpathy, Yann LeCun)
5. Content themes (e.g., career tips, tutorials, thought leadership, technical content)

Respond as a JSON object with keys:
- ai_interests: array of strings
- activity_level: string (low/medium/high)
- cross_signals: array of strings
- influencers: array of strings
- content_themes: array of strings

LinkedIn Profile:
{cleaned_text}
"""

        # 4️⃣ Call LLM
        response = call_llm_model(
            prompt=prompt,
            model="gpt-4",
            temperature=0.3,
            system_message="You are an expert AI career assistant analyzing LinkedIn profiles."
        )

        # 5️⃣ Parse the response
        try:
            parsed_response = json.loads(response)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse LLM response as JSON")

        # 6️⃣ Basic completeness check
        required = ["ai_interests", "activity_level", "cross_signals"]
        completeness = evaluate_input_completeness(parsed_response, required)
        
        # 7️⃣ Map to standardized output format
        payload = {
            "ai_interests": parsed_response.get("ai_interests", []),
            "activity_level": parsed_response.get("activity_level", "low"),
            "cross_signals": parsed_response.get("cross_signals", []),
            "influencers": parsed_response.get("influencers", []),
            "content_themes": parsed_response.get("content_themes", []),
            "confidence": 0.9 if completeness["is_complete"] else 0.6
        }

        # 8️⃣ Validate against schema (we'll need to create this schema)
        # validate_payload("user_linkedin_analysis.schema.json", payload)

        # 9️⃣ Self-explain and log
        explanation = generate_why_this_output_summary(
            agent_name="linkedin_agent",
            input_summary=cleaned_text[:200] + "..." if len(cleaned_text) > 200 else cleaned_text,
            rules_used=required,
            model_confidence=payload["confidence"],
        )
        log_agent_run(
            agent_name="linkedin_agent",
            user_id=user_id,
            session_id=session_id,
            explanation=explanation,
        )

        return payload

    except Exception as exc:
        log_error("linkedin_agent",
                  str(exc),
                  user_id=user_id,
                  session_id=session_id)
        # Return a schema-compliant stub so downstream still works
        fallback = {
            "ai_interests": [],
            "activity_level": "low", 
            "cross_signals": [],
            "influencers": [],
            "content_themes": [],
            "confidence": 0.0
        }
        # validate_payload("user_linkedin_analysis.schema.json", fallback)
        return fallback


# Optional placeholder for future downstream scoring
def score_linkedin_output(parsed_output):
    """Placeholder for tool_recommender/meta_agent to evaluate usefulness"""
    score = {
        "tool_signal_strength": len(parsed_output.get("ai_interests", [])),
        "influencer_alignment": len(parsed_output.get("influencers", [])) > 0,
        "activity_score": parsed_output.get("activity_level", "") in ["medium", "high"]
    }
    return score
