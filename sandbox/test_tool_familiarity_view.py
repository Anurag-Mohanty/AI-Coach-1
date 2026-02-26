
import streamlit as st
from agents.skill_assessment_agent.tool_familiarity_agent.tool_familiarity_agent import infer_tool_familiarity
from agent_core.global_agent_memory import store_memory, retrieve_memory

async def main():
    # Test user context
    test_user_id = "test_user"
    test_session_id = "test_session"

    # Set up test data
    mock_context = {
        "title": "Senior Product Manager",
        "tools_used": ["Jira", "Confluence", "Tableau", "Figma"],
        "task_clusters": ["Project Management", "Data Analysis", "Design", "Documentation"],
        "domain": "Healthcare"
    }

    # Store mock context
    store_memory("global", test_user_id, test_session_id, None, "test_setup", {}, mock_context)

    # Run tool familiarity agent
    result = await infer_tool_familiarity(
        user_id=test_user_id,
        session_id=test_session_id
    )

    # Display the view
    st.title("🛠️ Test Tool Familiarity View")
    
    # Retrieve and display tool data
    tool_data = retrieve_memory("tool_familiarity_agent",
                              test_user_id,
                              test_session_id,
                              subtask_id="tool_inference")

    if tool_data:
        st.success("Test data loaded successfully!")
        st.json(tool_data)
    else:
        st.error("No tool suggestions found. Please check memory storage.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
import streamlit as st
from agent_core.global_agent_memory import store_memory

def setup_mock_data():
    # Test user context
    test_user_id = "test_user"
    test_session_id = "test_session"

    # Mock tool familiarity data that matches the agent output
    mock_tool_data = {
        "tools_by_function": {
            "General Productivity": ["Microsoft Office", "Google Suite"],
            "Project Management": ["Trello", "Asana"],
            "Collaboration": ["Slack", "Zoom"],
            "Analytics": ["Google Analytics", "Tableau"]
        },
        "ai_tools_detected": ["Google Suite", "Asana", "Slack", "Google Analytics"],
        "initial_tool_depth_estimate": {
            "Microsoft Office": "expert",
            "Google Suite": "regular",
            "Trello": "surface",
            "Asana": "surface",
            "Slack": "regular",
            "Zoom": "expert",
            "Google Analytics": "surface",
            "Tableau": "surface"
        },
        "tool_maturity_score": 50,
        "tool_practitioner_profile": "Pragmatic"
    }

    # Store mock data in memory
    store_memory("tool_familiarity_agent",
                 test_user_id,
                 test_session_id,
                 "tool_inference",
                 "test_setup",
                 {},
                 mock_tool_data)

    # Set session state for user ID and session
    st.session_state["user_id"] = test_user_id
    st.session_state["session_id"] = test_session_id

    return mock_tool_data

def main():
    st.title("🛠️ Test Tool Familiarity View")
    
    # Setup mock data
    mock_data = setup_mock_data()
    
    # Display the mock data that was stored
    st.success("✅ Test data loaded successfully!")
    st.json(mock_data)

if __name__ == "__main__":
    main()
