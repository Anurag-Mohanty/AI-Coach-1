"""
generate_use_cases tool — surfaces 3 structured AI blind spots for a given role.

When task_clusters are available (from infer_role_detail), passes them to
use_case_miss_agent.find_ai_blind_spots() for grounded, effort-weighted use cases.
Falls back to the LLM prompt approach when task_clusters are not yet available.
"""
import json
import os
import re
import time

from openai import OpenAI
from agents.gap_analysis_agent.use_case_miss_agent import find_ai_blind_spots
from agent_core.session_trace import record_event

# Phase C — role archetype store for retrieved blind spot priors
try:
    from coach.intelligence.archetype_store import RoleArchetypeStore
    _archetype_store = RoleArchetypeStore()
except Exception:
    _archetype_store = None

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_PROMPT = """You are an AI productivity coach generating highly specific, realistic AI use cases.

User profile:
- Role: {seniority} {title}
- Company: {company}
- Domain: {domain}
- Tools they use: {tools_str}
- What they're trying to accomplish: {aspiration}
- Org/tool constraints: {org_constraints}
- Task breakdown:{task_clusters_str}

SENIORITY-AWARE FRAMING (this changes everything):
Seniority: {seniority}

For VP / Director / Head of / Principal:
- Use cases must be about STRATEGIC DECISIONS and ORG LEVERAGE — not writing faster or saving time on individual tasks.
- At this level, "roadmap prioritization" means: using AI to synthesize signals from multiple competing product areas, model portfolio tradeoffs, and align executive stakeholders — not drafting a document.
- Each use case should answer: "What decision cycle does AI compress? What org-level complexity does AI cut through?"
- Bad example: "Use Copilot to write the roadmap document" — this is a PM task, not a VP task.
- Good example: "Use AI to synthesize conflicting signals from 4 product lines and produce a portfolio recommendation with tradeoff analysis in hours instead of weeks."

For Manager / Senior IC:
- Use cases should be about practitioner depth and craft elevation — how AI makes them better at their specific domain skills.

For mid-level IC:
- Use cases should be immediate productivity wins — specific tasks that shrink from hours to minutes.

Apply the framing that matches "{seniority}".

{target_role_block}
CRITICAL ROLE OWNERSHIP CHECK:
Product Managers own: roadmap prioritization, requirements gathering, stakeholder alignment, market/competitive research, go-to-market strategy, product discovery, customer insight synthesis, product communications (PRDs, briefs, decks).
Product Managers do NOT own: software testing, code deployment, change request tracking, IT infrastructure, QA automation, DevOps pipelines, system maintenance.
Every use case you generate must be something the {title} personally does — not something their engineering team does.

ASPIRATION-FIRST FRAMING:
The user's goal is: {aspiration}
For each use case, you must be able to answer: "How does this use case help {seniority} {title} achieve that goal?"
- If the goal is promotion/leadership: frame use cases around building strategic visibility, demonstrating AI fluency, or freeing time for higher-leverage work
- If the goal is efficiency: frame around the biggest time drains in the task clusters
Lead with the use case most directly connected to their aspiration.

Generate exactly 3 AI use cases. Each must:
- Map to a real task cluster listed above
- Be specific to THIS person's role, company, and domain — not generic advice
- Respect their org/tool constraints exactly
- Connect clearly to their stated aspiration

For each use case, return a JSON object with:
- "title": Short, specific name (5-8 words) — name the actual task being transformed
- "task": The specific manual thing they do today (1 sentence, present tense, concrete — NOT generic)
- "ai_opportunity": How AI changes this (1-2 sentences — name the specific tool and specific action)
- "time_saved_pct": Conservative time estimate (integer 0-60)
- "suggested_tool": One specific tool within their approved constraints
- "aspiration_connection": One sentence — how this use case helps them achieve their stated goal

Return a JSON array of exactly 3 objects. No other text."""


def generate_use_cases(
    title: str,
    seniority: str = "",
    domain: str = "",
    tools_known: list = None,
    aspiration: str = "",
    org_constraints: str = "",
    company: str = "",
    task_clusters: list = None,
    session_id: str = None,
    aspiration_structured: dict = None,
    archetype_id: str = None,
) -> list:
    """
    Generate 3 structured AI use cases for a given role.

    When task_clusters are provided, routes through use_case_miss_agent.find_ai_blind_spots()
    for grounded use cases. Falls back to direct LLM prompt when task_clusters are absent.

    aspiration_structured (from interpret_aspiration) enriches use cases with target role
    context — company type, domain, and org context — so use cases are bridge framing
    (practice target role skills at current scope) rather than current-role optimization.

    Input:  role context fields + optional task_clusters + optional aspiration_structured
    Output: list of 3 use case dicts
    """
    tools_str = ", ".join((tools_known or [])[:10]) or "standard office tools"

    def _trace(agent, inputs, outputs, duration_ms, status="ok", error=None):
        if session_id:
            record_event(session_id, phase="reveal", agent=agent,
                         inputs=inputs, outputs=outputs,
                         duration_ms=duration_ms, status=status, error=error)

    # Build aspiration context dict for downstream agents
    asp = aspiration_structured or {}
    aspiration_ctx = {
        "target_role_archetype": asp.get("target_role_archetype", ""),
        "target_company_type":   asp.get("target_company_type", ""),
        "target_domain":         asp.get("target_domain", ""),
        "target_org_context":    asp.get("target_org_context", ""),
        "aspiration_category":   asp.get("aspiration_category", ""),
        "role_delta_summary":    asp.get("role_delta_summary", ""),
        "domain_shift_signal":   asp.get("domain_shift_signal", False),
    }

    # Path A: task clusters available — use the specialist agent
    if task_clusters:
        role_context = {
            "role_archetype": f"{seniority} {title}".strip(),
            "company": company or "their company",
            "domain": domain or "their industry",
            "org_shape": "enterprise" if company else "unknown",
            "ai_applicability_constraints": org_constraints or "standard enterprise caution",
            **aspiration_ctx,
        }

        # Phase C: fetch retrieved blind spot priors from archetype store if archetype_id known
        retrieved_patterns = []
        if archetype_id and _archetype_store:
            archetype = _archetype_store.get(archetype_id)
            if archetype:
                retrieved_patterns = archetype.get("common_blind_spots", [])
                if retrieved_patterns:
                    print(f"[generate_use_cases] Injecting {len(retrieved_patterns)} archetype priors for {archetype_id}")

        cluster_summary = [f"{c.get('name')} ({c.get('effort_pct')}%)" for c in task_clusters[:5]]
        t0 = time.time()
        blind_spots = find_ai_blind_spots(
            task_clusters, role_context,
            aspiration_context=aspiration_ctx,
            retrieved_patterns=retrieved_patterns or None,
        )
        _trace(
            agent="find_ai_blind_spots",
            inputs={"role": f"{seniority} {title}", "company": company, "domain": domain,
                    "task_clusters": cluster_summary, "aspiration": (aspiration or "")[:80],
                    "constraints": (org_constraints or "")[:80],
                    "target_role": aspiration_ctx.get("target_role_archetype", "")},
            outputs={"blind_spots": [b.get("task_cluster") for b in blind_spots[:3]],
                     "spot_0": (blind_spots[0].get("blind_spot", "") if blind_spots else None)},
            duration_ms=int((time.time() - t0) * 1000),
            status="error" if any("error" in str(b) for b in blind_spots) else "ok",
        )

        if blind_spots and not any("error" in str(b) for b in blind_spots):
            t1 = time.time()
            result = _synthesize_use_cases(
                blind_spots=blind_spots,
                title=title,
                seniority=seniority,
                company=company,
                domain=domain,
                tools_str=tools_str,
                aspiration=aspiration,
                org_constraints=org_constraints,
                task_clusters=task_clusters,
                aspiration_structured=aspiration_structured,
            )
            _trace(
                agent="synthesize_use_cases",
                inputs={"blind_spots": [b.get("task_cluster") for b in blind_spots[:3]]},
                outputs={"use_case_count": len(result),
                         "titles": [uc.get("title") for uc in result[:3]]},
                duration_ms=int((time.time() - t1) * 1000),
            )
            return result

    # Path B: no task clusters — direct LLM prompt
    _trace("generate_use_cases_path", {"path": "B — no task_clusters, using direct LLM"}, {}, 0, "skip")
    return _generate_direct(
        title=title,
        seniority=seniority,
        company=company,
        domain=domain,
        tools_str=tools_str,
        aspiration=aspiration,
        org_constraints=org_constraints,
        task_clusters=task_clusters,
        aspiration_structured=aspiration_structured,
    )


def _synthesize_use_cases(
    blind_spots: list,
    title: str,
    seniority: str,
    company: str,
    domain: str,
    tools_str: str,
    aspiration: str,
    org_constraints: str,
    task_clusters: list,
    aspiration_structured: dict = None,
) -> list:
    """
    Take blind spots from use_case_miss_agent and synthesize into final use case format.
    Uses GPT-4o to add specificity (tools, time estimates, concrete task descriptions).
    aspiration_structured enriches use cases with target role/company/org context.
    """
    blind_spots_str = json.dumps(blind_spots, indent=2)
    task_clusters_str = _format_task_clusters(task_clusters)

    is_senior = any(s in seniority.lower() for s in ["vp", "director", "chief", "head of", "principal", "senior"])
    seniority_instruction = (
        f"""
SENIORITY FRAMING (critical for {seniority}):
This person operates at a strategic/leadership level. Their use cases must reflect that.
- Do NOT frame use cases as "do [task] faster" or "write [document] with AI assistance."
- DO frame use cases as: "Use AI to make [strategic decision] in [days] instead of [weeks]" or "Use AI to synthesize [complex signals] and produce [leadership-ready output]."
- The ai_opportunity field should describe a decision cycle compression, not a document generation task.
- The title should name the DECISION or STRATEGIC CAPABILITY, not the task.
- Bad: "Streamlined Roadmap Document Creation" — Good: "AI-Powered Portfolio Prioritization"
- Bad ai_opportunity: "Use Copilot to draft the roadmap" — Good: "Use Copilot to synthesize input from 5 competing workstreams and generate a ranked portfolio recommendation with tradeoff analysis."
"""
        if is_senior else ""
    )

    # Build target role block from aspiration_structured
    asp = aspiration_structured or {}
    target_role = asp.get("target_role_archetype", "")
    target_company_type = asp.get("target_company_type", "")
    target_org_context = asp.get("target_org_context", "")
    aspiration_category = asp.get("aspiration_category", "")
    role_delta = asp.get("role_delta_summary", "")
    target_role_label = f"{target_role} at {target_company_type}".strip(" at") if target_company_type else target_role

    if target_role:
        target_role_block = f"""
TARGET ROLE — critical: changes how "task", "ai_opportunity", and "aspiration_connection" are written:
Building toward: {target_role_label}
What that role actually looks like: {target_org_context or 'not specified'}
Transition type: {aspiration_category or 'career growth'} | Gap to close: {role_delta or 'not specified'}

IMPORTANT: The use case framing must reflect what a {target_role_label} actually does — not a
generic {target_role}. The org type and domain define the decision context, org complexity,
and constraints this person will operate under.

COACHING PHILOSOPHY: The use case is a BRIDGE — not current-role optimization, not target-role
simulation. Practice target role capabilities within current role scope, using AI to elevate depth.

"task" field — Bridge framing (REQUIRED): Both current reality AND the target gap in one sentence.
  Show where they are AND what they're building toward, so the use case feels directional.
  Example: "You manage one product roadmap today — but a {target_role_label} synthesizes across
  4+ lines under {target_company_type or 'org'} constraints. AI closes that gap right now."
  NOT: "You're a {target_role} running portfolio decisions." (fictional — they aren't there yet)
  NOT: "You prioritize one product's roadmap." (no direction, no pull toward target)

"ai_opportunity" field: Show how AI enables practicing at {target_role_label} depth within current scope.
  What does doing this with AI teach them that they need at that level?
  Example: "Use Copilot to simulate portfolio-level synthesis: pull signals from adjacent products,
  model tradeoffs as if you owned all of them. Same mental model a {target_role} uses —
  your current scope as the training ground."
  NOT: "Use Copilot to write the doc faster." (no skill development toward target role)

"aspiration_connection" field: Name the specific target-role muscle being built.
  Example: "{target_role_label} runs on exactly this synthesis skill at 4x the complexity.
  Doing it now with AI means when your scope expands, the pattern is already muscle memory."
  NOT: "This helps you get promoted." (too generic — name the SPECIFIC muscle)
"""
    else:
        target_role_block = ""

    prompt = f"""You are an AI productivity coach. You have identified these AI blind spots for a {seniority} {title}:

{blind_spots_str}

User context:
- Company: {company or 'their company'}
- Domain: {domain or 'their domain'}
- Tools: {tools_str}
- Goal: {aspiration or 'not specified — use best judgment'}
- Org constraints: {org_constraints or 'standard enterprise caution'}
- Task breakdown:{task_clusters_str}
{seniority_instruction}{target_role_block}
CRITICAL: This person is a {title}. Every use case must be something THEY personally do — not their engineering team.
Product Managers own: roadmap/backlog work, stakeholder alignment, market research, requirements, product communications.
They do NOT own: software testing, deployments, change request management, IT infrastructure.

For each use case, add "aspiration_connection": one sentence on how it helps them toward their goal ({aspiration or 'career advancement'}).

Convert these blind spots into exactly 3 polished AI use cases. Return a JSON array of exactly 3. No other text.
Each object: title, task, ai_opportunity, time_saved_pct (0-60), suggested_tool, aspiration_connection."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI productivity expert. Return only valid JSON arrays."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        content = response.choices[0].message.content.strip()
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
        return json.loads(content.strip())
    except Exception as e:
        # Fall back to direct generation
        return _generate_direct(
            title=title, seniority=seniority, company=company, domain=domain,
            tools_str=tools_str, aspiration=aspiration, org_constraints=org_constraints,
            task_clusters=task_clusters, aspiration_structured=aspiration_structured,
        )


def _generate_direct(
    title: str,
    seniority: str,
    company: str,
    domain: str,
    tools_str: str,
    aspiration: str,
    org_constraints: str,
    task_clusters: list,
    aspiration_structured: dict = None,
) -> list:
    """Direct LLM generation — used when task_clusters are absent."""
    task_clusters_str = _format_task_clusters(task_clusters) if task_clusters else "\n  (task clusters not yet available)"

    # Build target role block for Path B
    asp = aspiration_structured or {}
    target_role = asp.get("target_role_archetype", "")
    target_company_type = asp.get("target_company_type", "")
    target_org_context = asp.get("target_org_context", "")
    aspiration_category = asp.get("aspiration_category", "")
    role_delta = asp.get("role_delta_summary", "")
    target_role_label = f"{target_role} at {target_company_type}".strip(" at") if target_company_type else target_role

    if target_role:
        target_role_block = f"""TARGET ROLE — critical context for use case framing:
Building toward: {target_role_label}
What that role actually looks like: {target_org_context or 'not specified'}
Transition type: {aspiration_category or 'career growth'} | Gap to close: {role_delta or 'not specified'}

COACHING PHILOSOPHY: Each use case is a BRIDGE — practice target role capabilities within
current role scope, using AI to elevate the depth of practice.
"task" field: Bridge framing — current reality AND target gap in one sentence.
"ai_opportunity": How AI enables practicing at {target_role_label} depth within current scope.
"aspiration_connection": Name the specific {target_role} muscle being built — not "helps get promoted."

"""
    else:
        target_role_block = ""

    prompt = _PROMPT.format(
        title=title or "professional",
        seniority=seniority or "mid-level",
        company=company or "their company",
        domain=domain or "their domain",
        tools_str=tools_str,
        aspiration=aspiration or "not yet captured — use best judgment based on their role",
        org_constraints=org_constraints or "not yet captured — assume standard enterprise caution",
        task_clusters_str=task_clusters_str,
        target_role_block=target_role_block,
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an AI productivity expert. Return only valid JSON arrays."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )
        content = response.choices[0].message.content.strip()
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
        return json.loads(content.strip())
    except Exception as e:
        return [{"error": str(e), "title": "Use case generation failed"}]


def _format_task_clusters(task_clusters: list) -> str:
    if not task_clusters:
        return "\n  (none available)"
    lines = []
    for c in task_clusters:
        name = c.get("name", "Task")
        effort = c.get("effort_pct", "?")
        opp = c.get("ai_opportunity", "")
        lines.append(f"\n  • {name}: {effort}% of time — AI opportunity: {opp}")
    return "".join(lines)
