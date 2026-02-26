import streamlit as st
import json

from agents.resume.resume_parser import extract_text_from_file
from agents.resume.resume_agent import analyze_resume

st.set_page_config(page_title="📄 Resume Agent Tester", layout="centered")
st.title("📄 Resume Agent")

# --- Upload or Paste ---
uploaded_file = st.file_uploader("Upload Resume (.pdf, .docx, .txt)",
                                 type=["pdf", "docx", "txt"])
resume_text = ""

if uploaded_file:
    resume_text = extract_text_from_file(uploaded_file)
    st.text_area("📄 Extracted Resume Text",
                 resume_text,
                 height=200,
                 disabled=True)
else:
    resume_text = st.text_area("📄 Or Paste Resume Text", height=200)

# --- Analyze Button ---
if st.button("🔍 Analyze Resume"):
    if not resume_text.strip():
        st.warning("Please provide resume text.")
    else:
        with st.spinner("Analyzing..."):
            result = analyze_resume(resume_text)
            try:
                parsed = json.loads(result)
                st.success("Parsed successfully!")
                st.json(parsed)
            except:
                st.error("❌ Parsing failed.")
                st.text(result)
