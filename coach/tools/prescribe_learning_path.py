"""
prescribe_learning_path tool — bridges the coordinator to the full PRESCRIBE pipeline.

Orchestrates two multi-agent sub-networks:
  1. Content recommendation: query_planner → retrieval_orchestrator (Perplexity + YouTube + GitHub)
                             → reflection_agent → content_scorer → content_explainer
  2. Learning path: intro_agent → path_summary_agent → gap_insight_agent
                    → learning_steps_agent → closing_cta_agent

The coordinator calls this once the user engages with a specific use case.
Returns a unified dict with a pre-assembled `formatted_output` string ready for direct
presentation to the user — the coordinator should paste it verbatim without paraphrasing.
"""
import asyncio
import json
import time

from agent_core.global_agent_memory import update_session_context
from agent_core.session_trace import record_event
from agents.recommendation_agent.content_recommendation.retrieval_orchestrator import run_retrieval_orchestrator
from agents.recommendation_agent.content_recommendation.content_scorer import score_content_item
from agents.recommendation_agent.content_recommendation.content_explainer import generate_explanation
from agents.recommendation_agent.learning_path.learning_steps_agent import generate_learning_steps


def _status(msg: str, expand: bool = False):
    """Write a step to the Streamlit st.status() widget, or print if not available."""
    print(msg)
    try:
        import streamlit as st
        if not st.runtime.exists():
            return
        status_ctx = st.session_state.get("_status_ctx")
        if status_ctx:
            status_ctx.write(msg)
            if expand:
                status_ctx.update(label=msg, state="running", expanded=True)
    except Exception:
        pass


def prescribe_learning_path(
    use_case: dict,
    user_id: str,
    session_id: str,
    profile: dict = None,
) -> dict:
    """
    Run the full PRESCRIBE pipeline for one use case.

    Input:
      use_case — one use case dict from generate_use_cases:
        {title, task, ai_opportunity, time_saved_pct, suggested_tool}
      user_id, session_id — for memory routing
      profile — user_model.profile dict (provides role context, aspiration, task clusters)

    Output:
      {formatted_output (str), intro_text, path_summary, gap_analysis, learning_steps,
       closing_cta, learning_modules (curated items), has_content (bool),
       error (if failed)}
    """
    profile = profile or {}

    # Build the subtask description from the use case
    use_case_title = use_case.get("title", "AI productivity workflow")
    subtask_description = (
        f"{use_case_title}: {use_case.get('task', '')}. "
        f"AI opportunity: {use_case.get('ai_opportunity', '')}. "
        f"Tool: {use_case.get('suggested_tool', '')}."
    )

    # Build the retrieval context dict the pipeline expects
    retrieval_context = _build_retrieval_context(use_case, profile)

    # Persona strings for coaching status messages
    _role = f"{profile.get('seniority', '')} {profile.get('title', '')}".strip()
    _company = profile.get("company", "")
    _role_label = f"{_role} at {_company}" if _company else (_role or "you")
    _seniority = profile.get("seniority", "").lower()
    _is_senior = any(s in _seniority for s in ["vp", "director", "chief", "head of", "principal", "senior"])

    print(f"\n{'='*60}")
    print(f"PRESCRIBE: Starting pipeline for use case: {use_case_title}")
    print(f"User: {user_id} | Session: {session_id}")
    print(f"Retrieval context keys: {list(retrieval_context.keys())}")
    print(f"{'='*60}")

    _status(
        f"Looking at what **{_role_label}** actually needs for **{use_case_title}** — "
        f"{'at your level, this isn\'t about basics. It\'s about using AI to move faster at scale.' if _is_senior else 'thinking about the real workflow, not just the tool.'}",
        expand=True,
    )

    t_retrieval = time.time()
    try:
        curated_items = _run_async(
            _run_content_pipeline(subtask_description, retrieval_context, user_id, session_id)
        )
    except Exception as e:
        print(f"PRESCRIBE ERROR: Content pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        record_event(session_id, phase="prescribe", agent="retrieval_pipeline",
                     inputs={"use_case": use_case_title},
                     outputs={},
                     duration_ms=int((time.time() - t_retrieval) * 1000),
                     status="error", error=str(e))
        return {"error": f"Content retrieval failed: {e}", "has_content": False}

    print(f"PRESCRIBE: Content pipeline complete. curated_items count: {len(curated_items)}")
    source_counts = {}
    for item in curated_items:
        src = item.get("source", "unknown")
        source_counts[src] = source_counts.get(src, 0) + 1
        print(f"  - [{src}] {item.get('title','?')} (score={item.get('score',0):.2f})")

    record_event(session_id, phase="prescribe", agent="retrieval_pipeline",
                 inputs={"use_case": use_case_title, "subtask": subtask_description[:80]},
                 outputs={"total_items": len(curated_items), "sources": source_counts,
                          "top_score": round(max((i.get("score", 0) for i in curated_items), default=0), 2)},
                 duration_ms=int((time.time() - t_retrieval) * 1000),
                 status="ok" if curated_items else "error",
                 error=None if curated_items else "No content retrieved from any source")

    _status(
        f"Found {len(curated_items)} results — "
        f"{'filtering out anything too introductory for your level...' if _is_senior else 'filtering for what actually moves you forward...'}"
    )

    # Step 2: Write the full context structure learning_path_agent expects to memory
    structured_aspiration = profile.get("aspiration_structured", {})
    session_context = {
        "subtask": {
            "id": _make_subtask_id(use_case_title),
            "title": use_case_title,
            "description": subtask_description,
        },
        "use_case": use_case,
        "content": {
            "curated_training": curated_items,
            "reflection_summary": f"Content curated for: {use_case_title}",
        },
        "aspiration": {
            "aspiration_category": structured_aspiration.get("aspiration_category", "AI Fluency"),
            "target_role_archetype": structured_aspiration.get("target_role_archetype", ""),
            "target_company_type": structured_aspiration.get("target_company_type", ""),
            "target_org_context": structured_aspiration.get("target_org_context", ""),
            "role_delta_summary": structured_aspiration.get("role_delta_summary", ""),
            "domain_shift_signal": structured_aspiration.get("domain_shift_signal", False),
            "target_company": profile.get("company", ""),
        },
        "persona": {
            "role": f"{profile.get('seniority', '')} {profile.get('title', '')}".strip(),
            "domain": profile.get("domain", ""),
            "company": profile.get("company", ""),
            "impact_scale": profile.get("org_shape", "enterprise"),
        },
        "skill_delta": {
            "missing_skills": _infer_skill_gaps(use_case, profile),
            "ai_enabler_gaps": [],
        },
        # Enriched context so sub-agents (learning_steps, intro, gap) have full picture
        "org_constraints": profile.get("org_constraints", ""),
        "task_clusters": profile.get("task_clusters", []),
        "tools_known": profile.get("tools_known", []),
        "user_id": user_id,
        "session_id": session_id,
        "subtask_id": _make_subtask_id(use_case_title),
    }
    update_session_context(user_id, session_id, session_context)

    print(f"PRESCRIBE: Session context written to memory. Running learning path agents...")
    _status(
        f"Sequencing the best resources into a step-by-step path — "
        f"{'ordering it around the decisions a {_role} actually has to make.' if _is_senior else 'writing why each step matters for your specific goal.'}"
        .replace("{_role}", _role or "leader")
    )

    # Step 3: Run learning_steps_agent only.
    # intro / path_summary / gap_insight / closing_cta produce text GPT-4o synthesis rewrites
    # anyway — skip them. learning_steps_agent earns its keep: it does explicit dependency-aware
    # sequencing + per-resource narration that gives synthesis richer raw material.
    # Optimized: sequencing uses gpt-4o-mini; narration is one batched gpt-4o call (not N calls).
    t_lp = time.time()
    print("PRESCRIBE: Running learning_steps_agent for sequencing + narration (skipping 4 other sub-agents)...")
    _status("Writing your personalized path...")

    lp_context = {
        **session_context,
        "content": {"curated_training": curated_items},
    }
    try:
        learning_steps_data = _run_async(generate_learning_steps(lp_context, return_structured_output=True))
        steps_narrative = (
            learning_steps_data.get("narrative", "")
            if isinstance(learning_steps_data, dict)
            else str(learning_steps_data)
        )
    except Exception as e:
        print(f"PRESCRIBE: learning_steps_agent failed: {e} — synthesis will write steps from scratch")
        steps_narrative = ""

    learning_path = {
        "intro_text": "",
        "path_summary": "",
        "gap_analysis": "",
        "learning_steps": steps_narrative,
        "closing_cta": "",
        "pacing_guidance": "1 module every 2-3 days",
    }
    record_event(session_id, phase="prescribe", agent="learning_path_agent",
                 inputs={"use_case": use_case_title, "module_count": len(curated_items)},
                 outputs={"has_steps": bool(steps_narrative), "steps_len": len(steps_narrative),
                          "skipped_agents": ["intro", "path_summary", "gap_insight", "closing_cta"]},
                 duration_ms=int((time.time() - t_lp) * 1000),
                 status="ok")

    # Step 4: Assemble formatted_output — a single string the coordinator pastes verbatim
    formatted_output = _assemble_formatted_output(learning_path, curated_items, use_case, profile)

    print(f"PRESCRIBE: formatted_output length: {len(formatted_output)} chars")
    print(f"PRESCRIBE: Pipeline complete successfully.")

    # Phase C: Flywheel write — record session outcome back to archetype store
    archetype_id = profile.get("archetype_id")
    if archetype_id:
        try:
            from coach.intelligence.flywheel_writer import update_archetype
            update_archetype(
                archetype_id=archetype_id,
                use_case_title=use_case_title,
                has_content=bool(curated_items),
            )
            print(f"PRESCRIBE: Flywheel updated for archetype {archetype_id}")
        except Exception as e:
            print(f"PRESCRIBE: Flywheel write failed (non-fatal): {e}")

    # Phase C+: Content Intelligence write — record served content items to content store
    if curated_items:
        try:
            from coach.intelligence.content_store import ContentStore
            _content_store = ContentStore()
            _content_store.record_session(
                use_case_category=_derive_content_category(use_case),
                seniority_tier=_normalize_seniority_tier(profile.get("seniority", "")),
                archetype_id=archetype_id,
                curated_items=curated_items,
            )
            print(f"PRESCRIBE: Content store updated ({len(curated_items)} items recorded)")
        except Exception as e:
            print(f"PRESCRIBE: Content store write failed (non-fatal): {e}")

    return {
        "formatted_output": formatted_output,
        "has_content": bool(formatted_output.strip()),
        "intro_text": learning_path.get("intro_text", ""),
        "path_summary": learning_path.get("path_summary", ""),
        "gap_analysis": learning_path.get("gap_analysis", ""),
        "learning_steps": learning_path.get("learning_steps", ""),
        "closing_cta": learning_path.get("closing_cta", ""),
        "learning_modules": curated_items,
        "pacing_guidance": learning_path.get("pacing_guidance", "1 module every 2-3 days"),
        "use_case_title": use_case_title,
    }


def _run_async(coro):
    """Run a coroutine, handling the case where an event loop is already running."""
    try:
        return asyncio.run(coro)
    except RuntimeError:
        # Streamlit or another framework already has a running event loop in this thread
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


def _assemble_formatted_output(
    learning_path: dict,
    curated_items: list,
    use_case: dict,
    profile: dict,
) -> str:
    """
    Synthesize a coaching narrative from sub-agent outputs + all available context.
    Uses GPT-4o to produce a single cohesive, personalized response.
    Falls back to the old concatenation approach if synthesis fails or no items.
    """
    if curated_items:
        try:
            return _synthesize_coaching_narrative(learning_path, curated_items, use_case, profile)
        except Exception as e:
            print(f"[_assemble_formatted_output] GPT-4o synthesis failed: {e} — falling back")

    return _assemble_fallback(learning_path, curated_items, use_case, profile)


def _synthesize_coaching_narrative(
    learning_path: dict,
    curated_items: list,
    use_case: dict,
    profile: dict,
) -> str:
    """
    Generate one cohesive coaching narrative using GPT-4o.
    Incorporates role/aspiration/org context, the curated resources,
    and the sub-agent outputs as raw material.
    """
    import os
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Build profile context
    persona_role = f"{profile.get('seniority', '')} {profile.get('title', '')}".strip()
    persona_company = profile.get("company", "")
    persona_domain = profile.get("domain", "")
    org_constraints = profile.get("org_constraints", "None stated")
    task_clusters = profile.get("task_clusters", [])
    structured_asp = profile.get("aspiration_structured", {})
    target_role = structured_asp.get("target_role_archetype", "")
    target_company_type = structured_asp.get("target_company_type", "")
    target_org_context = structured_asp.get("target_org_context", "")
    role_delta = structured_asp.get("role_delta_summary", "")
    target_role_label = f"{target_role} at {target_company_type}".strip(" at") if target_company_type else target_role
    aspiration_category = structured_asp.get("aspiration_category", "")
    seniority = profile.get("seniority", "").lower()
    is_senior = any(s in seniority for s in ["vp", "director", "chief", "head of", "principal", "senior"])

    # Task cluster summary
    task_cluster_lines = "\n".join([
        f"  • {c.get('name','?')} ({c.get('effort_pct','?')}% of time): {c.get('ai_opportunity','')}"
        for c in task_clusters[:4]
    ]) if task_clusters else "  (Not available)"

    # Resource list with full context
    resource_lines = []
    for i, item in enumerate(curated_items[:6], 1):
        link = item.get("link", "")
        title = item.get("title", "Resource")
        source = item.get("source", "")
        fmt = item.get("format", "")
        score = item.get("score", 0)
        why = item.get("why", "")
        snippet = (item.get("snippet") or item.get("description", ""))[:200]
        resource_lines.append(
            f"[{i}] {title}\n"
            f"    URL: {link}\n"
            f"    Type: {source} / {fmt}  Score: {score:.1f}\n"
            f"    Why relevant: {why or snippet}"
        )
    resources_text = "\n\n".join(resource_lines)

    # Sub-agent outputs as raw material
    intro_draft = learning_path.get("intro_text", "").strip()
    gap_draft = learning_path.get("gap_analysis", "").strip()
    steps_draft = learning_path.get("learning_steps", "").strip()
    cta_draft = learning_path.get("closing_cta", "").strip()

    # Seniority-aware framing instructions
    if is_senior:
        seniority_framing = f"""
SENIORITY CONTEXT: This person is a {persona_role}. They are NOT learning to use AI from scratch.
At their level, "{use_case.get('title', '')}" means something very different than it does for a junior PM.
- Frame each step around DECISIONS and LEVERAGE, not tool mechanics
- Each step should enable them to move faster, with more confidence, at greater org scale
- Avoid any framing that sounds like "here's how to use [tool]" — reframe as "here's how to use AI to make better [X] decisions"
- The output of each step should be a capability that changes how they lead or decide, not just how they type"""
    else:
        seniority_framing = f"""
SENIORITY CONTEXT: This person is building practical AI skills. Make each step feel immediately usable —
they should be able to apply it to real work within a day of completing it."""

    # Target role framing — makes "After this, you'll be able to:" lines specific to target role
    if target_role_label:
        target_role_narrative = f"""
TARGET ROLE FRAMING (critical for "After this, you'll be able to:" lines):
This person is building toward: {target_role_label}
What that role actually looks like: {target_org_context or 'not specified'}
Gap to close: {role_delta or 'not specified'}

They are practicing {target_role_label} capabilities within their CURRENT scope — not simulating
the target role, not just optimizing current work. The bridge: practice target skill at current scale.

Each "After this, you'll be able to:" line MUST name a capability they can practice NOW that
directly maps to what {target_role_label} runs on:
  GOOD: "run a portfolio-level synthesis of competing priorities — the same move a {target_role} makes,
        practiced here within your current product scope at {persona_company or 'your company'}"
  GOOD: "frame a stakeholder recommendation with the rigor a {target_role_label} would need —
        defensible structure, tradeoff analysis, clear ask"
  NOT: "be ready to work as a {target_role}" (aspirational, not actionable today)
  NOT: "help you get promoted" (too generic — name the SPECIFIC muscle)"""
    else:
        target_role_narrative = ""

    prompt = f"""You are an expert AI career coach writing a personalized learning path for a professional.

ABOUT THIS PERSON:
Role: {persona_role}{f' at {persona_company}' if persona_company else ''}
Domain: {persona_domain or 'not specified'}
Aspiration: {aspiration_category or 'career advancement'}{f' → {target_role_label}' if target_role_label else ''}
Org constraints: {org_constraints}

What they actually do (task clusters):
{task_cluster_lines}

THE USE CASE THEY CHOSE:
Title: {use_case.get('title', '')}
What AI does here: {use_case.get('ai_opportunity', '')}
Why this matters for their goal: {use_case.get('aspiration_connection', '')}
Tool to use: {use_case.get('suggested_tool', '')}
{seniority_framing}
{target_role_narrative}

RESOURCES FOUND ({len(curated_items)} total, ranked by relevance):
{resources_text}

RAW CONTENT FROM SUB-AGENTS (use as source material — rewrite into a cohesive narrative):
Intro draft: {intro_draft or '(none)'}
Gap analysis draft: {gap_draft or '(none)'}
Step-by-step drafts: {steps_draft or '(none)'}
Closing draft: {cta_draft or '(none)'}

YOUR TASK:
Write a single cohesive coaching response with this exact structure — NO section numbers:

**Opening** (2-3 sentences, NO label)
- Name their specific use case and the concrete AI action it enables
- Connect to their actual work friction at {persona_company or 'their company'} — make it feel specific, not generic

**What you'll develop** (bold heading, 2-3 sentences)
- The specific capabilities this path builds — use their org constraints (e.g., if Copilot is approved, say so)
- Connect to their aspiration toward {target_role or 'their goal'}

**Your learning path** (bold heading)
CRITICAL — structure each step TASK-FIRST, then the training:

**Step [N] — [Name the specific skill, decision, or action to master]**
[1 sentence: why this specific capability matters for a {persona_role} doing "{use_case.get('title', '')}" — be concrete, reference their domain/company if relevant]
📚 [Exact resource title](URL) · [source_type] · [duration if available, otherwise omit]
After this, you'll be able to: [specific action verb + what changes in how they work]

Repeat for each resource. The heading of each step is a TASK or SKILL — not the training title.

**To wrap up** (bold heading, 1-2 sentences)
- Connect completing this to their specific aspiration — feel like a milestone, not a cheerleader

CRITICAL RULES:
- Use ONLY the real URLs from the resources list — never invent URLs
- Step headings name a TASK or SKILL, never a resource title
- Every observation references their role, company, domain, or aspiration — NO generic statements
- Second person throughout ("you/your")
- Mentor tone — direct and confident, not fluffy
- Total response under 700 words
- No numbered section labels (not "1. OPENING" etc) — just bold headings
- If a resource has no URL, write the title without a link"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You write personalized AI coaching narratives. "
                    "Every sentence must reference the user's specific role, company, or aspiration. "
                    "Never use generic coaching language. Always include real URLs from the resource list."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content.strip()


def _assemble_fallback(
    learning_path: dict,
    curated_items: list,
    use_case: dict,
    profile: dict,
) -> str:
    """
    Fallback: concatenate sub-agent outputs (used if synthesis fails or no items).
    """
    sections = []

    intro = learning_path.get("intro_text", "").strip()
    if intro:
        sections.append(intro)

    gap = learning_path.get("gap_analysis", "").strip()
    if gap and gap not in ("", "N/A"):
        sections.append(gap)

    steps = learning_path.get("learning_steps", "").strip()
    if steps and steps != "No learning steps available." and len(steps) > 30:
        sections.append(steps)
    elif curated_items:
        fallback_steps = ["🛠️ **Your Learning Path**\n"]
        for i, item in enumerate(curated_items[:5], 1):
            title = item.get("title", "Resource")
            link = item.get("link", "")
            duration = item.get("duration", "")
            why = item.get("why", "")
            duration_display = f" — {duration}" if duration else ""
            link_display = f"\n🔗 [{link}]({link})" if link else ""
            why_display = f"\n🧠 {why}" if why else ""
            fallback_steps.append(
                f"▶️ **Step {i}: {title}**{duration_display}"
                f"{link_display}"
                f"{why_display}"
            )
        sections.append("\n\n".join(fallback_steps))

    cta = learning_path.get("closing_cta", "").strip()
    if cta:
        sections.append(f"---\n{cta}")

    return "\n\n".join(sections) if sections else ""


async def _run_content_pipeline(
    subtask: str,
    context: dict,
    user_id: str,
    session_id: str,
) -> list:
    """
    Run retrieval → score → explain pipeline without streamlit dependencies.
    Returns top scored + explained content items.

    Warm-start: fetches proven content from ContentStore for this use_case_category ×
    seniority_tier, then runs those candidates through the SAME reflection agent as
    fresh items — so seniority/tool/skill filtering applies equally to both pools.
    """
    curated_items, _reflection_log, _queries = await run_retrieval_orchestrator(
        subtask,
        context,
        user_id=user_id,
        session_id=session_id,
        print_debug=False,
        return_queries=True,
    )

    print(f"  _run_content_pipeline: retrieval returned {len(curated_items)} items after reflection")

    # Phase C+: Warm-start from content store — reflect on candidates before merging
    warm_accepted = []
    try:
        from coach.intelligence.content_store import ContentStore
        from agents.recommendation_agent.content_recommendation.reflection_agent import reflect_on_relevance
        use_case_category = _derive_content_category(context.get("use_case", {}))
        seniority_tier = _normalize_seniority_tier(context.get("seniority", ""))
        warm_candidates = ContentStore().get_warm_start(use_case_category, seniority_tier, top_n=5)
        if warm_candidates:
            print(f"  Content store: {len(warm_candidates)} warm candidates for {use_case_category}/{seniority_tier} → reflecting")
            warm_reflected, _ = await reflect_on_relevance(warm_candidates, subtask, context)
            fresh_links = {i.get("link") for i in curated_items}
            warm_accepted = [i for i in warm_reflected if i.get("link") not in fresh_links]
            print(f"  Content store: {len(warm_accepted)} warm items passed reflection, {len(warm_candidates) - len(warm_accepted)} rejected")
    except Exception as e:
        print(f"  Content store warm start skipped (non-fatal): {e}")

    all_items = curated_items + warm_accepted

    role = context.get("role", "your role")
    _status(f"Kept {len(all_items)} relevant results — ranking them by relevance to {role}...")

    scored = []
    for item in all_items:
        try:
            item["description"] = item.get("description") or item.get("snippet", "")
            item["format"] = item.get("format", "Article")
            item["score"] = score_content_item(
                item,
                context.get("use_case", {}).get("title", subtask),
                context.get("tool_familiarity", []),
                context.get("missing_skills", []),
                context.get("modality_preference", []),
            )
            item["why"] = generate_explanation(
                item,
                context.get("use_case", {}).get("title", subtask),
                context.get("missing_skills", []),
            )
            scored.append(item)
        except Exception as e:
            print(f"  Score/explain failed for '{item.get('title', '?')}': {e}")
            item.setdefault("score", 0)
            item.setdefault("why", "")
            scored.append(item)

    # Sort by score descending, return top 6
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored[:6]


def _build_retrieval_context(use_case: dict, profile: dict) -> dict:
    """Build the context dict the retrieval pipeline needs."""
    structured_aspiration = profile.get("aspiration_structured", {})
    role_str = f"{profile.get('seniority', '')} {profile.get('title', '')}".strip()
    aspiration_category = structured_aspiration.get("aspiration_category", profile.get("aspiration", ""))
    target_role = structured_aspiration.get("target_role_archetype", "")
    target_company_type = structured_aspiration.get("target_company_type", "")
    target_role_label = f"{target_role} at {target_company_type}".strip(" at") if target_company_type else target_role
    role_delta = structured_aspiration.get("role_delta_summary", "")
    domain_shift = structured_aspiration.get("domain_shift_signal", False)
    return {
        "use_case": use_case,
        "focused_subtask": use_case.get("title", ""),
        "tool_familiarity": profile.get("tools_known", []),
        "missing_skills": _infer_skill_gaps(use_case, profile),
        "modality_preference": _infer_modality(profile),
        "role": role_str,
        "seniority": profile.get("seniority", ""),
        "domain": profile.get("domain", ""),
        "org_constraints": profile.get("org_constraints", ""),
        "aspiration": aspiration_category,
        "learning_objectives": (
            f"Practice the AI skills a {target_role_label or role_str} needs for "
            f"{use_case.get('title', 'this use case')} — building toward that level from current scope"
            if target_role else
            f"Learn to use AI for {use_case.get('title', 'this use case')} "
            f"to {aspiration_category or 'advance career'}"
        ),
        "ai_literacy_signals": "intermediate professional",
        "target_role_archetype": target_role_label or role_str,
        "target_role_delta": role_delta,
        "domain_shift": domain_shift,
        "suggested_tool": use_case.get("suggested_tool", ""),
    }


def _infer_skill_gaps(use_case: dict, profile: dict) -> list:
    """Derive likely skill gaps from the use case and profile."""
    gaps = []
    ai_opp = use_case.get("ai_opportunity", "").lower()
    tool = use_case.get("suggested_tool", "").lower()

    if "prompt" in ai_opp or "gpt" in ai_opp:
        gaps.append("prompt engineering")
    if "azure" in tool or "studio" in ai_opp:
        gaps.append("Azure AI Studio basics")
    if "copilot" in tool:
        gaps.append("Microsoft Copilot workflows")
    if "automation" in ai_opp or "pipeline" in ai_opp:
        gaps.append("AI workflow automation")
    if "data" in ai_opp or "analysis" in ai_opp:
        gaps.append("data analysis with AI")

    return gaps[:3] if gaps else ["AI tool basics"]


def _infer_modality(profile: dict) -> list:
    """Infer preferred learning modalities from profile."""
    learning_style = profile.get("learning_style", "")
    if "video" in learning_style.lower():
        return ["video"]
    if "read" in learning_style.lower():
        return ["article", "docs"]
    return ["video", "article"]


def _make_subtask_id(title: str) -> str:
    """Turn a use case title into a stable subtask ID."""
    return title.lower().replace(" ", "_")[:40]


def _derive_content_category(use_case: dict) -> str:
    """
    Derive a category slug from a use case dict.
    Uses the task cluster name (use_case["task"]) as the primary signal —
    it's already clean and normalized by generate_use_cases.
    Falls back to the use case title if task is missing.
    """
    raw = use_case.get("task", "") or use_case.get("title", "")
    if not raw:
        return ""
    import re
    slug = raw.lower()
    slug = re.sub(r"[^a-z0-9\s]", "", slug)
    slug = re.sub(r"\s+", "_", slug.strip())
    return slug[:60]


def _normalize_seniority_tier(seniority: str) -> str:
    """Map free-form seniority string to a standard tier bucket."""
    if not seniority:
        return "manager"
    s = seniority.lower().strip()
    if any(x in s for x in ["vp", "vice president", "svp", "evp"]):
        return "vp"
    if any(x in s for x in ["director", "head of"]):
        return "director"
    if any(x in s for x in ["principal", "staff", "senior"]):
        return "senior"
    if any(x in s for x in ["manager", "lead"]):
        return "manager"
    return "manager"
