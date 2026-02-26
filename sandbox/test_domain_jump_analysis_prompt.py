
from agent_core.prompt_task_templates import get_task_template
from agent_core.prompt_builder import build_prompt_from_context
from agent_core.llm_client import call_llm_model
import json

def test_domain_jump_analysis():
    # 1. Load Template
    template = get_task_template("domain_jump_analysis")
    
    # 2. Test Input
    structured_input = {
        "current_domain": "healthcare",
        "target_domain": "adtech",
        "project_keywords": ["patient dashboard", "clinical workflows", "EHR integration"],
        "tools_used": ["Tableau", "SQL", "Python", "FHIR API"],
        "skills_from_resume": ["data analytics", "stakeholder management", "compliance"],
        "skills_from_linkedin": ["healthcare informatics", "project management"],
        "skills_by_use_case": {
            "adtech": [
                "real-time bidding",
                "campaign optimization",
                "audience segmentation"
            ]
        },
        "persona_context": {
            "tone": "analytical",
            "seniority": "senior",
            "goal": "transition to high-growth adtech"
        }
    }

    # 3. Build Prompt
    prompt_response = build_prompt_from_context(
        task="domain_jump_analysis",
        user_context=structured_input
    )

    print("\n=== Generated Prompt ===")
    print(prompt_response['prompt'])
    
    if prompt_response.get('missing_fields'):
        print("\n=== Missing Fields ===")
        print(prompt_response['missing_fields'])
        return

    # 4. Get LLM Response
    response = call_llm_model(prompt_response['prompt'])
    
    print("\n=== LLM Response ===")
    print(response)

    # 5. Validate JSON Response
    try:
        parsed = json.loads(response)
        print("\n=== Parsed Output ===")
        print(json.dumps(parsed, indent=2))
        
        # 6. Validate Required Fields
        required_fields = [
            "transferable_skills",
            "domain_specific_gaps", 
            "bridge_insight_summary",
            "suggested_mindset_shifts"
        ]
        
        missing = [field for field in required_fields if field not in parsed]
        if missing:
            print(f"\nWarning: Missing required fields: {missing}")
        
    except json.JSONDecodeError:
        print("Error: Response is not valid JSON")

if __name__ == "__main__":
    test_domain_jump_analysis()
