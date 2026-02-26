
import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="🧠 AI Skill Assessment App", layout="centered")

# Ensure we stay on main page
if "main" not in st.session_state:
    st.session_state.main = True

st.title("🧠 AI Skill Assessment App")

st.markdown("Welcome! Choose what you'd like to work on:")

selected = option_menu(
    menu_title=None,
    options=["📄 Resume Agent", "🔗 LinkedIn Agent", "🧪 Full Assessment", "📊 Dashboard", "🛠️ Admin"],
    icons=["file-text", "linkedin", "magic", "graph-up", "gear"],
    orientation="horizontal",
)

if selected == "📄 Resume Agent":
    st.markdown("## Resume Analysis")
    from pages import resume_view
elif selected == "🔗 LinkedIn Agent":
    st.markdown("## LinkedIn Analysis")
    from pages import linkedin_view
elif selected == "🧪 Full Assessment":
    st.info("⚙️ Full flow under development — stay tuned!")
elif selected == "📊 Dashboard":
    st.info("📈 Dashboard coming soon — will show progress and experiments.")
elif selected == "🛠️ Admin":
    st.info("💼 Admin insights and system performance metrics coming soon.")
