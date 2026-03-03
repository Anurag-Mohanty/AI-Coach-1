import os
import sys

# Load .env before any other imports — several modules create OpenAI clients at module level
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from coach.coordinator import CoachCoordinator
from coach.user_model.store import get_or_create_user, save_user_model, delete_user
from agent_core.persona_context import clear_user_context
from agent_core.session_trace import get_trace_json
from agent_core.llm_tracer import install_tracer

# Install the LLM call interceptor once at startup — captures every OpenAI
# call anywhere in the codebase and records it to the session trace.
install_tracer()

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Coach",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Global styles ──────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    /* Hide Streamlit chrome we don't need */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Keep the header (and sidebar toggle) visible but shrink it */
    header[data-testid="stHeader"] {background: transparent; height: 2.5rem;}

    /* Always show the sidebar collapse/expand toggle */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        z-index: 999999 !important;
    }

    /* Main content padding */
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem; max-width: 820px;}

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #F7F9FF;
        border-right: 1px solid #E2E8F8;
    }
    [data-testid="stSidebar"] .block-container {padding-top: 1rem;}

    /* Trace event rows */
    .trace-event {
        background: #FFFFFF;
        border: 1px solid #E2E8F8;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 6px;
        font-size: 0.82em;
        line-height: 1.5;
    }
    .trace-phase-header {
        font-size: 0.72em;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #6B7FCC;
        margin: 12px 0 6px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _init_session(name: str):
    """Load or create user, spin up coordinator, generate opening message."""
    user_model, is_returning = get_or_create_user(name)
    coordinator = CoachCoordinator(user_model)

    with st.spinner(""):
        opening = coordinator.get_opening_message()

    st.session_state.user_id = user_model["user_id"]
    st.session_state.user_name = name
    st.session_state.coordinator = coordinator
    st.session_state.display_messages = [{"role": "assistant", "content": opening}]
    st.session_state.last_uploaded_filename = None


def _handle_user_turn(user_message: str, file_bytes: bytes = None, filename: str = None):
    """Send one turn to the coordinator and append results to display_messages."""
    coordinator: CoachCoordinator = st.session_state.coordinator

    # Show user message immediately
    with st.chat_message("user"):
        label = user_message if not file_bytes else f"*[Resume uploaded: {filename}]*"
        st.markdown(label)
    st.session_state.display_messages.append({"role": "user", "content": label})

    # Collect intermediate messages emitted during tool execution.
    # For PRESCRIBE turns this includes:
    #   [0] pre-message ("On it — building your path for X...")
    #   [1] formatted_output (full coaching narrative)
    # For regular HOOK/REVEAL turns the list is empty.
    intermediate_messages: list[str] = []

    # st.status() shows live pipeline steps (written by prescribe pipeline).
    # It runs OUTSIDE the chat bubble so intermediate messages and the final
    # response can each be rendered as separate chat bubbles below.
    with st.status("Working...", expanded=False) as status_ctx:
        st.session_state["_status_ctx"] = status_ctx
        response = coordinator.chat(
            user_message,
            file_bytes=file_bytes,
            filename=filename,
            on_intermediate_message=intermediate_messages.append,
        )
        status_ctx.update(state="complete", expanded=False)
    st.session_state.pop("_status_ctx", None)

    # Render each message (intermediate + final) as a separate chat bubble.
    # For regular turns there are no intermediate messages so this behaves
    # identically to before — one bubble with `response`.
    all_messages = intermediate_messages + ([response] if response and response.strip() else [])
    for msg in all_messages:
        if msg and msg.strip():
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.session_state.display_messages.append({"role": "assistant", "content": msg})

    # Persist user model
    save_user_model(st.session_state.user_id, coordinator.user_model)


# ── Sidebar trace ─────────────────────────────────────────────────────────────

def _render_sidebar():
    """Render the live agent trace in the sidebar."""
    coordinator: CoachCoordinator = st.session_state.get("coordinator")
    if not coordinator:
        return

    session_id = coordinator.session_id
    user_name = st.session_state.get("user_name", "")
    phase = coordinator.user_model.get("coaching_state", {}).get("current_phase", "hook").upper()

    from agent_core.session_trace import get_trace

    with st.sidebar:
        st.markdown("### 🔭 Agent Trace")
        st.caption(f"User: **{user_name}** · Phase: **{phase}**")

        events = get_trace(session_id)
        if not events:
            st.info("No agent calls yet. Start chatting to see the trace.", icon="💡")
        else:
            current_phase = None
            for ev in events:
                ev_phase = ev.get("phase", "?")
                ev_type = ev.get("type", "tool")

                # Phase header when phase changes
                if ev_phase != current_phase:
                    current_phase = ev_phase
                    st.markdown(
                        f"<div class='trace-phase-header'>— {current_phase} —</div>",
                        unsafe_allow_html=True,
                    )

                if ev_type == "llm":
                    # ── LLM event: expandable with full prompt + response ──────
                    status_icon = {"ok": "🤖", "error": "❌"}.get(ev["status"], "🔵")
                    dur = f" {ev['duration_ms']}ms" if ev.get("duration_ms") else ""
                    model = ev.get("inputs", {}).get("model", "")
                    model_tag = f" `{model}`" if model else ""
                    ts = ev.get("timestamp", "")
                    label = f"{status_icon} {ev['agent']}{dur}{model_tag}"

                    with st.expander(label, expanded=False):
                        st.caption(f"🕐 {ts}")
                        if ev.get("error"):
                            st.error(ev["error"][:300])

                        sys_text = (ev.get("inputs") or {}).get("sys", "")
                        prompt_text = (ev.get("inputs") or {}).get("prompt", "")
                        response_text = (ev.get("outputs") or {}).get("response", "")

                        if sys_text:
                            st.markdown("**📋 System prompt:**")
                            st.code(sys_text, language=None)
                        if prompt_text:
                            st.markdown("**💬 User / input message:**")
                            st.code(prompt_text, language=None)
                        if response_text:
                            st.markdown("**✨ Response:**")
                            st.code(response_text, language=None)

                else:
                    # ── Tool event: compact card ──────────────────────────────
                    icon = {"ok": "✅", "error": "❌", "skip": "⚪"}.get(ev["status"], "🔵")
                    dur = f"<span style='color:#94A3B8;font-size:0.85em'> {ev['duration_ms']}ms</span>" if ev.get("duration_ms") else ""
                    ts = f"<span style='color:#CBD5E1;font-size:0.78em'>{ev.get('timestamp','')}</span>"

                    in_parts, out_parts = [], []
                    for k, v in (ev.get("inputs") or {}).items():
                        if v is None or v == "" or v == [] or v == {}:
                            continue
                        v_str = str(v)[:70] + ("…" if len(str(v)) > 70 else "")
                        in_parts.append(f"<b>{k}</b>: {v_str}")
                    for k, v in (ev.get("outputs") or {}).items():
                        if v is None or v == "" or v == [] or v == {}:
                            continue
                        v_str = str(v)[:70] + ("…" if len(str(v)) > 70 else "")
                        out_parts.append(f"<b>{k}</b>: {v_str}")

                    io_block = ""
                    if in_parts:
                        io_block += f"<div style='color:#64748B;font-size:0.8em;margin-top:4px'>↳ in: {'<br>'.join(in_parts)}</div>"
                    if out_parts:
                        io_block += f"<div style='color:#3B5BDB;font-size:0.8em'>↳ out: {'<br>'.join(out_parts)}</div>"
                    if ev.get("error"):
                        io_block += f"<div style='color:#E53E3E;font-size:0.78em'>⚠ {str(ev['error'])[:150]}</div>"

                    st.markdown(
                        f"<div class='trace-event'>"
                        f"{icon} <b>{ev['agent']}</b>{dur} {ts}"
                        f"{io_block}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        st.markdown("---")
        if events:
            trace_json = get_trace_json(session_id)
            st.download_button(
                label="📋 Export trace (JSON)",
                data=trace_json,
                file_name=f"trace_{session_id}.json",
                mime="application/json",
                use_container_width=True,
            )

        st.markdown("---")
        st.caption("**Danger zone**")
        if st.button("🗑️ Reset session (wipe all stored data)", use_container_width=True):
            user_id = st.session_state.get("user_id")
            if user_id:
                delete_user(user_id)
                clear_user_context(user_id)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ── Name screen ───────────────────────────────────────────────────────────────

def show_name_screen():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("## 🧠 AI Coach")
        st.markdown("Your personalized guide to working smarter with AI.")
        st.markdown("---")
        name = st.text_input(
            "What's your name?",
            placeholder="e.g. Sarah",
            label_visibility="visible",
        )
        if st.button("Get started →", type="primary", use_container_width=True):
            if name.strip():
                _init_session(name.strip())
                st.rerun()
            else:
                st.warning("Please enter your name to continue.")


# ── Chat screen ───────────────────────────────────────────────────────────────

def show_chat_screen():
    _render_sidebar()

    # Render existing conversation history
    for msg in st.session_state.display_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Resume uploader — sits between conversation and chat input
    with st.expander("📎 Attach resume (PDF, DOCX, or TXT)"):
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed",
        )

    # Handle new file upload (fires once per unique file)
    if (
        uploaded_file is not None
        and uploaded_file.name != st.session_state.get("last_uploaded_filename")
    ):
        st.session_state.last_uploaded_filename = uploaded_file.name
        file_bytes = uploaded_file.getvalue()
        _handle_user_turn(
            "I've uploaded my resume.",
            file_bytes=file_bytes,
            filename=uploaded_file.name,
        )
        st.rerun()

    # Handle typed message
    if user_input := st.chat_input("Message your coach..."):
        _handle_user_turn(user_input)
        st.rerun()


# ── Entry point ───────────────────────────────────────────────────────────────

if "user_id" not in st.session_state:
    show_name_screen()
else:
    show_chat_screen()
