
import streamlit as st
import asyncio
from agent_core.global_agent_memory import retrieve_memory
from agents.skill_assessment_agent.aspiration_agent import interpret_aspiration, process_custom_aspiration
import json

st.set_page_config(page_title="Career Aspiration", layout="wide")
st.title("🎯 Define Your Career Aspiration")

user_id = st.session_state.get("user_id", "demo_user")
session_id = st.session_state.get("session_id", "demo_session")

resume_data = st.session_state.get("resume_data", {})
linkedin_data = st.session_state.get("linkedin_data", {})
role_detail = st.session_state.get("role_detail", {})
role_context = st.session_state.get("role_context", {})

async def get_aspiration():
    with st.spinner("Analyzing your career trajectory..."):
        return await interpret_aspiration(user_id, session_id, resume_data, linkedin_data, role_detail, role_context)

if 'result' not in st.session_state:
    st.session_state.result = asyncio.run(get_aspiration())

result = st.session_state.result

if "error" in result:
    st.error(result["error"])
    st.stop()

st.subheader("🔍 Based on your profile, here are 5 realistic directions you might pursue:")

suggested_options = result.get("realistic_trajectory_options", [])
chosen_options = st.session_state.get("chosen_aspirations", [])

cols = st.columns(3)
for i, option in enumerate(suggested_options):
    with cols[i % 3]:
        if st.button(option):
            if option not in chosen_options and len(chosen_options) < 3:
                chosen_options.append(option)
                st.session_state["chosen_aspirations"] = chosen_options

if chosen_options:
    st.markdown("### ✅ In the next 2–3 years, I want to:")
    for item in chosen_options:
        st.markdown(f"- {item}")

st.markdown("---")
st.markdown("If none of these reflect your direction, describe it in your own words:")
user_input = st.text_area("Your custom career goal")

if st.button("Submit My Custom Aspiration") and user_input:
    with st.spinner("Validating your custom goal..."):
        is_valid, output, details = process_custom_aspiration(user_input, user_id, session_id)
        if is_valid:
            st.session_state["custom_aspiration"] = output
            st.success("✅ Custom goal accepted and stored!")
            st.json(output)
        else:
            if "error" in details:
                st.error(f"Validation failed: {details['error']}")
            else:
                st.warning("⚠️ This goal may not align with platform capabilities:")
                st.markdown(f"**Reason:** {details.get('explanation')}")
                st.markdown("**Suggestions:**")
                for s in details.get("suggestions", []):
                    st.markdown(f"- {s}")
