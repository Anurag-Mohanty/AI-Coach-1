
# 📦 Agent Utility Modules — Phase 1
# Located in: /agent_core/

These are shared services for intelligent agents that help them stay smart, self-aware, and collaborative.

## Core Utilities

### 1. Feedback Utils (feedback_utils.py)
Purpose: Capture, store, and analyze user feedback for any agent output.

Used by:
- Resume Agent → thumbs up on parsed title
- Role Detail Agent → correction on task clusters
- Tool Recommender → thumbs down on irrelevant tools

Functions:
- capture_user_feedback(thumbs, corrections, notes)
- store_feedback_locally(agent_name, feedback_dict)
- summarize_feedback_trends(agent_name)
- thumbs_up_down(content_id, was_helpful)

---

### 2. Input Evaluation (input_evaluation.py)
Purpose: Help agents assess input quality and completeness.

Used by:
- Role Detail Agent → detects vague/missing task clusters
- Skill Delta Agent → identifies missing target role
- Learning Path Agent → validates input completeness

Functions:
- validate_inputs(inputs)
- evaluate_input_completeness(output_dict, required_fields)
- detect_missing_context(context_dict)
- score_input_clarity(input_dict)

---

### 3. Agent Logger (agent_logger.py)
Purpose: Log agent runs, errors, and events for monitoring.

Used by:
- All agents for run history and debugging

Functions:
- log_agent_run(agent_name, inputs, outputs)
- log_error(agent_name, error_message)
- log_agent_event(agent_name, event_message)

---

### 4. Self Learning (self_learning.py)
Purpose: Enable agents to learn from feedback and improve.

Used by:
- Resume Agent → adjust prompt strategy
- Role Detail Agent → refine task clusters
- Tool Recommender → adapt suggestions

Functions:
- track_thumbs_up_rate(agent_name, field_name)
- auto_adjust_prompt_if_downvoted(agent_name, field_name)
- log_learning_signal(source_agent, quality_flag)
- suggest_prompt_improvements(agent_name)
- learn_from_feedback(agent, signal, payload)
- cache_and_reuse(subtask, items)

---

### 5. Downstream Formatter (downstream_formatter.py)
Purpose: Format agent outputs for downstream consumption.

Used by:
- Role Detail Agent → feeds Skill Delta
- Resume Agent → feeds Role Context
- Learning Path Agent → feeds Content Recommender

Functions:
- format_for_agent(agent_name, full_output_dict)
- standardize_payload_structure(output_dict, required_fields)
- tag_downstream_fields(fields_dict)

---

### 6. Trust Explainability (trust_explainability.py)
Purpose: Make agent decisions transparent and understandable.

Used by:
- All agents to explain their reasoning

Functions:
- generate_why_this_output_summary(agent_name, input_summary, rules_used, model_confidence)
- highlight_confidence_levels(fields_dict)
- display_reasoning_path(agent_name, intermediate_steps)
- offer_counterfactuals(field_name, alternative_value, potential_change)

---

### 7. Global Agent Memory (global_agent_memory.py)
Purpose: Share context across agent runs and sessions.

Used by:
- Learning Path Agent → recalls previous paths
- Content Recommender → shares discoveries
- All agents for context persistence

Functions:
- store_memory(agent_name, user_id, session_id, subtask_id, function, input_fields, output_fields)
- retrieve_memory(agent_name, user_id, session_id, subtask_id)
- get_context(user_id, session_id)
- record_feedback(agent_name, user_id, session_id, subtask_id, content_id, rating)
- merge_contexts(base_context, memory_context)
- summarize_history(agent_name, user_id, limit)

---

### 8. Content Cache (content_cache.py)
Purpose: Cache and retrieve content with metadata indexing.

Used by:
- Content Recommender → stores search results
- Learning Path Agent → caches learning paths
- Retrieval Orchestrator → manages content

Functions:
- store_content(items, metadata, subtask)
- store_feedback(content_id, was_helpful)
- search_cached_content(query_metadata, subtask, limit)
- get_feedback_score(content_id)
- update_content_metadata(content_id, metadata)
- get_content_by_id(content_id)

---

### 9. Timing Utils (timing_utils.py)
Purpose: Track and optimize agent execution times.

Used by:
- All agents for performance monitoring
- Retrieval orchestrator for API timing

Functions:
- track_time(category, display)
- timed_function(category, display)
- TimingStats.record(category, duration, function_name)
- TimingStats.get_stats(category)

---

### 10. Compliance Utils (compliance_utils.py)
Purpose: Handle data privacy and regulatory compliance.

Used by:
- Resume Agent → Remove PII
- Role Context Agent → Hash sensitive data
- All agents for data protection

Functions:
- remove_personally_identifiable_info(text)
- hash_input_data(input_str)
- log_data_usage_consent(user_id)
- forget_user_data(user_id)
- validate_learning_path(modules)
- validate_content(content)

---

### 11. Persona Context (persona_context.py)
Purpose: Maintain user profile and preferences.

Used by:
- Aspiration Agent → stores goals
- Resume/LinkedIn Agent → updates context
- Cultural Agent → uses preferences

Functions:
- get_user_context(user_id)
- update_shared_context(user_id, new_payload)
- infer_missing_context(user_context)
- notify_agents_of_major_context_shift(user_id, change_fields)

---

### 12. Dashboard Hooks (dashboard_hooks.py)
Purpose: Enable agent monitoring and insights.

Used by:
- Admin dashboard → tracks performance
- Meta agent → scores agents
- Developer view → flags issues

Functions:
- get_agent_health_snapshot(agent_name)
- return_last_run_timestamp(agent_name)
- return_feedback_score_avg(agent_name)
- flag_if_confidence_dropping(agent_name)

---

### 13. Test Tools (test_tools.py)
Purpose: Support agent testing and simulation.

Used by:
- Resume Agent → test parsing
- Role Detail Agent → simulate inputs
- All agents for debugging

Functions:
- mock_upstream_context(role_title)
- simulate_downstream_usage(output_dict)
- auto_generate_edge_case_inputs()
- visualize_agent_io_path(agent_name, inputs, outputs)

