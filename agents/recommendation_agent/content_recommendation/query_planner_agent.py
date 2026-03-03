# query_planner_agent.py

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --------------------------------------------
# Generate atomic search queries from subtask
# --------------------------------------------
from agent_core.timing_utils import timed_function

@timed_function("Query Planning", display=False)
async def generate_search_queries(subtask, context, n=4, print_debug=False):
    seniority = context.get('seniority', '').lower()
    is_senior = any(s in seniority for s in ['vp', 'director', 'chief', 'head of', 'principal', 'senior'])
    seniority_constraint = (
        "- This person is a senior leader (VP/Director/Principal). Do NOT generate beginner tutorial queries. "
        "Focus on strategic application: how AI accelerates executive decisions, team leverage, org-level impact, "
        "and advanced workflows. Avoid 'intro to', 'getting started with', or 'basics of' style queries."
        if is_senior else
        "- Focus on practical, hands-on content — tutorials, walkthroughs, and prompt templates "
        "the user can apply immediately in their daily work."
    )
    org_constraints = context.get('org_constraints', '')
    org_note = f"\n- Org constraints (prefer tools that fit): {org_constraints}" if org_constraints else ""

    # Target role note — generates 1-2 queries specifically at target role level
    target_role = context.get("target_role_archetype", "")
    target_delta = context.get("target_role_delta", "")
    current_role = context.get("role", "")
    target_note = ""
    if target_role and target_role.lower() not in current_role.lower():
        target_note = (
            f"\n- TARGET ROLE: This person is building toward '{target_role}'. "
            f"Generate at least 1-2 queries specifically about AI skills or workflows AT THAT LEVEL — "
            f"not just queries for their current role. "
            f"{'Gap to close: ' + target_delta if target_delta else ''}"
        )

    prompt = f"""
You are an expert research strategist for an AI learning platform.
Your job is to generate {n} smart, focused, platform-searchable queries that can help a user learn how to complete this subtask.

IMPORTANT:
- Do NOT treat the subtask as one single action.
- Instead, imagine a human with the given role, seniority, and tool familiarity performing the subtask in a real-world setting.
- Break that subtask into 3–5 realistic micro-steps someone in this role would take.
- For each micro-step, write ONE distinct query that could help them learn that part.

Subtask:
"{subtask}"

User Context:
- Domain: {context.get('domain', 'N/A')}
- Tools: {', '.join(context.get('tool_familiarity', [])) or 'None'}
- Missing Skills: {', '.join(context.get('missing_skills', [])) or 'None'}
- Seniority: {context.get('seniority', 'N/A')}{org_note}{target_note}

Constraints:
- Every query must be explicitly focused on AI-related workflows, ideally using LLMs, GPT, LangChain, or automation agents, or any AI related concepts or tools.
- Avoid suggesting learning paths based entirely on legacy tools like Excel, Tableau, SQL, or Zendesk.
- If you must mention legacy tools, it should be in the context of how AI integrates with them.
{seniority_constraint}


Each query should sound like something someone would search on YouTube, GitHub, or Google to find:
- Tutorials
- Prompt templates
- Code walkthroughs
- LinkedIn posts
- Real demo content

Avoid vague or academic phrasing. Keep it tactical and grounded in execution.
Each query should reflect a different part of the process — do not repeat phrases or themes.

---
Example:
If the subtask was "Use GPT to summarize 10 Tableau dashboards into business-speak for execs",
the atomic queries could be:
- "Prompt engineering to convert Tableau KPIs to stakeholder summaries"
- "Use GPT to rewrite dashboard metrics into business insights"
- "GPT examples for summarizing healthcare analytics for exec MBRs"
- "LangChain prompts for BI report generation from Tableau"
- "Business storytelling from dashboards using GPT in healthcare"

Reverse anchor:
The kinds of content we hope to surface with these queries include:
- A video showing how GPT-4 rephrases KPIs into plain language
- A GitHub repo with prompt templates for dashboard summarization
- A blog post explaining how to automate MBR slide generation from Tableau
- A LinkedIn post from a PM sharing their workflow for exec-ready reporting
- A tutorial that walks through using GPT with Tableau for insight generation

Design queries that would lead to these results.
---

Return exactly {n} queries, one per line.
Return each query on a new line, no numbering or bullet points.
"""

    try:
        res = client.chat.completions.create(model="gpt-4",
                                             messages=[{
                                                 "role": "user",
                                                 "content": prompt
                                             }],
                                             temperature=0.4,
                                             max_tokens=400)
        queries = [
            q.strip()
            for q in res.choices[0].message.content.strip().split('\n')
            if q.strip()
        ]
        if print_debug:
            print("\n[Query Planner Generated]\n", "\n".join(queries))
        return queries
    except Exception as e:
        print("[Query Planner Error]", e)
        return [subtask]


# Example test
if __name__ == "__main__":
    example_subtask = "Use GPT to convert dashboard metrics into business-speak for healthcare executives"
    example_context = {
        "domain": "healthcare",
        "tool_familiarity": ["GPT-4", "Tableau"],
        "missing_skills": ["prompt chaining", "executive storytelling"],
        "seniority": "Senior Product Manager"
    }
    generate_search_queries(example_subtask, example_context, print_debug=True)