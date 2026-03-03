
import os
import json
from openai import OpenAI
from typing import Dict, Any
from agent_core.input_evaluation import evaluate_input_completeness
from agent_core.agent_logger import log_agent_run, log_error
from agent_core.timing_utils import timed_function

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_prompt(inputs: dict) -> str:
    """Build prompt from inputs"""
    return f"""
You are an expert in organizational role profiling.

Analyze the following user role:
- Title: {inputs.get('title', 'Not specified')}
- Seniority: {inputs.get('seniority', 'Not specified')}
- Company: {inputs.get('company', 'Not specified')}
- Company Size: {inputs.get('company_size', 'Not specified')}
- Domain: {inputs.get('domain', 'Not specified')}
- Team Size: {inputs.get('team_size', 'Not specified')}
- Tenure: {inputs.get('tenure', 'Not specified')}
- Cross-functional Exposure: {inputs.get('cross_functional_density', 'Not specified')}
- Task Clusters: {inputs.get('task_clusters', 'Not specified')}
- Effort Distribution: {inputs.get('effort_distribution', 'Not specified')}

Please analyze the role and return a JSON object with these fields:
- contextualized_role_type: Specific description of role type
- org_shape_inference: Organization structure (flat/hierarchical/matrix)
- cross_functional_density: Level of cross-team work (low/medium/high)
- ops_or_strategy_bias: Balance between operations and strategy
- ai_applicability_constraints: Any limitations for AI adoption
- role_archetype_tag: Role classification tag
- confidence_score: Analysis confidence (0.0-1.0)
- reasoning_log: Explanation of analysis

Format the response as a valid JSON object."""

@timed_function("role_context_agent")
async def analyze_role_context(input_bundle: Dict[str, Any], user_id: str = "default_user", session_id: str = "default_session") -> Dict[str, Any]:
    """Main function to analyze role context"""
    try:
        # Validate required fields
        required_fields = ["title", "company", "domain"]
        input_eval = evaluate_input_completeness(input_bundle, required_fields)
        if input_eval.get("missing_fields"):
            return {"error": f"Missing required inputs: {input_eval['missing_fields']}"}

        # Generate completion
        messages = [
            {"role": "system", "content": "You are an organizational context analyst."},
            {"role": "user", "content": build_prompt(input_bundle)}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.3
        )

        try:
            result = response.choices[0].message.content.strip()
            structured_output = json.loads(result)
            log_agent_run("role_context_agent", input_bundle, structured_output)
            
            return {
                "full_output": structured_output,
                "role_context": structured_output,
                "downstream_payloads": {
                    "skill_delta_agent": structured_output,
                    "use_case_miss_agent": structured_output,
                    "role_ladder_agent": structured_output
                }
            }
            
        except json.JSONDecodeError as e:
            log_error("role_context_agent", f"JSON parse error: {str(e)}")
            return {"error": f"Failed to parse response: {str(e)}"}

    except Exception as e:
        log_error("role_context_agent", str(e))
        return {"error": f"Analysis failed: {str(e)}"}
