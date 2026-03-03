
# -------------------------------------
# Global Agent Memory Store
# -------------------------------------
import os
import json
from datetime import datetime

_memory_store = {}

# -------------------------------------
# Store a memory snapshot from an agent
# -------------------------------------
async def store_memory(agent_name, user_id, session_id, subtask_id, function, input_fields, output_fields, notes=None):
    if user_id not in _memory_store:
        _memory_store[user_id] = {}
    if session_id not in _memory_store[user_id]:
        _memory_store[user_id][session_id] = {}
        
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "function": function,
        "input_fields": input_fields,
        "output_fields": output_fields,
        "notes": notes
    }
    
    _memory_store[user_id][session_id][subtask_id] = record
    return record

# -------------------------------------
# Get full session context for a user
# -------------------------------------
async def get_context(user_id, session_id):
    if user_id not in _memory_store:
        return {}
    return _memory_store[user_id].get(session_id, {})

# -------------------------------------------------------
# Sync helpers — use these from sync agent code
# -------------------------------------------------------

def get_memory(user_id, session_id):
    """Sync version of get_context."""
    if user_id not in _memory_store:
        return {}
    return _memory_store[user_id].get(session_id, {})


def update_session_context(user_id, session_id, context_dict):
    """Write a structured context dict into session memory.
    Used by prescribe_learning_path to set up the context structure
    that learning_path_agent sub-agents expect to read.
    Merges into existing session data rather than overwriting.
    """
    if user_id not in _memory_store:
        _memory_store[user_id] = {}
    if session_id not in _memory_store[user_id]:
        _memory_store[user_id][session_id] = {}
    _memory_store[user_id][session_id].update(context_dict)


def store_memory_sync(agent_name, user_id, session_id, subtask_id, function, input_fields, output_fields, notes=None):
    """Sync version of store_memory for use in non-async agent code."""
    if user_id not in _memory_store:
        _memory_store[user_id] = {}
    if session_id not in _memory_store[user_id]:
        _memory_store[user_id][session_id] = {}
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "function": function,
        "input_fields": input_fields,
        "output_fields": output_fields,
        "notes": notes,
    }
    _memory_store[user_id][session_id][subtask_id] = record
    return record
