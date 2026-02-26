
import streamlit as st
import asyncio
from agents.recommendation_agent.content_recommendation.content_recommender_agent import recommend_learning_content, handle_feedback

st.set_page_config(
    page_title="🎓 Content Recommender",
    layout="wide",
    menu_items=None,
    initial_sidebar_state="collapsed"
)

# Configure dark theme
st.markdown("""
<style>
    .stApp {
        margin: 0;
        padding: 0;
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stButton button {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #464B5C;
    }
    .stTextInput input {
        background-color: #262730;
        color: #FAFAFA;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 Content Recommender Agent")

st.markdown("""
This agent recommends highly specific training content - based on your job-level use case, tools, and skill gaps.
It breaks down complex tasks into atomic queries and searches multiple sources.
""")

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

async def run_content_recommendation():
    st.info(f"🎯 Current Task: {mock_inputs['focused_subtask']}")

    with st.spinner("Running content search pipeline..."):
        results = await recommend_learning_content(mock_inputs)

        with st.expander("🔍 Search Process Steps", expanded=True):
            st.markdown("""
            1. Query Planning
            2. Multi-source Retrieval  
            3. Reflection & Filtering
            4. Scoring & Ranking
            """)

        st.subheader("🎯 Final Recommendations")
        for idx, item in enumerate(results):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    #### {idx+1}. {item['title']}
                    **Source**: {item['source']} | **Format**: {item['format']}
                    **Link**: [{item['link']}]({item['link']})

                    {item.get('why', '')}
                    """)
                with col2:
                    st.button("👍 Helpful", key=f"up_{idx}")
                    st.button("👎 Not Helpful", key=f"down_{idx}")

if st.button("🚀 Run Content Recommender Agent"):
    asyncio.run(run_content_recommendation())
