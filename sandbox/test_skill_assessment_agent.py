import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.skill_assessment_agent.skill_assessment_agent import run_initial_orchestration, get_data_for_screen, handle_user_update, generate_summary

async def test_skill_assessment_agent():
    print("\n=== Testing Skill Assessment Agent ===")

    # Test case setup
    test_user_id = "test_user"
    test_session_id = "test_session"
    resume_data = {} # Placeholder
    linkedin_data = {} # Placeholder
    role_detail = {} # Placeholder
    role_context = {} # Placeholder

    # Test 1: Initial Orchestration
    print("\nTest 1: Initial Orchestration")
    try:
        completed = await run_initial_orchestration(test_user_id, test_session_id, resume_data, linkedin_data, role_detail, role_context)
        print("Completed agents:", list(completed.keys()))
    except Exception as e:
        print(f"Error in initial orchestration: {str(e)}")

    # Test 2: Screen Data Retrieval
    print("\nTest 2: Screen Data Retrieval")
    try:
        resume_data = get_data_for_screen("ResumeAgent", test_user_id, test_session_id)
        print("Resume data retrieved:", bool(resume_data))
    except Exception as e:
        print(f"Error retrieving screen data: {str(e)}")

    # Test 3: User Update Handling
    print("\nTest 3: User Update Handling")
    try:
        await handle_user_update(
            agent_name="ResumeAgent",
            field="title",
            new_value="Senior Product Manager",
            user_id=test_user_id,
            session_id=test_session_id
        )
        print("User update handled successfully")
    except Exception as e:
        print(f"Error handling user update: {str(e)}")

    # Test 4: Summary Generation
    print("\nTest 4: Summary Generation")
    try:
        summary = await generate_summary(test_user_id, test_session_id)
        print("\nGenerated Summary:")
        for bullet in summary.get("summary",[]): #handle potential missing key
            print(f"- {bullet}")
    except Exception as e:
        print(f"Error generating summary: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_skill_assessment_agent())