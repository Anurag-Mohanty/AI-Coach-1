"""
llm_tracer.py — system-wide LLM call interceptor.

install_tracer() monkey-patches openai.resources.chat.completions.Completions.create
ONCE at app startup. After that, every OpenAI chat completion made anywhere in the
codebase is automatically recorded to the session trace — no per-file changes needed.

Each trace event captures:
  - Which file + function made the call (via inspect.stack)
  - The model used
  - The system prompt (first 300 chars)
  - The last user message (first 600 chars)
  - The full response (first 800 chars)
  - Duration in ms

The session_id and phase are read from ContextVars set by the coordinator at the
start of each turn (via set_active_session / set_active_phase in session_trace.py).
"""
import functools
import inspect
import time

from agent_core.session_trace import record_event, get_active_session, get_active_phase

_installed = False

# Files/paths to skip when walking the call stack to find the real caller.
_SKIP_PATTERNS = (
    "/openai/",
    "/httpx/",
    "/httpcore/",
    "llm_tracer.py",
    "<frozen",
    "/asyncio/",
    "/concurrent/",
)


def install_tracer() -> None:
    """
    Patch openai.resources.chat.completions.Completions.create once at startup.
    Safe to call multiple times — installs only once.
    """
    global _installed
    if _installed:
        return
    _installed = True

    try:
        import openai.resources.chat.completions as _completions_mod
        _original = _completions_mod.Completions.create

        @functools.wraps(_original)
        def _traced_create(self_c, *args, **kwargs):
            session_id = get_active_session()
            phase = get_active_phase()
            t0 = time.time()

            # Identify the calling agent (first non-openai frame)
            agent_label = _caller_name()

            messages = kwargs.get("messages", args[0] if args else [])
            model = kwargs.get("model", "?")

            try:
                response = _original(self_c, *args, **kwargs)
                content = ""
                if response.choices:
                    content = response.choices[0].message.content or ""
                duration = int((time.time() - t0) * 1000)

                if session_id:
                    sys_msgs = [m for m in messages if m.get("role") == "system"]
                    user_msgs = [m for m in messages if m.get("role") == "user"]
                    sys_preview = (sys_msgs[0]["content"][:300] if sys_msgs else "")
                    prompt_preview = (
                        user_msgs[-1]["content"][:600]
                        if user_msgs
                        else (messages[-1].get("content", "")[:600] if messages else "")
                    )

                    record_event(
                        session_id,
                        phase=phase,
                        agent=agent_label,
                        inputs={
                            "model": model,
                            "sys": sys_preview,
                            "prompt": prompt_preview,
                        },
                        outputs={"response": content[:800]},
                        duration_ms=duration,
                        status="ok",
                        event_type="llm",
                    )
                return response

            except Exception as exc:
                duration = int((time.time() - t0) * 1000)
                if session_id:
                    record_event(
                        session_id,
                        phase=phase,
                        agent=agent_label,
                        inputs={"model": model},
                        outputs={},
                        duration_ms=duration,
                        status="error",
                        error=str(exc)[:300],
                        event_type="llm",
                    )
                raise

        _completions_mod.Completions.create = _traced_create
        print("[LLM Tracer] ✅ Installed — every OpenAI call will appear in the sidebar trace.")

    except Exception as e:
        print(f"[LLM Tracer] ⚠️  Could not install: {e}")


def _caller_name() -> str:
    """
    Walk the call stack and return 'filename.function_name' for the first frame
    that isn't inside the openai SDK, httpx, or this file.
    """
    try:
        stack = inspect.stack(context=0)   # context=0 avoids reading source lines (faster)
        for frame_info in stack[2:12]:     # skip _traced_create + _caller_name
            fname = frame_info.filename
            if any(p in fname for p in _SKIP_PATTERNS):
                continue
            module = fname.split("/")[-1].replace(".py", "")
            func = frame_info.function
            return f"{module} → {func}"
    except Exception:
        pass
    return "unknown"
