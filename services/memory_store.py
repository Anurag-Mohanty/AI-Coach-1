# services/memory_store.py
from agent_core.global_agent_memory import store_memory, get_context


# ---------- write ----------
async def save_blob(user_id: str, session_id: str, blob_name: str, data: dict):
    """
    Wraps global store_memory.  We stash the blob in output_fields.
    """
    await store_memory(
        agent_name=blob_name,  # we piggy-back on subtask_id slot
        user_id=user_id,
        session_id=session_id,
        subtask_id=blob_name,
        function="save_blob",
        input_fields={},
        output_fields=data,
    )


# ---------- read ----------
async def load_blob(user_id: str, session_id: str, blob_name: str) -> dict | None:
    """
    Pulls the session context, then returns the requested blob's output_fields.
    """
    ctx = await get_context(user_id, session_id) or {}
    record = ctx.get(blob_name)  # record saved under that key
    return (record or {}).get("output_fields")