"""
session_trace.py — per-session agent call recorder + LLM call interceptor support.

Records every tool call the coordinator makes, every sub-step inside pipelines,
and (via llm_tracer.py) every raw LLM call with prompt + response.

Context vars allow the LLM tracer to tag events with the right session/phase
without threading session_id through every function call.
"""
import time
from contextvars import ContextVar
from datetime import datetime

# Module-level store: {session_id: [event, event, ...]}
_traces: dict = {}

# Context vars — set by coordinator at the start of each turn so the LLM
# tracer can tag events without needing session_id passed explicitly.
_active_session: ContextVar = ContextVar("active_session", default=None)
_active_phase: ContextVar = ContextVar("active_phase", default="hook")


# ── Context var helpers ────────────────────────────────────────────────────────

def set_active_session(session_id: str) -> None:
    _active_session.set(session_id)

def get_active_session() -> str:
    return _active_session.get()

def set_active_phase(phase: str) -> None:
    _active_phase.set(phase.lower())

def get_active_phase() -> str:
    return _active_phase.get()


# ── Trace store ────────────────────────────────────────────────────────────────

def clear_trace(session_id: str) -> None:
    """Start a fresh trace for this session."""
    _traces[session_id] = []


def record_event(
    session_id: str,
    phase: str,
    agent: str,
    inputs: dict = None,
    outputs: dict = None,
    duration_ms: int = None,
    status: str = "ok",
    error: str = None,
    event_type: str = "tool",   # "tool" (coordinator-level) or "llm" (raw LLM call)
) -> None:
    """Append one event to the session trace."""
    if session_id not in _traces:
        _traces[session_id] = []
    _traces[session_id].append({
        "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
        "phase": phase.upper(),
        "agent": agent,
        "inputs": inputs or {},
        "outputs": outputs or {},
        "duration_ms": duration_ms,
        "status": status,
        "error": error,
        "type": event_type,
    })


def get_trace(session_id: str) -> list:
    """Return the raw event list for a session."""
    return _traces.get(session_id, [])


def get_trace_json(session_id: str) -> str:
    """Return the full trace as a JSON string (for download)."""
    import json
    return json.dumps(_traces.get(session_id, []), indent=2, default=str)


# ── Internal helpers ───────────────────────────────────────────────────────────

def _compact(d: dict, max_chars: int = 120) -> str:
    """Turn a dict into a short human-readable string."""
    parts = []
    for k, v in d.items():
        if v is None or v == "" or v == [] or v == {}:
            continue
        if isinstance(v, list):
            if len(v) == 0:
                continue
            elif len(v) <= 3:
                v_str = f"[{', '.join(str(x)[:40] for x in v)}]"
            else:
                v_str = f"[{len(v)} items]"
        elif isinstance(v, dict):
            v_str = f"{{{len(v)} keys}}"
        elif isinstance(v, str) and len(v) > 60:
            v_str = v[:57] + "..."
        else:
            v_str = str(v)
        parts.append(f"{k}={v_str}")

    result = ", ".join(parts)
    if len(result) > max_chars:
        result = result[:max_chars - 3] + "..."
    return result or "(none)"
