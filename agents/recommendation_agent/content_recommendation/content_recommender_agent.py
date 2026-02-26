# content_recommender_agent.py (now uses retrieval orchestrator + query debugging)

from .retrieval_orchestrator import run_retrieval_orchestrator
from .content_scorer import score_content_item
from .content_explainer import generate_explanation
from agent_core.self_learning import cache_and_reuse
import streamlit as st
from agent_core.timing_utils import track_time, timed_function

# -----------------------------------
# 🧠 Content Recommender Agent Logic (Retrieval Orchestrator Edition)
# -----------------------------------
@timed_function("Content Recommendation", display=True)
async def recommend_learning_content(inputs: dict, linkedin_token=None) -> list:
    subtask = inputs["focused_subtask"]
    st.info(f"🔍 Task: {subtask}")

    # 🔍 1. Orchestrated retrieval + reflection
    curated_items, reflection_log, generated_queries = await run_retrieval_orchestrator(
        subtask,
        inputs,
        user_id="test_user",
        session_id="demo_session",
        print_debug=True,
        return_queries=True
    )

    st.markdown("### 📝 Generated Search Queries")
    for q in generated_queries:
        st.write(f"- {q}")

    st.write(f"🧠 Reflection Agent accepted {len(curated_items)} items for this subtask")

    with st.expander("🔎 Reflection Debug Log"):
        for entry in reflection_log:
            st.markdown(f"**{entry['title']}**\n\n> {entry['reflection']}")

    # 📊 2. Score and explain
    scored_items = []
    st.write(f"Processing {len(curated_items)} curated items...")

    for item in curated_items:
        try:
            item["description"] = item.get("description") or item.get("snippet", "")
            item["format"] = item.get("format", "Post")

            item["score"] = score_content_item(
                item,
                inputs["use_case"],
                inputs["tool_familiarity"],
                inputs["missing_skills"],
                inputs.get("modality_preference", [])
            )

            item["why"] = generate_explanation(item, inputs["use_case"], inputs["missing_skills"])

            st.write(f"✅ Scored {item['title']}: {item['score']}")
            st.write(f"  Why: {item['why']}")

            scored_items.append(item)
        except Exception as e:
            st.warning(f"Failed to score item {item.get('title', 'Unknown')}: {str(e)}")
            import traceback
            st.write(f"Error details: {traceback.format_exc()}")
            continue

    # 🏁 3. Return sorted + cache
    top_items = sorted(scored_items, key=lambda x: x["score"], reverse=True)
    cache_and_reuse(subtask, top_items)
    return top_items


# -----------------------------------
# Optional: Feedback handler
# -----------------------------------
def handle_feedback(content_id: str, was_helpful: bool):
    from agents.recommendation.content_feedback import record_feedback
    from agent_core.feedback_utils import thumbs_up_down
    record_feedback(content_id, was_helpful)
    thumbs_up_down(content_id, was_helpful)