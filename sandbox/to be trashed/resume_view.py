import streamlit as st
import json

from agents.resume.resume_agent import analyze_resume
from agents.resume.resume_parser import extract_text_from_file

st.title("📄 Resume Analyzer")

# =============================
# 📤 Upload or Paste Resume
# =============================
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

# =============================
# 🔍 Run Resume Agent
# =============================
if resume_text:
    resume_result = analyze_resume(resume_text)
    try:
        parsed_resume = json.loads(resume_result)
        st.session_state["parsed_resume"] = parsed_resume
        st.success("✅ Resume parsed successfully.")
    except:
        st.error("❌ Could not parse resume result.")
        st.text(resume_result)
        st.stop()

    tabs = st.tabs(["🧠 Parsed Resume", "➡️ Downstream Preview", "📝 Feedback"])

    # Tab 1: Parsed Resume
    with tabs[0]:
        st.subheader("🧠 Parsed Resume")
        st.json(parsed_resume)

    # Tab 2: Downstream Preview
    with tabs[1]:
        st.subheader("➡️ Downstream Agent Preview")
        st.markdown("### Feeds into:")

        st.markdown("#### → Role Context Agent")
        st.code(json.dumps(
            {
                "title": parsed_resume.get("title"),
                "company": parsed_resume.get("company"),
                "domain": parsed_resume.get("domain")
            },
            indent=2),
                language='json')

        st.markdown("#### → Tool Familiarity Agent")
        st.code(json.dumps({"tools": parsed_resume.get("tools")}, indent=2),
                language='json')

        st.markdown("#### → Skill Delta Agent")
        st.code(json.dumps(
            {
                "seniority": parsed_resume.get("seniority"),
                "ai_keywords": parsed_resume.get("ai_keywords")
            },
            indent=2),
                language='json')

    # Tab 3: Feedback & Corrections
    with tabs[2]:
        st.subheader("📝 Feedback & Correction")

        def feedback_input(label, key, default_val):
            col1, col2 = st.columns([3, 1])
            with col1:
                correction = st.text_input(
                    f"{label} (Detected: {default_val})", key=f"corr_{key}")
            with col2:
                thumbs = st.radio("👍/👎", ["👍", "👎"], key=f"thumb_{key}")
            return correction.strip(
            ) if thumbs == "👎" and correction.strip() else default_val

        corrected_resume = {}
        for field in ["title", "seniority", "company", "domain"]:
            corrected_resume[field] = feedback_input(
                field.title(), field, parsed_resume.get(field, ""))

        corrected_resume["tools"] = parsed_resume.get("tools", [])
        corrected_resume["ai_keywords"] = parsed_resume.get("ai_keywords", [])

        if not corrected_resume["ai_keywords"]:
            st.warning(
                "⚠️ No AI terms found in resume. Add them manually or edit resume."
            )

        if not corrected_resume["tools"]:
            st.warning("⚠️ No tools detected. You can add some manually.")

        st.markdown("#### ✅ Final Corrected Output")
        st.json(corrected_resume)

        if st.button("💾 Save Corrections (Mock)"):
            st.success("Corrections saved locally to session.")
            st.session_state["corrected_resume"] = corrected_resume

        # ✅ Prefer corrected version as downstream default
        resume_data = st.session_state.get("corrected_resume", parsed_resume)
        st.session_state["resume_data"] = resume_data

        if st.button("✅ Confirm Resume & Proceed"):
            st.session_state["resume_confirmed"] = True
            st.success("✅ Resume confirmed and ready for full analysis.")

else:
    st.info("Please upload or paste your resume to begin.")
