
# pages/cultural_alignment_view.py
import streamlit as st
from agents.skill_assessment_agent.cultural_alignment_agent.cultural_alignment_agent import run_cultural_alignment_agent
from agents.skill_assessment_agent.cultural_alignment_agent.tone_profile_engine import generate_prompt_variants

st.set_page_config(page_title="Cultural Alignment Profiler", layout="centered")
st.title("🧭 Cultural Alignment Profiler")

# Collect structured user context from session or manual input
context_inputs = st.session_state.get("persona_context", {})

# Cultural context with improved prompt
st.markdown("### 🌍 Help us personalize your learning experience")
st.markdown("""
To present content in the most relevant way, we'd like to understand the cultural influences that have shaped you. 
This is completely optional - please share only if you feel comfortable.
""")
ethnicity = st.text_input(
    "What cultural backgrounds have influenced your learning style? (e.g., South Asian academic tradition, North American business culture, European collaborative style)",
    context_inputs.get("ethnicity", ""))
if ethnicity:
    context_inputs["ethnicity"] = ethnicity

# Simplified tone selection
st.markdown("### 🎙️ How do you prefer to learn new things?")

from agents.skill_assessment_agent.role_detail.role_detail_agent import extract_focus_topic_from_role

# Dynamically extract topic for tone prompt
if "target_topic" not in context_inputs:
    context_inputs["target_topic"] = extract_focus_topic_from_role(
        context_inputs.get("role_details", {})) or "explaining a concept to a team"

# Integrated tone options with descriptions
selected_tone = st.radio(
    "Choose your preferred learning style:",
    [
        "Clear, step-by-step tactical instructions (direct and actionable)",
        "Real-world stories and examples (narrative and relatable)",
        "Side-by-side comparisons with pros and cons (analytical and thorough)"
    ],
    index=0)

# Map selection back to internal format
tone_mapping = {
    "Clear, step-by-step tactical instructions (direct and actionable)": "Directive / Tactical",
    "Real-world stories and examples (narrative and relatable)": "Story-Driven",
    "Side-by-side comparisons with pros and cons (analytical and thorough)": "Analytical / Contrastive"
}

# Optional custom input
custom_input = st.text_area(
    "✍️ Or describe your own preferred way of learning:",
    key="custom_tone_input")

# Store selections in context
from agent_core.global_agent_memory import store_memory

if custom_input:
    context_inputs["tone_preference_custom"] = custom_input
    context_inputs["tone_source"] = "custom"
else:
    mapped_tone = tone_mapping[selected_tone]
    context_inputs["tone_preference_custom"] = selected_tone
    context_inputs["tone_source"] = mapped_tone

# Save tone preference to global memory
store_memory(agent_name="cultural_alignment_agent",
             user_id="demo_user",
             session_id="demo_session",
             subtask_id="tone_selector",
             function="store_user_tone_preference",
             input_fields={"topic": context_inputs["target_topic"]},
             output_fields={
                 "tone_preference_custom": context_inputs["tone_preference_custom"],
                 "tone_source": context_inputs["tone_source"]
             })

# Update the persistent persona context
from agent_core.persona_context import update_shared_context

update_shared_context(
    "demo_user", {
        "preferred_tone": context_inputs["tone_preference_custom"],
        "tone_style": context_inputs["tone_source"],
        "work_style_notes": context_inputs.get("work_style_notes", ""),
        "tone_topic": context_inputs["target_topic"]
    })
