
import json
import os
import re
from openai import OpenAI

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

_BLIND_SPOT_PROMPT = """You are an AI opportunity analyst identifying where AI is underused.

Role context:
- Role: {role_archetype}
- Company: {company}
- Industry/Domain: {domain}
- Org shape: {org_shape}
- Approved AI tools (constraints): {ai_constraints}

Task clusters for this role (what they actually spend time on):
{task_clusters}

SENIORITY-AWARE FRAMING (critical):
Examine "{role_archetype}" — the seniority changes what "AI opportunity" means entirely:

For VP / Director / Head of / Principal level:
- AI opportunity is NOT about task automation or writing documents faster.
- It IS about: compressing decision cycles, synthesizing signals across org complexity, running portfolio-level scenario analysis, and reducing the time from "I need to decide" to "I have a defensible recommendation with stakeholder alignment."
- The blind spot for a VP is: "they spend 2-3 weeks building consensus for a decision that AI could help them frame, pressure-test, and pre-align in 3 days."
- Frame each blind spot as: what DECISION or STRATEGIC JUDGMENT does AI accelerate at this level?

For Manager / Senior IC level:
- AI opportunity is about individual productivity and team efficiency.
- The blind spot is specific tasks they currently do manually that AI compresses from hours to minutes.

Apply the correct framing based on the seniority detected in "{role_archetype}".

{target_role_block}{prior_knowledge_block}
Find the 3 specific AI blind spots — clusters where AI creates the most leverage at their level.
Prioritize clusters with effort_pct >= 15% and ai_opportunity = "high" or "medium".

CRITICAL — be specific to {company} in {domain}. Name the ACTUAL friction at this type of organization:
- Healthcare insurer: regulatory sign-off from clinical, actuarial, and compliance extends every decision cycle
- Large enterprise: approval chains, change-advisory boards, procurement timelines slow AI adoption
- Startup: no friction — AI adoption is instant but scaling is the challenge
Do NOT write generic observations. Name the specific mechanism.

Respect the approved AI tools — only suggest tools from the constraints list. If Microsoft 365 Copilot is approved, lead with that.

For each blind spot return:
- "task_cluster": exact name from the list above
- "blind_spot": the specific friction or decision bottleneck most amenable to AI (1 sentence, very concrete — name the {company}-specific mechanism)
- "ai_opportunity": exactly how AI changes this (1-2 sentences — name the specific approved tool, the specific action, and what decision cycle or friction is eliminated)
- "effort_pct": the effort_pct value from above

Return a JSON array of exactly 3 objects. No other text."""


def find_ai_blind_spots(
    task_clusters: list,
    role_context: dict,
    aspiration_context: dict = None,
    retrieved_patterns: list = None,
) -> list:
    """
    Find AI blind spots in a role's task clusters using LLM analysis.
    Input:  task_clusters       — list of {name, effort_pct, ai_opportunity}
            role_context        — dict with role_archetype, org_shape, ai_applicability_constraints
            aspiration_context  — optional dict with target role info (enriches blind spot framing)
            retrieved_patterns  — optional list of common_blind_spots from archetype store;
                                  injected as priors so LLM confirms/refines rather than derives from scratch
    Output: list of 3 blind spot dicts
    """
    clusters_str = "\n".join([
        f"- {c.get('name', 'Task')}: {c.get('effort_pct', '?')}% of time, "
        f"AI opportunity: {c.get('ai_opportunity', 'unknown')}"
        for c in (task_clusters or [])
    ])

    # Build target role block if aspiration context is available
    asp = aspiration_context or {}
    target_role = asp.get("target_role_archetype", "")
    target_company_type = asp.get("target_company_type", "")
    target_org_context = asp.get("target_org_context", "")
    target_domain = asp.get("target_domain", "")
    aspiration_category = asp.get("aspiration_category", "")
    role_delta = asp.get("role_delta_summary", "")

    if target_role:
        target_role_label = f"{target_role} at {target_company_type}".strip(" at") if target_company_type else target_role
        target_role_block = f"""TARGET ROLE (what this person is building toward):
- Target: {target_role_label}
- What that role actually looks like: {target_org_context or 'not specified'}
- Target domain: {target_domain or 'same as current'}
- Transition type: {aspiration_category or 'not specified'}
- Key gap to close: {role_delta or 'not specified'}

COACHING PHILOSOPHY — how to frame each blind spot:
Learning happens by practicing TARGET ROLE capabilities within current role scope — not by
simulating the target role, and not just by optimizing the current role faster.

The blind spot should answer: "What target role capability lives inside this current task cluster,
and how can AI let them practice it NOW at current scale?"

For a PM at Cigna targeting VP of Product at a healthcare startup:
  BAD blind_spot: "Writing PRDs takes 3 hours" (current friction — builds nothing new)
  BAD blind_spot: "You'll be making portfolio decisions across 3 product lines" (fictional VP work)
  GOOD blind_spot: "Your single-product roadmap work is the entry point for the portfolio synthesis
    a {target_role_label} runs daily. AI can let you practice that thinking now — same mental model,
    your current scope as the training ground."
  GOOD ai_opportunity: "Use Copilot to simulate portfolio-level prioritization: pull signals from
    adjacent products, model tradeoffs, and produce a recommendation as if you owned all of them.
    You're building the {target_role} synthesis muscle within your current scope."

Frame: current task = entry point → target skill = destination → AI = bridge

"""
    else:
        target_role_block = ""

    # Build prior knowledge block from archetype store retrieved patterns (Phase C)
    if retrieved_patterns:
        priors_text = "\n".join(
            f"  • [{p.get('task_cluster', '?')}] {p.get('blind_spot', '')} → {p.get('ai_opportunity', '')}"
            for p in retrieved_patterns[:3]
        )
        session_count_note = f" across users in similar roles"
        prior_knowledge_block = f"""
PRIOR KNOWLEDGE (from intelligence gathered{session_count_note}):
These patterns were identified as common blind spots for this type of role:
{priors_text}

IMPORTANT: Validate these priors against THIS user's specific context ({role_context.get('company', 'their company')},
{role_context.get('domain', 'their domain')}, their org constraints). Personalize — do NOT just repeat them.
If a prior applies, confirm and sharpen it with company-specific detail.
If a prior doesn't apply, replace it with a more accurate blind spot for this specific user.

"""
    else:
        prior_knowledge_block = ""

    prompt = _BLIND_SPOT_PROMPT.format(
        role_archetype=role_context.get("role_archetype", "professional"),
        company=role_context.get("company", "their company"),
        domain=role_context.get("domain", "their industry"),
        org_shape=role_context.get("org_shape", "enterprise"),
        ai_constraints=role_context.get("ai_applicability_constraints", "standard enterprise caution"),
        task_clusters=clusters_str or "No task clusters provided",
        target_role_block=target_role_block,
        prior_knowledge_block=prior_knowledge_block,
    )

    try:
        response = _client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Return only valid JSON arrays."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        content = response.choices[0].message.content.strip()
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
        return json.loads(content.strip())
    except Exception as e:
        return [{"error": str(e), "blind_spot": "Blind spot analysis failed"}]


def identify_ai_opportunities_from_tasks(role_details, confirmed_tools, parsed_resume, industry, aspiration):
    missed_use_cases = []
    high_freq_tasks = []

    task_clusters = role_details.get('task_clusters', {})
    if isinstance(task_clusters, str):
        task_clusters = json.loads(task_clusters)
        
    for cluster in task_clusters if isinstance(task_clusters, list) else []:
        task_name = cluster.get('name') if isinstance(cluster, dict) else str(cluster)
        task_frequency = cluster.get('frequency', 'unknown') if isinstance(cluster, dict) else 'unknown'
        task_effort = cluster.get('effort', 'medium') if isinstance(cluster, dict) else 'medium'

        ai_opportunities = determine_ai_opportunities(task_name, industry)
        ai_used = any(is_ai_enabled_tool(tool, task_name) for tool in confirmed_tools)

        if not ai_used:
            for opportunity in ai_opportunities:
                suggested_ai_use = opportunity.get('use_case', 'AI assistance')
                impact = estimate_impact(task_effort, task_frequency)
                ease_of_adoption = estimate_adoption_ease(parsed_resume.get('seniority', ''), aspiration)

                if is_high_frequency_task(task_frequency):
                    high_freq_tasks.append(task_name)

                missed_use_cases.append({
                    "task": task_name,
                    "suggested_ai_use": suggested_ai_use,
                    "impact": impact,
                    "ease_of_adoption": ease_of_adoption,
                    "reason": f"No AI tool detected for {task_name}"
                })

    summary_insight = summarize_insight(len(high_freq_tasks), len(role_details.get('task_clusters', [])))

    return {
        "missed_use_cases": missed_use_cases,
        "summary_insight": summary_insight
    }

def determine_ai_opportunities(task_name, industry):
    task_keywords = task_name.lower()
    suggestions = []

    if "plan" in task_keywords:
        suggestions.append({"use_case": "AI-powered scenario simulation"})
    if "report" in task_keywords or "status" in task_keywords:
        suggestions.append({"use_case": "Automated status report generator"})
    if "email" in task_keywords or "communication" in task_keywords:
        suggestions.append({"use_case": "AI draft assistant (e.g., Grammarly, Copilot)"})
    if not suggestions:
        suggestions.append({"use_case": "General task automation"})

    return suggestions

def is_ai_enabled_tool(tool, task_name):
    return tool.get("ai_related", False)

def estimate_impact(task_effort, task_frequency):
    if task_effort == "high" or task_frequency == "daily":
        return "high"
    elif task_effort == "medium" or task_frequency == "weekly":
        return "medium"
    else:
        return "low"

def estimate_adoption_ease(seniority, aspiration):
    if "lead" in seniority.lower() or "promote" in aspiration.lower():
        return "easy"
    elif "manager" in seniority.lower():
        return "moderate"
    else:
        return "low"

def is_high_frequency_task(task_frequency):
    return task_frequency.lower() in ["daily", "multiple times a day"]

def summarize_insight(high_freq_task_count, total_task_count):
    if total_task_count > 0:
        percentage = (high_freq_task_count / total_task_count) * 100
        return f"You are missing AI opportunities in {int(percentage)}% of your high-frequency tasks."
    else:
        return "Could not detect enough tasks to analyze."
