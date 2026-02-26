import asyncio
from agent_core.global_agent_memory import store_memory, retrieve_memory
from agent_core.feedback_utils import store_feedback_locally
from agent_core.self_learning import log_learning_signal
from agent_core.input_evaluation import evaluate_input_completeness
from agent_core.trust_explainability import generate_why_this_output_summary
from agent_core.persona_context import get_user_context
from agent_core.downstream_formatter import format_for_agent
from agent_core.llm_client import call_llm_model

# Import child agents
from agents.skill_assessment_agent.resume.resume_agent import analyze_resume
from agents.skill_assessment_agent.linkedin.linkedin_agent import analyze_linkedin_profile
from agents.skill_assessment_agent.role_context_agent.role_context_agent import analyze_role_context
from agents.skill_assessment_agent.role_detail.role_detail_agent import infer_work_structure
from agents.skill_assessment_agent.tool_familiarity_agent.tool_familiarity_agent import infer_tool_familiarity
from agents.skill_assessment_agent.cultural_alignment_agent.cultural_alignment_agent import run_cultural_alignment_agent
from agents.skill_assessment_agent.aspiration_agent import interpret_aspiration

AGENT_SEQUENCE = [
    "ResumeAgent", "LinkedInAgent", "RoleContextAgent", "RoleDetailAgent",
    "ToolFamiliarityAgent", "CulturalAlignmentAgent", "AspirationAgent"
]

AGENT_FUNCTIONS = {
    "ResumeAgent": analyze_resume,
    "LinkedInAgent": analyze_linkedin_profile,
    "RoleContextAgent": analyze_role_context,
    "RoleDetailAgent": infer_work_structure,
    "ToolFamiliarityAgent": infer_tool_familiarity,
    "CulturalAlignmentAgent": run_cultural_alignment_agent,
    "AspirationAgent": interpret_aspiration
}

async def run_initial_orchestration(user_id: str, session_id: str, resume_data=None, linkedin_data=None, role_detail=None, role_context=None):
    completed = {}
    for agent in AGENT_SEQUENCE:
        try:
            if agent == "AspirationAgent":
                result = await interpret_aspiration(user_id, session_id, resume_data, linkedin_data, role_detail, role_context)
            elif agent == "CulturalAlignmentAgent":
                result = run_cultural_alignment_agent(user_id, session_id, {
                    "ethnicity": resume_data.get("ethnicity", ""),
                    "work_style": resume_data.get("work_style", ""),
                    "collab_pattern": resume_data.get("collab_pattern", ""),
                    "tone_preference": resume_data.get("tone_preference", "")
                })
            elif asyncio.iscoroutinefunction(AGENT_FUNCTIONS[agent]):
                result = await AGENT_FUNCTIONS[agent](user_id, session_id)
            else:
                result = AGENT_FUNCTIONS[agent](user_id)
            store_memory(agent, user_id, session_id, "skill_assessment", "run_initial_orchestration", {}, result)
            completed[agent] = result
        except Exception as e:
            print(f"Error in {agent}: {str(e)}")
    return completed

def get_data_for_screen(screen_id: str, user_id: str, session_id: str):
    data = retrieve_memory(screen_id, user_id, session_id, "skill_assessment")
    return data or {}

async def handle_user_update(agent_name: str, field: str, new_value: str, user_id: str, session_id: str):
    store_feedback_locally(agent_name, {"field": field, "new_value": new_value})

    if agent_name == "AspirationAgent":
        result = await interpret_aspiration(user_id, session_id, None, None, None, None)
    elif asyncio.iscoroutinefunction(AGENT_FUNCTIONS[agent_name]):
        result = await AGENT_FUNCTIONS[agent_name](user_id, session_id)
    else:
        result = AGENT_FUNCTIONS[agent_name](user_id)

    store_memory(agent_name, user_id, session_id, "skill_assessment", f"update_field_{field}", {}, result)
    return result

async def generate_summary(user_id: str, session_id: str):
    context = {}

    # Process each agent sequentially with proper async handling
    for agent in AGENT_SEQUENCE:
        try:
            memory = retrieve_memory(agent, user_id, session_id, "skill_assessment")
            if not memory:
                if agent == "AspirationAgent":
                    resume_data = context.get("ResumeAgent", {})
                    linkedin_data = context.get("LinkedInAgent", {})
                    role_detail = context.get("RoleDetailAgent", {})
                    role_context = context.get("RoleContextAgent", {})
                    memory = await interpret_aspiration(user_id, session_id, resume_data, linkedin_data, role_detail, role_context)
                elif agent == "RoleContextAgent":
                    memory = await analyze_role_context(user_id, session_id)
                elif agent == "ToolFamiliarityAgent":
                    memory = await infer_tool_familiarity(user_id, session_id)
                elif asyncio.iscoroutinefunction(AGENT_FUNCTIONS[agent]):
                    memory = await AGENT_FUNCTIONS[agent](user_id, session_id)
                else:
                    memory = AGENT_FUNCTIONS[agent](user_id)
            if memory:
                context[agent] = memory
        except Exception as e:
            print(f"Error in {agent}: {str(e)}")
            continue

    persona = get_user_context(user_id)

    prompt = f"""
You are an intelligent AI coach synthesizing a skill profile for a professional user.

Here is what we know:
{context}

Generate exactly **5 concise, high-signal bullets** that:
- Reflect true synthesis (not repetition of titles or roles)
- Provide new insights across task clusters, tool usage, org shape, and learning goals
- Include specific AI interests, task–tool pairings, or aspirational tension
- Sound clear, not robotic; confident but not overdone

Examples:
- You work across platform migration, vendor tools, and cost automation — but have limited exposure to real-time ML systems.
- You're confident using SQL and GA4, and you're beginning to explore LangChain and prompt engineering.
- Your org model is flat and cross-functional — with room to experiment.

Now generate 5 such bullets. Keep each line under 20 words.
"""

    response = call_llm_model(prompt=prompt)
    bullets = response.strip().split("\n")
    return {"summary": bullets, "persona": persona, "raw_context": context}