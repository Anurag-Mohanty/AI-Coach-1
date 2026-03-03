from openai import OpenAI
import os
import json
from agent_core.agent_logger import log_agent_event

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_learning_steps(context, return_structured_output=False):
    curated = context.get("content", {}).get("curated_training", [])
    subtask = context.get("subtask", {})
    use_case = context.get("use_case", {})

    if not curated:
        return "No learning steps available."

    # === Step 1: Order the trainings to build toward the subtask (gpt-4o-mini — simple ordering) ===
    sequencing_prompt = f"""You are helping a user learn how to accomplish the following subtask:
"{subtask.get('title')}"

Available trainings:
{chr(10).join(f"- {item['title']}" for item in curated)}

Determine the best order to present these trainings so the user can successfully complete the subtask.
Return ONLY the titles, in order, as a numbered list."""

    try:
        ordering_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a thoughtful learning path planner. Output a numbered list of training titles."},
                {"role": "user", "content": sequencing_prompt.strip()},
            ],
        )
        ordered_titles = [
            line.strip().split(". ", 1)[-1]
            for line in ordering_response.choices[0].message.content.strip().splitlines()
            if line.strip()
        ]
    except Exception:
        ordered_titles = [item["title"] for item in curated]

    # Resolve ordered items, preserving any titles that didn't match exactly
    ordered_items = []
    for title in ordered_titles:
        item = next((x for x in curated if x["title"] == title), None)
        if item:
            ordered_items.append(item)
    # Append any curated items that didn't appear in the ordering output
    seen = {id(x) for x in ordered_items}
    for item in curated:
        if id(item) not in seen:
            ordered_items.append(item)

    # === Step 2: Batch narration — one gpt-4o call for all items ===
    ai_opportunity = use_case.get("ai_opportunity", "")
    aspiration_connection = use_case.get("aspiration_connection", "")
    persona_role = context.get("persona", {}).get("role", "")
    persona_domain = context.get("persona", {}).get("domain", "")
    aspiration_target = context.get("aspiration", {}).get("target_role_archetype", "")

    items_block = "\n\n".join(
        f"[{i}] \"{item['title']}\""
        for i, item in enumerate(ordered_items)
    )

    batch_narration_prompt = f"""You are an expert AI learning coach writing personalized training descriptions.

About the learner:
- Role: {persona_role}{f' in {persona_domain}' if persona_domain else ''}
- Aspiration: {aspiration_target or 'advance their career'}
- Use case: "{use_case.get('title')}"
- Learning to: {ai_opportunity}
- Why it matters: {aspiration_connection}

For each resource below, write exactly two sentences in second person:
1. What the learner will concretely be able to DO after this resource (specific to the resource title)
2. How this directly helps them {ai_opportunity[:80] if ai_opportunity else 'complete the use case'} — connect to their goal of {aspiration_target or 'career advancement'}

Be concrete. No generic phrases. Name the actual capability gained.

Resources:
{items_block}

Return ONLY a JSON array, one object per resource, in the same order:
[{{"index": 0, "description": "sentence 1", "impact": "sentence 2"}}, ...]"""

    try:
        narration_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You generate focused, subtask-aware training descriptions. Return JSON only."},
                {"role": "user", "content": batch_narration_prompt.strip()},
            ],
            temperature=0.4,
        )
        raw = narration_response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        narrations = json.loads(raw)
    except Exception as e:
        log_agent_event("LearningStepsAgent", f"Batch narration failed: {e} — using empty narrations")
        narrations = [{"index": i, "description": "", "impact": ""} for i in range(len(ordered_items))]

    # Index narrations by position for fast lookup
    narration_map = {entry.get("index", i): entry for i, entry in enumerate(narrations)}

    # === Step 3: Assemble step blocks ===
    steps_md = ["\U0001F6E0️ **Your Step-by-Step Learning Journey**\n"]
    structured_steps = []

    for i, item in enumerate(ordered_items, 1):
        narration = narration_map.get(i - 1, {})
        description = narration.get("description", "")
        impact = narration.get("impact", "")

        duration_str = item.get("duration", "") or ""
        link_str = item.get("link", "") or ""
        source_str = item.get("source", "") or ""

        duration_display = f" — {duration_str}" if duration_str else ""
        link_display = f"\n🔗 [{link_str}]({link_str})" if link_str else ""

        if description:
            block = (
                f"▶️ **Step {i}: {item['title']}**{duration_display}"
                f"{link_display}\n"
                f"{description}\n"
                f"🧠 Why this matters for you: {impact}"
            )
        else:
            block = f"▶️ **Step {i}: {item['title']}**{duration_display}{link_display}"

        steps_md.append(block)
        structured_steps.append({
            "step": i,
            "title": item["title"],
            "description": description,
            "why_it_matters": impact,
            "link": link_str,
            "duration": duration_str,
            "source": source_str,
        })

    if return_structured_output:
        return {"narrative": "\n\n".join(steps_md), "steps": structured_steps}

    return "\n\n".join(steps_md)
