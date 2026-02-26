import streamlit as st
from agents.skill_assessment_agent.tool_familiarity_agent.tool_helpers import store_user_selected_tools, process_custom_tool_input, capture_tool_feedback
from agent_core.global_agent_memory import retrieve_memory

st.set_page_config(page_title="Tool Familiarity Confirmation", page_icon="🛠️")

st.title("🛠️ Confirm Your Familiar Tools")

user_id = st.session_state.get("user_id", "default_user")
session_id = st.session_state.get("session_id", "default_session")

# Retrieve inferred tools
tool_data = retrieve_memory("tool_familiarity_agent",
                            user_id,
                            session_id,
                            subtask_id="tool_inference")

if not tool_data:
    st.error("No tool suggestions found. Please complete earlier steps first.")
    st.stop()

selected_tools = {}
depth_estimates = {}

st.subheader("Suggested Tool Categories")

# Display tools by function
for function, tools in tool_data.get("tools_by_function", {}).items():
    with st.expander(f"🏁 {function}"):
        st.markdown("**Select tools you are familiar with:**")
        selected = st.multiselect("", tools, key=function)
        selected_tools[function] = selected

        if selected:
            for tool in selected:
                depth = st.selectbox(f"Depth of familiarity with {tool}:",
                                     ["Surface", "Regular", "Expert"],
                                     key=f"{function}_{tool}_depth")
                depth_estimates[tool] = depth

        # Feedback option
        feedback = st.radio(f"Was this category relevant?",
                            ["Thumbs Up", "Thumbs Down"],
                            key=f"{function}_feedback",
                            horizontal=True)
        if feedback == "Thumbs Down":
            notes = st.text_input(
                f"Optional: Suggest why {function} wasn't relevant",
                key=f"{function}_notes")
            capture_tool_feedback(user_id,
                                  session_id,
                                  category=function,
                                  thumbs_up=False,
                                  notes=notes)
        else:
            capture_tool_feedback(user_id,
                                  session_id,
                                  category=function,
                                  thumbs_up=True)

st.divider()

# Allow user to add custom tool
st.subheader("🌐 Add Your Own Tool")
custom_tool = st.text_input("If you use a tool not listed above, add it here:")
if st.button("Validate and Add Tool"):
    is_valid, corrected_tool = process_custom_tool_input(custom_tool)
    if is_valid:
        st.success(
            f"Tool '{corrected_tool}' added! Please confirm its familiarity below."
        )
        # Assume added to a new 'Custom Added' category
        if "Custom Added" not in selected_tools:
            selected_tools["Custom Added"] = []
        selected_tools["Custom Added"].append(corrected_tool)
        depth = st.selectbox(f"Depth of familiarity with {corrected_tool}:",
                             ["Surface", "Regular", "Expert"],
                             key=f"custom_{corrected_tool}_depth")
        depth_estimates[corrected_tool] = depth
    else:
        st.warning(
            "This input does not seem like a typical workflow tool. Please recheck."
        )

# Submit
if st.button("💾 Confirm Tool Familiarity"):
    store_user_selected_tools(user_id, session_id, selected_tools,
                              depth_estimates)
    st.success("Your tool familiarity has been saved!")
    st.balloons()
