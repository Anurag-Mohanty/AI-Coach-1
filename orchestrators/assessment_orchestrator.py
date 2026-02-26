import services.memory_store as memory
from tools.tools_registry import REGISTRY
from services.schema_loader import validate_payload


async def run(user_id: str, session_id: str, resume_file=None, resume_text=None) -> dict:
    """
    Calls the required extraction tools and merges their outputs into
    user_current_capabilities.json blob.
    """
    bundle = {"skills": [], "tools": [], "roles": [], "confidence": 0.0}

    # 1️⃣  call the resume tool (sync → no await)
    if resume_file or resume_text:
        resume_caps = REGISTRY["resume_extract"](user_id, session_id, resume_file, resume_text)
    else:
        resume_caps = {"skills": [], "tools": [], "roles": [], "confidence": 0.0}
    for k in ["skills", "tools", "roles"]:
        bundle[k].extend(resume_caps.get(k, []))

    bundle["skills"] = list(set(bundle["skills"]))
    bundle["tools"] = list(set(bundle["tools"]))
    bundle["roles"] = list(set(bundle["roles"]))
    bundle["confidence"] = resume_caps.get("confidence", 0.8)

    validate_payload("user_current_capabilities.schema.json", bundle)
    await memory.save_blob(user_id, session_id, "user_current_capabilities", bundle)
    return bundle
