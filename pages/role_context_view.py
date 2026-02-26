import streamlit as st
from agents.skill_assessment_agent.role_context_agent.role_context_agent import analyze_role_context
from agents.skill_assessment_agent.role_context_agent.context_narrative import get_or_generate_role_context_narrative
import asyncio

st.set_page_config(page_title="Role Context", layout="wide")
st.title("🔍 Role Context Agent")

# =============================
# 📋 INPUT SECTION
# =============================
st.subheader("📋 Enter Your Role Details")

input_data = {
    "title": st.text_input("Role Title", "Senior Product Manager"),
    "seniority": st.selectbox("Seniority", ["Junior", "Mid", "Senior IC", "Lead"]),
    "company": st.text_input("Company", "Healthcare Tech Inc"),
    "company_size": st.text_input("Company Size", "5000+"),
    "domain": st.text_input("Domain", "Healthcare"),
    "team_size": st.text_input("Team Size", "8"),
    "tenure": st.text_input("Tenure", "3 years"),
    "cross_functional_density": st.selectbox("Cross-functional Density", ["low", "medium", "high", "very high"]),
    "task_clusters": st.text_input("Task Clusters", "platform strategy, vendor management, compliance"),
    "effort_distribution": st.text_input("Effort Distribution", "40% strategy, 30% coordination, 30% execution")
}

if st.button("🔍 Analyze Role Context", type="primary", use_container_width=True):
    with st.spinner("Analyzing your role context..."):
        try:
            context_output = asyncio.run(analyze_role_context(input_data, user_id="test_user", session_id="test_session"))

            if "error" in context_output:
                st.error(f"Analysis Error: {context_output['error']}")
            else:
                tabs = st.tabs(["🧠 Analysis", "➡️ Downstream Preview", "📝 Feedback"])

                with tabs[0]:
                    st.subheader("📊 Context Analysis")
                    st.json(context_output["full_output"])

                    if "narrative" in context_output:
                        st.markdown("### 📝 Context Narrative")
                        st.markdown(context_output["narrative"])

                with tabs[1]:
                    st.markdown("### 🔄 Feeds into:")
                    for agent_name, payload in context_output.get("downstream_payloads", {}).items():
                        with st.expander(f"→ {agent_name.replace('_', ' ').title()}"):
                            st.json(payload)

                with tabs[2]:
                    st.markdown("### 💬 Was this analysis helpful?")
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        feedback = st.radio("Rating", ["👍", "👎"], key="feedback")
                    with col2:
                        if feedback == "👎":
                            st.text_input("What could be improved?", key="improvement")
                            if st.button("Submit Feedback"):
                                st.success("Thank you for helping us improve!")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
else:
    st.info("Enter your role details and click Analyze to begin.")