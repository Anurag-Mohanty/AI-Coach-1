"""
infer_role_detail tool — direct GPT-4 call to break a role into task clusters.

Returns task clusters with effort percentages and AI opportunity ratings.
This feeds generate_use_cases — no task clusters = generic use cases.

Why a direct GPT-4 call (not the underlying role_detail_agent):
- role_detail_agent uses call_llm_model() which returns raw text; json.loads() fails silently
  on markdown code fences, leaving task_clusters empty
- The agent's output format ({effort_distribution: {name: "35"}} as a separate dict) does not
  match the {name, effort_pct (int), ai_opportunity} per-cluster format the coordinator expects
- Direct call gives us full control over the prompt, JSON enforcement, and output shape
"""
import json
import os
import re

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Phase C — role archetype store (load once at module level)
try:
    from coach.intelligence.archetype_store import RoleArchetypeStore
    _archetype_store = RoleArchetypeStore()
except Exception:
    _archetype_store = None  # Graceful fallback if store not available

_SYSTEM = (
    "You are an expert in workplace productivity and role analysis. "
    "Return ONLY valid JSON. No markdown, no prose, no code fences."
)

_PROMPT = """Analyze the DAILY WORK STRUCTURE of the following role and break it into 4-5 task clusters.

Role title: {role}
Company: {company}
Industry: {domain}
Seniority: {seniority}
{role_context_section}

Your job is to describe what this person ACTUALLY DOES every week — not their skills, not their resume, not aspirations.
Ground this in what this SPECIFIC role at this SPECIFIC company typically involves day-to-day.

PRODUCT MANAGER DISAMBIGUATION (critical):
- "PM" = Product Manager. NOT Project Manager, NOT Program Manager.
- Product Managers own: roadmap prioritization, requirements/discovery, stakeholder alignment, market/competitive research, go-to-market planning, product strategy
- Product Managers do NOT own: software testing, code deployment, IT infrastructure, change request tracking, system maintenance, QA
- At an enterprise healthcare company like Cigna, a PM's clusters will include things like: navigating clinical/actuarial/compliance stakeholders, backlog management under regulatory constraints, cross-functional coordination across IT/clinical/operations

SENIORITY CALIBRATION (critical):
- VP / Director / Head of / Principal: Task clusters involve portfolio-level decisions, executive alignment, org-wide strategy, and coordinating across multiple teams or product lines. They DO NOT spend time on individual task execution. Their clusters are: portfolio/roadmap strategy, executive stakeholder management, org leadership, cross-functional program coordination, and strategic market positioning.
- Senior Manager / Manager: Mix of individual execution AND team oversight. Some strategy, mostly driving delivery and team capability.
- Senior IC / Mid-level: Primarily individual execution. Clusters are specific tasks they personally complete every week.
Apply this calibration to "{seniority}" when generating clusters.

IMPORTANT: Do NOT infer task clusters from skills listed on a resume. A PM who lists "AI strategy" as a skill does not spend 25% of their time on "AI-First Product Strategy" — they spend time on roadmap prioritization, stakeholder alignment, market research, and product discovery. Clusters reflect the ROLE, not the resume.

For each cluster, assess the real AI opportunity — where AI can genuinely reduce time or improve quality for this specific role/domain combination at this seniority level.

Return a JSON object with exactly these fields:
{{
  "task_clusters": [
    {{
      "name": "Short descriptive name (3-5 words)",
      "effort_pct": <integer 1-100, all clusters must sum to ~100>,
      "ai_opportunity": "<high|medium|low>",
      "description": "One sentence describing what this cluster involves day-to-day at this company"
    }}
  ],
  "ai_opportunity_density": <float 0.0-1.0, weighted average of AI opportunity across clusters>
}}

Rules:
- 4-5 clusters only
- effort_pct values must sum to approximately 100
- ai_opportunity must be exactly "high", "medium", or "low"
- Clusters must describe the ACTUAL DAILY WORK of this role — not the person's skills or interests"""


def infer_role_detail(
    role: str,
    company: str = "",
    domain: str = "",
    seniority: str = "",
    resume: str = None,
    role_context: dict = None,
    user_id: str = "default_user",
) -> dict:
    """
    Break a role into task clusters with effort percentages and AI opportunity ratings.

    Input:  role title, optional company/domain/seniority, optional resume text,
            optional role_context dict from analyze_role
    Output: {task_clusters: [{name, effort_pct, ai_opportunity, description}],
             ai_opportunity_density} or {error}
    """
    # Phase C: Check archetype store before making a GPT-4o call.
    # For known archetypes (score >= 0.6), return pre-computed task_clusters instantly.
    org_shape = (role_context or {}).get("org_shape", "")
    if _archetype_store and seniority and domain:
        archetype, score = _archetype_store.find_closest(seniority, domain, org_shape)
        if archetype and score >= 0.6:
            print(f"[infer_role_detail] Archetype hit: {archetype['archetype_id']} (score={score:.2f}) — skipping LLM")
            return {
                "task_clusters": archetype["task_clusters"],
                "ai_opportunity_density": archetype.get("ai_opportunity_density", 0.7),
                "archetype_id": archetype["archetype_id"],
                "archetype_score": score,
                "source": "archetype_store",
            }

    # Build role context section
    # NOTE: We deliberately do NOT pass the resume text here.
    # Resume skills sections contaminate cluster generation — a PM who lists "AI strategy"
    # as a skill should not get "AI-First Product Strategy" as a daily task cluster.
    # Task clusters must come from role+company+domain knowledge, not resume content.
    if role_context:
        constraints = role_context.get("ai_applicability_constraints", "")
        org_shape = role_context.get("org_shape", "")
        role_context_section = ""
        if org_shape:
            role_context_section += f"Org shape: {org_shape}\n"
        if constraints:
            role_context_section += f"AI tool constraints: {constraints}"
        role_context_section = role_context_section.strip()
    else:
        role_context_section = ""

    prompt = _PROMPT.format(
        role=role or "professional",
        company=company or "not specified",
        domain=domain or "not specified",
        seniority=seniority or "mid-level",
        role_context_section=role_context_section,
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content.strip()
        # Strip markdown fences if present (belt-and-suspenders)
        content = re.sub(r"^```(?:json)?\n?", "", content)
        content = re.sub(r"\n?```$", "", content)
        data = json.loads(content)
    except Exception as e:
        return {"error": f"infer_role_detail failed: {e}"}

    task_clusters = data.get("task_clusters", [])
    if not task_clusters:
        return {"error": "No task clusters returned"}

    # Normalise: ensure effort_pct is int, ai_opportunity is lowercase
    for cluster in task_clusters:
        cluster["effort_pct"] = int(cluster.get("effort_pct", 20))
        cluster["ai_opportunity"] = str(cluster.get("ai_opportunity", "medium")).lower()

    return {
        "task_clusters": task_clusters,
        "ai_opportunity_density": float(data.get("ai_opportunity_density", 0.5)),
        "archetype_id": None,
        "source": "llm",
    }
