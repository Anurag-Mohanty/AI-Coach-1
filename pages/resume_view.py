import streamlit as st
from agents.skill_assessment_agent.resume.resume_agent import analyze_resume
from agents.skill_assessment_agent.resume.resume_parser import extract_text_from_file

def main():
    # Initialize session tracking
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "demo_user"
    if 'session_id' not in st.session_state:
        from datetime import datetime
        st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Initialize session state
    if 'resume_content' not in st.session_state:
        st.session_state.resume_content = None
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False

    st.title("📄 Resume Agent")

    # File uploader
    uploaded_file = st.file_uploader("Upload your resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

    # Display the current content area
    if 'resume_content' in st.session_state and st.session_state.resume_content:
        st.text_area("Current Resume Content", st.session_state.resume_content, height=200, disabled=True)
    else:
        st.text_area("Or paste your resume text here", "", height=200, key="manual_input")

    # Handle file upload
    if uploaded_file is not None and not st.session_state.file_uploaded:
        with st.spinner("Processing resume..."):
            try:
                st.session_state.resume_content = extract_text_from_file(uploaded_file)
                st.session_state.file_uploaded = True
                st.success("✅ Resume uploaded successfully!")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    # Analyze button
    if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
        if st.session_state.resume_content or st.session_state.get("manual_input"):
            with st.spinner("Analyzing resume..."):
                try:
                    content = st.session_state.resume_content or st.session_state.get("manual_input")
                    result = analyze_resume(resume_text=content)
                    st.session_state.analysis_result = result
                    st.success("✅ Analysis complete!")
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
        else:
            st.warning("Please upload a resume or paste text first")

    # Always show results if they exist
    if st.session_state.analysis_result:
        st.markdown("---")
        st.subheader("Analysis Results")

        result = st.session_state.analysis_result
        if "error" in result:
            st.error(f"Analysis error: {result['error']}")
        else:
            # Display extracted fields
            st.subheader("🧠 Extracted Fields")
            if "extracted_fields" in result:
                st.json(result["extracted_fields"])
            else:
                st.json(result)  # Display full result if no extracted_fields key

            # Display downstream agent data if available
            if "downstream_payloads" in result:
                st.subheader("📦 Downstream Agent Data")
                for agent_name, payload in result["downstream_payloads"].items():
                    with st.expander(f"🔄 {agent_name.replace('_', ' ').title()}"):
                        st.json(payload)

            # Feedback section
            st.markdown("### Was this analysis helpful?")
            col1, col2 = st.columns([1, 3])
            with col1:
                feedback = st.radio("Rating", ["👍", "👎"], key="feedback")
            with col2:
                if feedback == "👎":
                    st.text_input("What could be improved?", key="feedback_text")

if __name__ == "__main__":
    main()