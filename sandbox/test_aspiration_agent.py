import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.skill_assessment_agent.aspiration_agent import interpret_aspiration, process_custom_aspiration

async def test_aspiration_agent():
    print("\n=== Testing Aspiration Agent ===")

    # Test case 1: Basic career trajectory
    print("\nTest Case 1: Standard Career Path")
    mock_resume = {
        "title": "Senior Product Manager",
        "company": "HealthTech Inc",
        "domain": "Healthcare", 
        "experience": "5 years"
    }
    mock_linkedin = {
        "endorsements": ["Product Strategy", "Healthcare IT", "Team Leadership"],
        "recent_activity": "Leading cross-functional teams"
    }
    mock_role_detail = {
        "responsibilities": ["Product roadmap", "Stakeholder management"],
        "team_size": 5
    }
    mock_role_context = {
        "company_type": "Enterprise",
        "growth_stage": "Scale-up"
    }

    try:
        result = await interpret_aspiration(
            user_id="test_user",
            session_id="test_session",
            resume_data=mock_resume,
            linkedin_data=mock_linkedin,
            role_detail=mock_role_detail,
            role_context=mock_role_context
        )
        print("\nOutput structure:")
        if result.get("realistic_trajectory_options"):
            print("\nSuggested career paths:")
            for option in result["realistic_trajectory_options"]:
                print(f"- {option}")
        else:
            print("No career path suggestions found")
        print("\nFull output:")
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")

    # Test case 2: Domain switch aspiration
    print("\nTest Case 2: Domain Switch")
    mock_resume["domain"] = "Finance"
    result = await interpret_aspiration(
        user_id="test_user_2",
        session_id="test_session_2",
        resume_data=mock_resume,
        linkedin_data=mock_linkedin,
        role_detail=mock_role_detail,
        role_context=mock_role_context
    )
    if result:
        print("\nCareer Path Options:")
        for option in result.get("realistic_trajectory_options", []):
            print(f"- {option}")
        print(f"\nRealism Score: {result.get('realism_score', 0)}")
        print(f"Summary: {result.get('role_delta_summary', '')}")


    # Test case 3: Custom aspiration processing
    print("\nTest Case 3: Custom Aspiration")
    custom_input = "I want to transition into AI product management while leveraging my healthcare background"
    is_valid, output, details = process_custom_aspiration(
        custom_input,
        user_id="test_user_3",
        session_id="test_session_3"
    )
    if details:
        print("\nValidation Details:")
        print(f"Valid: {details.get('valid', False)}")
        print(f"Explanation: {details.get('explanation', '')}")

import asyncio

async def main():
    await test_aspiration_agent()

if __name__ == "__main__":
    asyncio.run(main())