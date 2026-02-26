from openai import OpenAI
import os
from agent_core.global_agent_memory import store_memory, get_context
from agent_core.self_learning import learn_from_feedback
from agent_core.feedback_utils import capture_feedback
from agent_core.trust_explainability import explain_why_included
from agent_core.agent_logger import log_agent_event

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_learning_steps(context, return_structured_output=False):
    curated = context.get("content", {}).get("curated_training", [])
    query_plan = context.get("content", {}).get("query_plan", [])
    subtask = context.get("subtask", {})
    use_case = context.get("use_case", {})
    user_id = context.get("user_id")
    session_id = context.get("session_id")
    subtask_id = context.get("subtask_id")

    if not curated:
        return "No learning steps available."

    # === Step 1: Order the trainings to build toward the subtask ===
    sequencing_prompt = f"""
You are helping a user learn how to accomplish the following subtask:
"{subtask.get('title')}"

Available trainings:
{chr(10).join(f"- {item['title']}" for item in curated)}

Determine the best order to present these trainings so the user can successfully complete the subtask. 
Return ONLY the titles, in order, as a numbered list.
"""

    try:
        ordering_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role":
                "system",
                "content":
                "You are a thoughtful learning path planner. Your output is a numbered list of training titles."
            }, {
                "role": "user",
                "content": sequencing_prompt.strip()
            }])
        ordered_titles = [
            line.strip().split(". ", 1)[-1] for line in
            ordering_response.choices[0].message.content.strip().splitlines()
            if line.strip()
        ]
    except Exception:
        ordered_titles = [item["title"] for item in curated]

    # === Step 2: Build narrative blocks ===
    steps_md = ["\U0001F6E0️ **Your Step-by-Step Learning Journey**\n"]
    structured_steps = []

    for i, title in enumerate(ordered_titles, 1):
        item = next((x for x in curated if x["title"] == title), None)
        if not item:
            continue

        narration_prompt = f"""
You are an expert AI learning coach.
Help a user master the subtask: \"{subtask.get('title')}\"
That contributes to this broader use case: \"{use_case.get('title')}\"

You are about to include a training called "{item['title']}".

This training was also selected by a reflection agent for the following reason:
{context.get('content', {}).get('reflection_summary', '')}

Write exactly two informative, specific sentences, written in second person (you/your):
1. What the learner will concretely do or gain in this training
2. How it directly helps them complete the subtask (and indirectly supports the broader use case)
Be clear and concise. Avoid generic phrasing. Keep it subtask-aware and written in the tone of a mentor guiding the learner.
"""

        try:
            narration_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role":
                    "system",
                    "content":
                    "You generate highly focused subtask-aware training descriptions. Respond in 2 sentences."
                }, {
                    "role": "user",
                    "content": narration_prompt.strip()
                }])
            narration = narration_response.choices[0].message.content.strip()
            lines = narration.split("\n")
            description = lines[0].lstrip("1234567890. ").strip()
            impact = lines[1].lstrip("1234567890. ").strip() if len(
                lines) > 1 else ""

            block = f"""▶️ **Step {i}: {item['title']}**  
📺 {item['title']} — {item['duration']}  
{description}  
🧠 Why this matters: {impact}"""
            steps_md.append(block)

            structured_steps.append({
                "step": i,
                "title": item["title"],
                "description": description,
                "why_it_matters": impact,
                "link": item.get("link"),
                "duration": item.get("duration"),
                "source": item.get("source")
            })

            store_memory(agent="LearningStepsAgent",
                         user_id=user_id,
                         session_id=session_id,
                         subtask_id=subtask_id,
                         function="training_step_narration",
                         input_fields={"title": title},
                         output_fields={
                             "description": description,
                             "why": impact
                         })

            capture_feedback(agent="LearningStepsAgent",
                             content_id=f"step-{i}-{title}",
                             rating=None,
                             subtask_id=subtask_id)

            explain_why_included(agent="LearningStepsAgent",
                                 user_id=user_id,
                                 content_title=title,
                                 reason=impact)

        except Exception:
            fallback = f"▶️ **Step {i}: {title}**\n📺 {item['title']} — {item.get('duration')} (no narration available)"
            steps_md.append(fallback)
            structured_steps.append({
                "step": i,
                "title": item["title"],
                "description": "N/A",
                "why_it_matters": "N/A",
                "link": item.get("link"),
                "duration": item.get("duration"),
                "source": item.get("source")
            })

    if return_structured_output:
        return {"narrative": "\n\n".join(steps_md), "steps": structured_steps}

    return "\n\n".join(steps_md)
