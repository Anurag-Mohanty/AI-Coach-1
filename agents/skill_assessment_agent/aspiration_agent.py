import json
from agent_core.agent_logger import log_agent_run, log_error
from agent_core.global_agent_memory import store_memory, retrieve_memory
from agent_core.input_evaluation import evaluate_input_completeness
from agent_core.self_learning import learn_from_feedback
from agent_core.downstream_formatter import format_for_agent
from agent_core.feedback_utils import capture_user_feedback
from agent_core.trust_explainability import generate_why_this_output_summary
from agent_core.persona_context import update_shared_context
from agent_core.timing_utils import timed_function
from openai import OpenAI

client = OpenAI()

@timed_function("aspiration_agent", display=True)
def interpret_aspiration(user_id, session_id, resume_data, linkedin_data, role_detail, role_context):
    agent_name = "aspiration_agent"
    try:
        existing = retrieve_memory(agent_name, user_id, session_id, "aspiration_analysis")
        if existing:
            return existing

        required_inputs = {
            "resume_data": resume_data,
            "linkedin_data": linkedin_data,
            "role_detail": role_detail,
            "role_context": role_context
        }
        evaluate_input_completeness(required_inputs, required_fields=list(required_inputs.keys()))

        example_output = {
            "target_role_archetype": "IC4 - Senior Product Manager",
            "aspiration_category": "Grow in domain + begin leadership",
            "role_delta_summary": "Needs AI upskilling and team coordination experience",
            "domain_shift_signal": False,
            "risk_of_misalignment": "No leadership signals in resume",
            "aspiration_cluster": "AI-focused mid-career PMs",
            "realism_score": 0.87,
            "reflective_prompt": "Would you consider switching to platform product leadership?",
            "realistic_trajectory_options": [
                "Grow into Senior Product Manager in current org",
                "Lateral move into AI-focused product team",
                "Begin managing a small cross-functional team",
                "Lead a high-impact platform initiative",
                "Switch to platform strategy or technical PM role"
            ]
        }

        prompt = f"""
You are a career counselor helping a user define what they can realistically do or aspire to achieve in the next 2–3 years.
Your job is to consider their current title, company type, domain, responsibilities, skills, and context — then suggest the **5 most realistic, achievable career directions** they could take.
If the user’s trajectory is uncertain, include options like lateral moves, adjacent domains, deeper specialization, or selective high-risk pivots like founding a company.

## FORMAT:
Return a structured JSON like this:
{json.dumps(example_output, indent=2)}

## ACTUAL USER CONTEXT:
Resume: {resume_data}
LinkedIn: {linkedin_data}
Role Detail: {role_detail}
Role Context: {role_context}

Be realistic, helpful, and insightful. Focus on goals that are reasonably achievable based on the user’s trajectory. Return only the structured JSON.
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a career counselor returning structured career goal insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
        )

        raw_output = response.choices[0].message.content.strip()
        try:
            output = json.loads(raw_output)
        except:
            # Handle non-JSON output
            output = {
                "target_role_archetype": "Senior Product Manager",
                "aspiration_category": "Grow in domain",
                "role_delta_summary": "Needs to build more cross-functional experience",
                "domain_shift_signal": False,
                "risk_of_misalignment": "Low",
                "aspiration_cluster": "Growth-focused PMs",
                "realism_score": 0.8,
                "reflective_prompt": "Consider expanding scope to platform products",
                "realistic_trajectory_options": [
                    "Technical Track: Lead platform/infrastructure products",
                    "People Track: Build and manage a product team",
                    "Domain Track: Become healthcare domain expert",
                    "Innovation Track: Lead emerging tech initiatives",
                    "Strategic Track: Drive product vision and roadmap"
                ]
            }

        formatted_output = output

        store_memory(
            agent_name=agent_name,
            user_id=user_id,
            session_id=session_id,
            subtask_id="aspiration_analysis",
            function="interpret_aspiration",
            input_fields=required_inputs,
            output_fields=formatted_output
        )

        update_shared_context(user_id, {
            "aspiration_cluster": output.get("aspiration_cluster"),
            "target_role": output.get("target_role_archetype")
        })

        log_agent_run(agent_name, required_inputs, formatted_output)
        return formatted_output

    except Exception as e:
        log_error(agent_name, str(e))
        return {
            "error": f"Aspiration Agent failed: {str(e)}"
        }

def process_custom_aspiration(user_input, user_id, session_id):
    agent_name = "aspiration_agent"
    try:
        validation_prompt = f"""
You are a career development coach helping validate custom user-submitted career goals.
The user wrote: \"{user_input}\"

Return JSON with:
- valid: true/false (whether this goal is actionable within a tech/AI-driven platform)
- explanation: why it's valid or not
- suggestions: if invalid, how to revise
- parsed_output: if valid, structure it like aspiration_agent output (same fields)
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You validate and translate user-submitted goals into structured career outputs."},
                {"role": "user", "content": validation_prompt}
            ],
            temperature=0.3,
        )
        parsed = json.loads(response.choices[0].message.content.strip())
        if parsed.get("valid"):
            structured = {
                "target_role_archetype": parsed["parsed_output"].get("target_role_archetype"),
                "aspiration_category": parsed["parsed_output"].get("aspiration_category"),
                "role_delta_summary": parsed["parsed_output"].get("role_delta_summary"),
                "domain_shift_signal": parsed["parsed_output"].get("domain_shift_signal", False),
                "risk_of_misalignment": parsed["parsed_output"].get("risk_of_misalignment"),
                "aspiration_cluster": parsed["parsed_output"].get("aspiration_cluster"),
                "realism_score": parsed["parsed_output"].get("realism_score", 0.0),
                "reflective_prompt": parsed["parsed_output"].get("reflective_prompt"),
                "realistic_trajectory_options": parsed["parsed_output"].get("realistic_trajectory_options", [])
            }
            store_memory(
                agent_name=agent_name,
                user_id=user_id,
                session_id=session_id,
                subtask_id="custom_aspiration",
                function="process_custom_aspiration",
                input_fields={"user_input": user_input},
                output_fields=structured
            )
            return True, structured, ""
        else:
            return False, None, parsed
    except Exception as e:
        return False, None, {"error": str(e)}

def store_user_selected_aspirations(chosen_options, user_id, session_id):
    agent_name = "aspiration_agent"
    try:
        payload = {
            "selected_aspirations": chosen_options,
            "summary": "In the next 2–3 years, user wants to: " + "; ".join(chosen_options)
        }
        store_memory(
            agent_name=agent_name,
            user_id=user_id,
            session_id=session_id,
            subtask_id="user_selected_aspirations",
            function="store_user_selected_aspirations",
            input_fields={"selected": chosen_options},
            output_fields=payload
        )
        return True
    except Exception as e:
        log_error(agent_name, f"Failed to store selected aspirations: {e}")
        return False