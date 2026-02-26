
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.skill_assessment_agent.tool_familiarity_agent.tool_familiarity_agent import infer_tool_familiarity

async def test_tool_familiarity_agent():
    print("\n=== Testing Tool Familiarity Agent ===")

    # Test case 1: Basic tool inference
    print("\nTest Case 1: Standard Tool Profile")
    test_user_id = "test_user"
    test_session_id = "test_session"

    # Mock context data
    mock_context = {
        "title": "Senior Product Manager",
        "tools_used": ["Jira", "Confluence", "Tableau", "Figma"],
        "task_clusters": ["Project Management", "Data Analysis", "Design", "Documentation"],
        "domain": "Healthcare"
    }

    # Store mock context in memory
    from agent_core.global_agent_memory import store_memory
    store_memory("global", test_user_id, test_session_id, None, "test_setup", {}, mock_context)

    try:
        result = await infer_tool_familiarity(
            user_id=test_user_id,
            session_id=test_session_id
        )
        
        formatted_result = result.get("output", result)
        
        # Store formatted result in global memory for view to access
        store_memory("tool_familiarity_agent", 
                    test_user_id, 
                    test_session_id, 
                    "tool_inference",
                    "infer_tool_familiarity",
                    {"title": "Senior Product Manager", "tools_used": ["Jira", "Confluence", "Tableau", "Figma"]},
                    formatted_result)

        print("\nTool Clusters:")
        for function, tools in formatted_result.get("tools_by_function", {}).items():
            print(f"\n{function}:")
            for tool in tools:
                print(f"- {tool}")
                depth = formatted_result.get("tool_depth_estimate", {}).get(tool, "unknown")
                print(f"  Depth: {depth}")
        
        print("\nAI Tools Detected:")
        for tool in formatted_result.get("ai_tools_detected", []):
            print(f"- {tool}")
            
        print(f"\nTool Maturity Score: {formatted_result.get('tool_maturity_score', 0)}%")
        print(f"Practitioner Profile: {formatted_result.get('tool_practitioner_profile', 'Unknown')}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_tool_familiarity_agent())
