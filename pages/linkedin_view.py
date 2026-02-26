import streamlit as st
import json

from agents.skill_assessment_agent.linkedin.linkedin_agent import analyze_linkedin_profile
from agents.skill_assessment_agent.linkedin.linkedin_feedback import get_corrected_linkedin

st.title("🔗 LinkedIn Agent")

# =============================
# 📋 INPUT SECTION
# =============================
st.subheader("📋 Paste Your LinkedIn Profile Text")

profile_text = st.text_area(
    "Paste copied LinkedIn profile (About, Activity, etc.)", height=200)

if profile_text:
    result = analyze_linkedin_profile(profile_text)
    try:
        parsed_linkedin = json.loads(result)
        st.session_state["parsed_linkedin"] = parsed_linkedin
        st.success("LinkedIn profile analyzed successfully.")
    except:
        st.error("❌ Could not parse LinkedIn result.")
        st.text(result)
        st.stop()

    tabs = st.tabs(
        ["🧠 Parsed LinkedIn", "➡️ Downstream Preview", "📝 Feedback"])

    # --- Tab 1: Parsed Output ---
    with tabs[0]:
        st.json(parsed_linkedin)

    # --- Tab 2: Downstream Preview ---
    with tabs[1]:
        st.markdown("### 🔄 Feeds into:")

        st.markdown("#### → Tool Recommender Agent")
        st.code(json.dumps(
            {"ai_interests": parsed_linkedin.get("ai_interests", [])},
            indent=2),
                language='json')

        st.markdown("#### → Experiment Agent")
        st.code(json.dumps(
            {"activity_level": parsed_linkedin.get("activity_level")},
            indent=2),
                language='json')

        st.markdown("#### → Meta Agent")
        st.code(json.dumps(
            {"cross_signals": parsed_linkedin.get("cross_signals", [])},
            indent=2),
                language='json')

    # --- Tab 3: Feedback & Correction ---
    with tabs[2]:
        st.markdown("### 💬 Review & Correct Fields")

        corrected_linkedin = get_corrected_linkedin(parsed_linkedin)
        st.session_state["corrected_linkedin"] = corrected_linkedin

        st.markdown("#### ✅ Final Output (for downstream agents)")
        st.json(corrected_linkedin)

        if st.button("✅ Save Corrections (Mock)"):
            st.success("Corrections saved to session.")
else:
    st.info("Paste your LinkedIn text above to begin.")
