"""
Role Detail Agent — Streamlit Test View
Location: /pages/role_detail_view.py

This page allows you to:
- Input role, resume, LinkedIn context
- Run the Role Detail Agent
- View structured output
- Preview downstream agent payloads
- Give feedback (thumbs up/down, notes)
"""

import streamlit as st
from agents.skill_assessment_agent.role_detail.role_detail_agent import infer_work_structure
from agent_core.feedback_utils import capture_user_feedback
from agent_core.agent_logger import log_agent_run

st.set_page_config(page_title="Role Details", layout="wide")
st.title("📋 Role Details Agent")

# Input fields
input_data = {
    "role": st.text_input("Role Title", "Senior Product Manager"),
    "resume": st.text_area("Resume Text (Optional)"),
    "linkedin": st.text_area("LinkedIn Text (Optional)"),
    "role_context": st.text_area("Role Context (Optional, JSON format)")
}

# Add aspiration selector
aspiration = st.radio(
    "What's your goal for the next 6-12 months?",
    ["Get promoted", "Switch domains", "Lateral move", "AI upskilling"]
)

if st.button("🔍 Analyze Role Details", type="primary", use_container_width=True):
    with st.spinner("Analyzing role details..."):
        try:
            work_structure = infer_work_structure(
                role=input_data["role"],
                resume=input_data["resume"],
                linkedin=input_data["linkedin"],
                role_context=input_data["role_context"],
                aspiration=aspiration
            )

            if isinstance(work_structure, dict):
                st.json(work_structure)
            else:
                st.json({"analysis": work_structure})

            # Feedback section
            st.markdown("### Was this analysis helpful?")
            col1, col2 = st.columns([1, 3])
            with col1:
                feedback = st.radio("Rating", ["👍", "👎"], key="feedback")
            with col2:
                if feedback == "👎":
                    st.text_input("What could be improved?", key="feedback_text")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
else:
    st.info("Enter your role details and click Analyze to begin.")