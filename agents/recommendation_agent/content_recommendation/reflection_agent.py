# reflection_agent.py (tightened reflection logic)

from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from agent_core.timing_utils import timed_function

@timed_function("Content Reflection")
async def reflect_on_relevance(content_items, focused_subtask, context):
    """Filter for content that helps with task + context.

    Uses a keyword fast-path for obvious matches, then a single batched
    gpt-4o-mini call for the rest (replacing up to 12 individual gpt-4 calls).
    """
    filtered = []
    reflection_log = []

    print("\n📊 Starting content reflection process")
    print(f"Initial content items: {len(content_items)}")

    # Pre-filter based on keywords
    keywords = set([
        *[kw.lower() for kw in focused_subtask.split()],
        *[tool.lower() for tool in context.get('tool_familiarity', [])],
        *[skill.lower() for skill in context.get('missing_skills', [])]
    ])
    print(f"Using keywords: {', '.join(keywords)}")

    pre_filtered = []
    for item in content_items:
        text = f"{item.get('title', '')} {item.get('description', '')} {item.get('snippet', '')}".lower()
        matches = sum(1 for kw in keywords if kw in text)
        if matches > 0:
            item["keyword_matches"] = matches
            pre_filtered.append(item)
            print(f"✓ Pre-filtered: {item.get('title')} ({matches} matches)")
        else:
            print(f"✗ Filtered out: {item.get('title')} (no keyword matches)")

    # Sort by matches and take top 12 for reflection
    pre_filtered.sort(key=lambda x: x.get("keyword_matches", 0), reverse=True)
    content_items = pre_filtered[:12]

    tools = context.get('tool_familiarity', [])
    missing_skills = context.get('missing_skills', [])

    # Separate fast-path items from those needing LLM evaluation
    needs_llm = []
    for item in content_items:
        if any(tool.lower() in item.get('description', '').lower() for tool in tools) or \
           any(skill.lower() in item.get('description', '').lower() for skill in missing_skills):
            item["reflection"] = "Directly relevant based on tools/skills"
            item["format"] = item.get("format", "Post")
            item["description"] = item.get("description") or item.get("snippet", "")
            item["score"] = 1.0
            print(f"✅ Accepted (fast path): {item.get('title')} ({item.get('source')})")
            filtered.append(item)
        else:
            needs_llm.append(item)

    # Batch evaluate remaining items in a single LLM call
    if needs_llm:
        seniority_str = context.get('seniority', '').lower()
        is_senior = any(s in seniority_str for s in ['vp', 'director', 'chief', 'head of', 'principal', 'senior'])
        seniority_note = (
            "IMPORTANT: This person is a senior leader. Reject content that is introductory, "
            "beginner-level, or titled 'Getting started', 'Basics of', 'Intro to', or similar. "
            "They need strategic, advanced, or practitioner-level content."
            if is_senior else ""
        )
        role_str = context.get('role', '') or f"{context.get('seniority', '')} {context.get('domain', '')}".strip()

        items_block = "\n\n".join(
            f"[{i}] Title: {item.get('title')}\n"
            f"    Description: {item.get('description', '')}\n"
            f"    Snippet: {item.get('snippet', '')}"
            for i, item in enumerate(needs_llm)
        )

        batch_prompt = f"""You are an expert AI learning coach evaluating content relevance in bulk.

Learner context:
- Role: {role_str}
- Goal: {context.get('learning_objectives', context.get('aspiration', 'improve AI skills'))}
- Familiar tools: {', '.join(context.get('tool_familiarity', []))}
- Missing skills: {', '.join(context.get('missing_skills', []))}
- AI literacy: {context.get('ai_literacy_signals', 'intermediate')}
- Target persona: {context.get('target_role_archetype', context.get('role', ''))}
{seniority_note}

Task the learner wants to solve: "{focused_subtask}"

Evaluate each content item below. For each, decide:
- YES: directly enables the task given the context
- ADJACENT: related but not sufficient to complete the task
- NO: irrelevant, too generic, or too basic for this person's level

Content items:
{items_block}

Return ONLY a JSON array, one object per item, in the same order:
[{{"index": 0, "decision": "YES", "reason": "short reason"}}, ...]"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": batch_prompt}],
                temperature=0.3,
            )
            raw = response.choices[0].message.content.strip()
            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            decisions = json.loads(raw)
        except Exception as e:
            print(f"Batch reflection failed: {e} — accepting all as ADJACENT")
            decisions = [{"index": i, "decision": "ADJACENT", "reason": "batch eval failed"} for i in range(len(needs_llm))]

        for entry in decisions:
            idx = entry.get("index", 0)
            if idx >= len(needs_llm):
                continue
            item = needs_llm[idx]
            decision = entry.get("decision", "NO").upper()
            reason = entry.get("reason", "")

            reflection_log.append({"title": item.get("title"), "reflection": f"{decision}: {reason}"})

            if decision in ("YES", "ADJACENT"):
                item["reflection"] = f"{decision}: {reason}"
                item["format"] = item.get("format", "Post")
                item["description"] = item.get("description") or item.get("snippet", "")
                item["score"] = 1.0
                print(f"✅ Accepted ({decision}): {item.get('title')} ({item.get('source')})")
                print(f"  Reason: {reason}")
                filtered.append(item)
            else:
                print(f"❌ Rejected: {item.get('title')} ({item.get('source')}) — {reason}")

    return filtered, reflection_log