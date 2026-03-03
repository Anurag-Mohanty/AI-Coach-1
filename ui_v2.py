import streamlit as st
import json
from datetime import datetime, timedelta

from resume_parser import extract_text_from_file  # ✅ PDF/DOCX parsing helper
from resume_agent import analyze_resume
from linkedin_agent import analyze_linkedin_profile
from role_context_agent import analyze_role_context
from tool_familiarity_agent import infer_and_confirm_tools
from use_case_agent import generate_ai_use_cases
from tool_recommender import recommend_tools
from cultural_alignment_agent import infer_communication_style
from aspiration_agent import interpret_aspiration
from role_ladder_agent import map_role_ladder
from skill_delta_agent import identify_skill_gaps
from role_details_agent import infer_work_structure
from use_case_miss_agent import identify_ai_opportunities_from_tasks
from domain_jump_agent import analyze_domain_jump
from meta_agent import recommend_learning_path  # Peer pattern agent
from learning_path_agent import recommend_learning_path as build_learning_path  # Personalized path agent
from experiment_agent import suggest_experiment
from follow_up_agent import follow_up_agent
from feedback_agent import capture_user_feedback

st.set_page_config(page_title="🧠 AI Skill Assessment App", layout="centered")
st.title("🧠 AI Skill Assessment App")

# =============================
# 📤 RESUME INPUT SECTION
# =============================
st.subheader("📤 Upload or Paste Your Resume")

uploaded_resume = st.file_uploader("Upload Resume (.pdf, .docx, .txt)",
                                   type=["pdf", "docx", "txt"])
resume_text = ""

if uploaded_resume:
    resume_text = extract_text_from_file(uploaded_resume)
    st.text_area("📄 Extracted Resume Text",
                 resume_text,
                 height=200,
                 disabled=True)
else:
    resume_text = st.text_area("📄 Or Paste Resume Text Here", height=200)

# --- RESUME AGENT TAB ---
st.subheader("📄 Resume Agent")

resume_tabs = st.tabs(
    ["🔍 Analyze", "🧭 Preview Downstream Usage", "📝 Provide Feedback"])

with resume_tabs[0]:
    if resume_text:
        resume_result = analyze_resume(resume_text)
        try:
            parsed_resume = json.loads(resume_result)
            st.success("Resume analyzed successfully.")
            st.json(parsed_resume)
        except:
            st.error("❌ Failed to parse resume response.")
            st.text(resume_result)
            st.stop()
    else:
        st.warning("Please upload or paste your resume.")

with resume_tabs[1]:
    st.markdown("### 🔄 How Parsed Resume Feeds Other Agents")

    if 'parsed_resume' in locals():
        st.markdown("#### → Role Context Agent Input")
        st.code(json.dumps(
            {
                "title": parsed_resume.get("title"),
                "company": parsed_resume.get("company"),
                "domain": parsed_resume.get("domain")
            },
            indent=2),
                language='json')

        st.markdown("#### → Tool Familiarity Agent Input")
        st.code(json.dumps({"tools": parsed_resume.get("tools")}, indent=2),
                language='json')

        st.markdown("#### → Skill Delta Agent Input")
        st.code(json.dumps(
            {
                "seniority": parsed_resume.get("seniority"),
                "ai_keywords": parsed_resume.get("ai_keywords")
            },
            indent=2),
                language='json')
    else:
        st.info("Analyze resume first to preview downstream usage.")

with resume_tabs[2]:
    if 'parsed_resume' in locals():
        st.markdown("### 💬 Review & Give Feedback on Extracted Fields")

        def feedback_field(label, key, default):
            col1, col2 = st.columns([3, 1])
            with col1:
                correction = st.text_input(f"{label} (Detected: {default})",
                                           key=f"correction_{key}")
            with col2:
                thumbs = st.radio("Feedback", ["👍", "👎"], key=f"thumb_{key}")
            return correction.strip(
            ) if thumbs == "👎" and correction.strip() else default

        corrected_resume = {}
        for field in ["title", "seniority", "company", "domain"]:
            corrected_resume[field] = feedback_field(
                field.title(), field, parsed_resume.get(field, ""))

        corrected_resume["tools"] = parsed_resume.get("tools", [])
        corrected_resume["ai_keywords"] = parsed_resume.get("ai_keywords", [])

        if not corrected_resume["ai_keywords"]:
            st.warning(
                "⚠️ No AI-related terms found in resume. You may want to add some."
            )

        if not corrected_resume["tools"]:
            st.warning(
                "⚠️ No tools were detected. Double check or provide manual list."
            )

        st.markdown("#### ✅ Final Corrected Output (used for downstream)")
        st.json(corrected_resume)

        # Optional: Log corrections
        if st.button("Save Corrections (Mock)"):
            st.success("✅ Corrections saved locally.")
            st.session_state["corrected_resume"] = corrected_resume
    else:
        st.info("Analyze resume first to provide feedback.")

# =============================
# 🔗 LINKEDIN INPUT
# =============================
linkedin_text = st.text_area("🔗 Paste LinkedIn Profile Text", height=200)

# =============================
# 🌟 ASPIRATION
# =============================
aspiration = st.radio(
    "🌟 What’s your goal for the next 6–12 months?",
    ["Get promoted", "Switch domains", "Lateral move", "AI upskilling"])

if st.button("Analyze Profile"):
    if not resume_text.strip():
        st.warning("Please upload or paste your resume.")
    elif not linkedin_text.strip():
        st.warning("Please paste your LinkedIn profile text.")
    else:
        with st.spinner("Analyzing..."):

            # ============================
            # 🔷 SKILL ASSESSMENT AGENT
            # ============================
            st.header("🔷 Skill Assessment Agent")

            st.subheader("📄 Resume Agent")
            resume_result = analyze_resume(resume_text)
            try:
                parsed_resume = json.loads(resume_result)
                st.json(parsed_resume)
            except:
                st.error("❌ Failed to parse resume response.")
                st.text(resume_result)
                st.stop()

            st.subheader("🔗 LinkedIn Agent")
            profile_result = analyze_linkedin_profile(linkedin_text)
            try:
                parsed_linkedin = json.loads(profile_result)
                st.json(parsed_linkedin)
            except:
                st.error("❌ Failed to parse LinkedIn response.")
                st.text(profile_result)
                st.stop()

            st.subheader("🏢 Role Context Agent")
            context_result = analyze_role_context(parsed_resume,
                                                  parsed_linkedin)
            st.json(context_result)

            st.subheader("🧾 Role Details Agent")
            role_title = parsed_resume.get("title", "unknown")
            company_name = parsed_resume.get("company", "unknown")
            industry = parsed_resume.get("domain", "unknown")
            work_structure = infer_work_structure(
                role=role_title,
                resume=resume_text,
                linkedin=linkedin_text,
                role_context=json.dumps(context_result),
                aspiration=aspiration)
            try:
                role_details = json.loads(work_structure)
                st.json(role_details)
            except:
                st.warning("⚠️ Could not parse work structure response.")
                st.text(work_structure)
                role_details = {}

            st.subheader("🧰 Tool Familiarity Agent")
            confirmed_tools = infer_and_confirm_tools(parsed_resume)
            st.json(confirmed_tools)

            st.subheader("🌐 Cultural Alignment Agent")
            inferred_style = infer_communication_style(parsed_resume,
                                                       parsed_linkedin,
                                                       context_result)
            st.json(inferred_style)

            # ============================
            # 🔹 ASPIRATION AGENT
            # ============================
            st.header("🔹 Aspiration Agent")
            aspiration_result = interpret_aspiration(parsed_resume,
                                                     parsed_linkedin,
                                                     aspiration)
            st.json(aspiration_result)

            # ============================
            # 🔷 GAP ANALYSIS AGENT
            # ============================
            st.header("🔷 Gap Analysis Agent")

            st.subheader("📈 Role Ladder Agent")
            role_ladder = map_role_ladder(parsed_resume, parsed_linkedin,
                                          aspiration_result)
            st.json(role_ladder)

            st.subheader("🧠 Skill Delta Agent")
            skill_gaps = identify_skill_gaps(parsed_resume, aspiration_result,
                                             role_ladder)
            st.json(skill_gaps)

            st.subheader("📌 Use Case Miss Agent")
            if role_details:
                missed_uses = identify_ai_opportunities_from_tasks(
                    role_details, confirmed_tools, parsed_resume, industry,
                    aspiration)
                st.json(missed_uses)
            else:
                st.info(
                    "Skipping use case gap check — no role details available.")

            st.subheader("🌐 Domain Jump Agent")
            domain_jump = analyze_domain_jump(parsed_resume, aspiration_result,
                                              role_ladder)
            st.json(domain_jump)

            # ============================
            # 🟢 RECOMMENDATION AGENT
            # ============================
            st.header("🟢 Recommendation Agent")

            st.subheader("🚀 Use Case Generator Agent")
            use_cases = generate_ai_use_cases(parsed_resume)
            st.markdown(use_cases)

            st.subheader("🛠️ Tool Recommender Agent")
            tools = recommend_tools(parsed_resume, use_cases)
            st.markdown(tools)

            st.subheader("📊 Meta Agent: Peer-Informed Learning Path")
            meta_recommendations = recommend_learning_path(
                parsed_resume, aspiration_result, role_ladder, confirmed_tools,
                domain_jump)
            st.json(meta_recommendations)

            st.subheader(
                "📚 Learning Path Agent: Personalized Step-by-Step Plan")
            learning_path = build_learning_path(parsed_resume,
                                                aspiration_result, role_ladder,
                                                confirmed_tools, skill_gaps,
                                                domain_jump, missed_uses)
            st.json(learning_path)

            # ============================
            # 🧪 EXPERIMENT & FEEDBACK
            # ============================
            st.header("🧪 Experiment & Feedback Loop")

            st.subheader("🧪 Experiment Agent")
            experiment = suggest_experiment(missed_uses, confirmed_tools,
                                            aspiration)
            st.json(experiment)

            st.subheader("🔁 Follow-Up Agent")
            mock_last_used_date = datetime.today().date() - timedelta(days=22)
            mock_feedback = "It was helpful but a bit confusing"
            followup = follow_up_agent(last_used_tools=confirmed_tools,
                                       last_used_date=mock_last_used_date,
                                       feedback_summary=mock_feedback)
            st.json(followup)

            st.subheader("💬 Feedback Agent")
            feedback_summary = capture_user_feedback(
                recommendations=learning_path,
                experiment_result=experiment,
                follow_up_data=followup)
            st.json(feedback_summary)
