# pages/content_view.py

import streamlit as st
from agents.recommendation.content_recommender_agent import recommend_learning_content, handle_feedback

st.set_page_config(page_title="🎓 Content Recommender", layout="wide")
st.title("🎓 Content Recommender Agent")

st.markdown(
    "This agent recommends highly specific training content — based on your job-level use case, tools, and skill gaps."
)

# -----------------------------------------------
# 🔧 MOCKED FULL CONTEXT INPUTS (based on Agent I/O Map)
# -----------------------------------------------
mock_inputs = {
    "use_case": "Use AI to generate insight-ready slides for Monthly Business Review in healthcare claims",
    "tool_familiarity": ["GPT-4", "Tableau", "SQL"],
    "missing_skills": ["Prompt engineering", "Automation workflows"],
    "user_context": "Senior PM at a healthcare tech company",
    "domain": "Healthcare",
    "seniority": "Senior PM",
    "impact_scale": "Org-level reporting and decision support",
    "ai_literacy_signals": "Understands prompt chaining and retrieval but struggles with fine-tuning",
    "target_role_archetype": "Director of AI Product Management",
    "learning_objectives": "Be able to autonomously design and implement AI-powered reporting workflows",
    "recommended_use_cases": ["automated insight generation", "natural language SQL reporting", "workflow orchestration"],
    "modality_preference": ["Video", "Notebook"],
    "focused_subtask": "Summarize 10 Tableau dashboards into 6 stakeholder-ready insights for a Monthly Business Review using GPT"
}

if st.button("🚀 Run Content Recommender Agent", key="run_button"):
    with st.spinner("Thinking like an AI coach..."):
        results = recommend_learning_content(mock_inputs)

    for idx, item in enumerate(results):
        with st.container():
            st.subheader(f"#{idx + 1}: {item['title']}")
            st.markdown(f"**Link**: [{item['link']}]({item['link']})")
            st.markdown(f"**Source**: {item['source']} | **Format**: {item['format']}")
            st.markdown(f"**Score**: {item['score']}")
            st.markdown(f"**Why this?** {item['why']}")
            st.markdown(f"**Snippet**: {item['snippet']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Helpful", key=f"up_{idx}"):
                    handle_feedback(item['id'], True)
                    st.toast("Thanks for the feedback!", icon="✅")
            with col2:
                if st.button("👎 Not Helpful", key=f"down_{idx}"):
                    handle_feedback(item['id'], False)
                    st.toast("We’ll do better next time.", icon="⚠️")
