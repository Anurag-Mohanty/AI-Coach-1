# reflection_agent.py (tightened reflection logic)

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from agent_core.timing_utils import timed_function

@timed_function("Content Reflection", display=True)
async def reflect_on_relevance(content_items, focused_subtask, context):
    """Filter for content that helps with task + context"""
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

    for item in content_items:
        # Accept items that match any of our tools or skills
        if any(tool.lower() in item.get('description', '').lower() for tool in tools) or \
           any(skill.lower() in item.get('description', '').lower() for skill in missing_skills):
            item["reflection"] = "Directly relevant based on tools/skills"
            item["format"] = item.get("format", "Post")
            item["description"] = item.get("description") or item.get("snippet", "")
            item["score"] = 1.0
            print(f"✅ Accepted (fast path): {item.get('title')} ({item.get('source')})")
            filtered.append(item)
            continue


        prompt = f"""
You are an expert AI learning coach helping a product manager upskill through highly specific tasks.

Here is the context of the learner:
- Role: {context['seniority']} in {context['domain']}
- Goal: {context['learning_objectives']}
- Familiar tools: {', '.join(context['tool_familiarity'])}
- Missing skills: {', '.join(context['missing_skills'])}
- AI literacy: {context['ai_literacy_signals']}
- Target persona: {context['target_role_archetype']}

The current task they want to solve is:
"{focused_subtask}"

Here is a piece of content they might consider:
Title: {item.get('title')}
Description: {item.get('description')}
Snippet: {item.get('snippet', '')}

Evaluate the content based on these:
1. Does it *directly* help with the specific task described?
2. Is it appropriate given their tool familiarity and missing skills?
3. Is it specific enough to move the user forward toward task completion?

Respond strictly with one of these tags and a short reason:
- YES: if it directly enables the task given the context.
- ADJACENT: related but not sufficient to complete the task.
- NO: irrelevant or too generic.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=80
            )
            reply = response.choices[0].message.content.strip().lower()
            reflection_log.append({
                "title": item.get('title'),
                "reflection": reply
            })

            # Process reflection response with better parsing
            is_relevant = "yes:" in reply.lower() or "adjacent:" in reply.lower()

            if is_relevant:
                item["reflection"] = reply
                # Ensure all items have required fields
                item["format"] = item.get("format", "Post")
                item["description"] = item.get("description") or item.get("snippet", "")
                item["score"] = 1.0  # Base score for relevant items

                # Add debug info
                print(f"✅ Accepted: {item.get('title')} ({item.get('source')})")
                print(f"  Reason: {reply}")

                filtered.append(item)
            else:
                print(f"❌ Rejected: {item.get('title')} ({item.get('source')})")
                print(f"  Reason: {reply}")
        except Exception as e:
            print("Reflection failed:", e)
            continue

    return filtered, reflection_log