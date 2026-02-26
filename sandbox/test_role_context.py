import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.skill_assessment_agent.role_context_agent.role_context_agent import analyze_role_context
from agents.skill_assessment_agent.role_context_agent.context_narrative import get_or_generate_role_context_narrative

async def test_role_context():
    # Test input
    test_input = {
        "title": "Senior Product Manager",
        "seniority": "Senior IC",
        "company": "Healthcare Tech Inc",
        "company_size": "5000+", 
        "domain": "Healthcare",
        "team_size": "8",
        "tenure": "3 years",
        "cross_functional_density": "high",
        "task_clusters": "platform strategy, vendor management, compliance",
        "effort_distribution": "40% strategy, 30% coordination, 30% execution"
    }

    print("\nTesting Role Context Agent...")
    context_output = await analyze_role_context(test_input, user_id="test_user", session_id="test_session")

    if "error" in context_output:
        print("Error:", context_output["error"])
        return

    print("\nRole Context Output:")
    print(context_output["role_context"])

    print("\nTesting Context Narrative...")
    narrative = get_or_generate_role_context_narrative(
        context_output["role_context"], 
        user_id="test_user",
        session_id="test_session"
    )
    print("\nNarrative Output:")
    print(narrative)

if __name__ == "__main__":
    asyncio.run(test_role_context())