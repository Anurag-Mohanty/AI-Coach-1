import streamlit as st
import asyncio
from agents.recommendation_agent.learning_path.learning_path_agent import recommend_learning_path

st.set_page_config(page_title="🎯 Learning Path", layout="wide")

async def generate_path():
    mock_input = {
        "persona": {
            "role": "Senior Product Manager",
            "domain": "Healthcare",
            "impact_scale": "Org-wide"
        },
        "aspiration": {
            "aspiration_category": "switch",
            "target_role_archetype": "AI Product Manager",
            "target_company": "Google"
        },
        "subtask": {
            "title": "Design stakeholder-facing dashboards powered by GPT",
            "description": "Structure GPT outputs and embed them in dashboards using Streamlit or Tableau"
        }
    }
    return await recommend_learning_path(mock_input)

def display_intro(intro_text):
    sections = intro_text.split('\n\n')
    intro = sections[0].replace("👋 Introduction\n", "")
    why_subtask = sections[1].replace("📌 Why This Subtask Matters\n", "") if len(sections) > 1 else ""

    st.markdown("### 👋 Introduction") 
    st.write(intro)

    if why_subtask:
        st.markdown("### 📌 Why This Subtask Matters")
        st.write(why_subtask)

def display_gaps(gaps_text):
    st.markdown("### 🧠 Skill Gaps to Address")
    sections = gaps_text.strip().split('\n\n')
    
    if len(sections) > 0:
        # Display opening context
        context = sections[0].replace("🧠 Skill Gaps to Address\n", "")
        st.write(context)

        # Display skill gaps list if present
        if len(sections) > 1:
            st.write("These include:")
            for skill in sections[1].split('\n'):
                if skill.strip():
                    st.markdown(f"- {skill.strip()}")

def display_learning_steps(steps):
    st.markdown("### 🛠️ Your Step-by-Step Learning Journey")
    steps_list = steps.split('\n\n')

    for step in steps_list:
        if step.startswith('▶️'):
            lines = step.split('\n')
            title = lines[0]
            with st.expander(title, expanded=True):
                content = []
                for line in lines[1:]:
                    if line.startswith('🧠'):
                        st.markdown("---")
                        st.markdown(line)
                    else:
                        content.append(line)
                st.markdown('\n'.join(content))

def display_next_steps(cta_text):
    st.markdown("### ✅ Ready to Begin?")
    st.write(cta_text.replace("✅ Ready to Begin?\n", ""))

if st.button("Generate Learning Path", type="primary"):
    with st.spinner("Generating personalized learning path..."):
        result = asyncio.run(generate_path())

        if isinstance(result, dict) and "learning_path_narrative" in result:
            sections = result["learning_path_narrative"].split("="*50)

            intro = sections[0].strip()
            gaps = sections[1].strip() if len(sections) > 1 else ""
            steps = sections[2].strip() if len(sections) > 2 else ""
            summary = sections[3].strip() if len(sections) > 3 else ""
            cta = sections[4].strip() if len(sections) > 4 else ""

            display_intro(intro)
            st.markdown("---")
            display_gaps(gaps)
            st.markdown("---")
            display_learning_steps(steps)
            st.markdown("---")
            display_next_steps(cta)
        else:
            st.error("Failed to generate learning path")