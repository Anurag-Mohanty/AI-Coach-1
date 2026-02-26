# agents/linkedin/linkedin_feedback.py

import streamlit as st
import json


def get_corrected_linkedin(parsed_output):
    """Get corrected LinkedIn data with user feedback"""
    return collect_feedback(parsed_output)

def collect_feedback(parsed_output):
    st.markdown("### 💬 Review LinkedIn Insights")

    corrections = {}
    ratings = {}

    for field, value in parsed_output.items():
        if isinstance(value, (str, list)):
            col1, col2 = st.columns([4, 1])
            with col1:
                default_val = json.dumps(value) if isinstance(value,
                                                              list) else value
                corrected = st.text_input(
                    f"{field.title()} (Detected: {default_val})",
                    key=f"li_corr_{field}")
            with col2:
                thumbs = st.radio("👍/👎", ["👍", "👎"], key=f"li_rating_{field}")

            # Save only if correction differs
            if thumbs == "👎" and corrected.strip(
            ) and corrected != default_val:
                try:
                    corrections[field] = json.loads(
                        corrected) if corrected.startswith("[") else corrected
                except:
                    corrections[field] = corrected
            ratings[field] = thumbs

    st.markdown("### ✅ Final Corrected Output")
    final_output = parsed_output.copy()
    final_output.update(corrections)
    st.json(final_output)

    if st.button("Save Feedback"):
        st.success("✅ Feedback stored in session.")
        st.session_state["linkedin_feedback"] = {
            "corrections": corrections,
            "ratings": ratings,
            "final_output": final_output
        }

    return final_output
