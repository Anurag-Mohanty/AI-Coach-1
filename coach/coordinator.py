"""
CoachCoordinator — the brain of the v3 coaching experience.

Uses OpenAI tool calling to decide when to invoke specialist tools.
Maintains conversation history within a session.
Persists nothing itself — caller is responsible for saving the user model.
"""
import json
import os
import time
from datetime import datetime

from openai import OpenAI

from coach.tools.parse_resume import parse_resume_from_text
from coach.tools.analyze_role import analyze_role
from coach.tools.infer_role_detail import infer_role_detail
from coach.tools.infer_cultural_tone import infer_cultural_tone
from coach.tools.interpret_aspiration import interpret_aspiration
from coach.tools.generate_use_cases import generate_use_cases
from coach.tools.prescribe_learning_path import prescribe_learning_path
from agent_core.persona_context import get_user_context, update_shared_context
from agent_core.session_trace import (
    clear_trace, record_event,
    set_active_session, set_active_phase,
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── Tool definitions for OpenAI function calling ──────────────────────────────

_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "parse_resume",
            "description": (
                "Extract a structured professional profile from raw resume text "
                "that the user has pasted into the conversation. "
                "Call this when the user provides their resume as text."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "resume_text": {
                        "type": "string",
                        "description": "The raw resume text provided by the user.",
                    }
                },
                "required": ["resume_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_role",
            "description": (
                "Analyze a professional role to determine its archetype, "
                "organizational context, and AI applicability constraints. "
                "Call this once you know the user's title and at least one of "
                "company or domain. Always call this before infer_role_detail."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Job title"},
                    "company": {"type": "string", "description": "Company name (use empty string if unknown)"},
                    "domain": {"type": "string", "description": "Industry or domain (e.g. fintech, B2B SaaS, healthcare)"},
                    "seniority": {"type": "string", "description": "Seniority level (e.g. senior, lead, director)"},
                    "company_size": {"type": "string", "description": "Company size or stage (e.g. Series C, enterprise, startup)"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "infer_role_detail",
            "description": (
                "Break the user's role into specific task clusters with effort percentages "
                "and AI opportunity ratings. Call this immediately after analyze_role — "
                "it reveals what they actually spend their time on, which drives use case quality. "
                "Without task clusters, use cases will be generic."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "description": "Full role description — title + seniority + company context",
                    },
                },
                "required": ["role"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "infer_cultural_tone",
            "description": (
                "Infer how this person prefers to communicate and receive information, "
                "based on their org context. Call this silently after analyze_role — "
                "never announce it to the user. Use the result to calibrate your own voice "
                "for the rest of the session."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "company": {"type": "string", "description": "Company name"},
                    "domain": {"type": "string", "description": "Industry or domain"},
                    "seniority": {"type": "string", "description": "Seniority level"},
                    "org_shape": {"type": "string", "description": "Org structure inferred from analyze_role (flat/hierarchical/matrix)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "interpret_aspiration",
            "description": (
                "Interpret what the user said they want to accomplish into structured "
                "career goal intelligence: realistic trajectory options, aspiration category, "
                "realism score. Call this once the user answers the aspiration question. "
                "Do NOT call this until the user has explicitly stated what they're hoping for."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "aspiration_statement": {
                        "type": "string",
                        "description": "Exactly what the user said they want to accomplish — verbatim or close paraphrase.",
                    },
                },
                "required": ["aspiration_statement"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_use_cases",
            "description": (
                "Generate 3 specific AI use cases for the user's role. "
                "Call this at the start of the REVEAL phase, after you have the user's "
                "aspiration and org constraints. The more context you pass, the better. "
                "Uses task clusters from infer_role_detail if available."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Job title"},
                    "seniority": {"type": "string", "description": "Seniority level"},
                    "domain": {"type": "string", "description": "Industry or domain"},
                    "tools_known": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tools the user currently uses",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "prescribe_learning_path",
            "description": (
                "Build a personalized learning path for one specific AI use case. "
                "Call this when the user engages with a specific use case from generate_use_cases — "
                "either by asking how to do it, asking for resources, or asking to go deeper. "
                "Runs a full content recommendation pipeline (YouTube, GitHub, Perplexity) "
                "and returns a sequenced learning path with narrated steps."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "use_case_index": {
                        "type": "integer",
                        "description": "Which use case the user is asking about (0-indexed: 0, 1, or 2). Default 0 if unclear.",
                    },
                    "use_case_title": {
                        "type": "string",
                        "description": "Title of the use case the user wants to explore (for logging/display).",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_profile",
            "description": (
                "Store information the user has revealed in conversation — aspiration, "
                "org constraints, or corrections to their profile. "
                "Call this whenever the user tells you something important about their goals, "
                "what they're trying to accomplish, or what tools/policies their company has."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "aspiration": {
                        "type": "string",
                        "description": (
                            "What the user is actually trying to accomplish with AI. "
                            "e.g. 'Reduce time spent writing stakeholder updates', "
                            "'Appear credible in exec conversations about AI', "
                            "'Quietly upskilling for a job search'"
                        ),
                    },
                    "org_constraints": {
                        "type": "string",
                        "description": (
                            "What AI tools the user can realistically use given their company. "
                            "e.g. 'Company has approved Microsoft Copilot only', "
                            "'No restrictions but HIPAA means no patient data in external tools', "
                            "'IT approval required for any new software'"
                        ),
                    },
                    "title": {"type": "string", "description": "Corrected job title if user clarified it"},
                    "company": {"type": "string", "description": "Corrected company name if user clarified it"},
                    "domain": {"type": "string", "description": "Corrected domain/industry if user clarified it"},
                },
                "required": [],
            },
        },
    },
]


# ── System prompt builder ──────────────────────────────────────────────────────

def _build_system_prompt(user_model: dict) -> str:
    name = user_model.get("name", "the user")
    phase = user_model.get("coaching_state", {}).get("current_phase", "hook")
    profile = user_model.get("profile", {})
    last_summary = user_model.get("coaching_state", {}).get("last_conversation_summary")
    is_returning = bool(user_model.get("interaction_history"))

    # Build profile summary
    parts = []
    if profile.get("title"):
        parts.append(f"Title: {profile['title']}")
    if profile.get("seniority"):
        parts.append(f"Seniority: {profile['seniority']}")
    if profile.get("company"):
        parts.append(f"Company: {profile['company']}")
    if profile.get("domain"):
        parts.append(f"Domain: {profile['domain']}")
    if profile.get("tools_known"):
        parts.append(f"Tools: {', '.join(profile['tools_known'][:6])}")
    profile_str = " | ".join(parts) if parts else "None yet"

    # Role intelligence
    role_archetype_str = ""
    if profile.get("role_archetype"):
        role_archetype_str = f"\nRole archetype: {profile['role_archetype']}"
    if profile.get("ai_applicability_constraints"):
        role_archetype_str += f"\nAI constraints: {profile['ai_applicability_constraints']}"
    if profile.get("org_shape"):
        role_archetype_str += f"\nOrg shape: {profile['org_shape']}"

    # Task clusters
    task_cluster_str = ""
    task_clusters = profile.get("task_clusters", [])
    if task_clusters:
        cluster_lines = []
        for c in task_clusters[:5]:
            name_c = c.get("name", "Task")
            effort = c.get("effort_pct", "?")
            opp = c.get("ai_opportunity", "")
            cluster_lines.append(f"  • {name_c} ({effort}% of time) — AI opportunity: {opp}")
        task_cluster_str = "\nTask clusters:\n" + "\n".join(cluster_lines)

    # Cultural tone
    tone_str = ""
    if profile.get("tone_style"):
        tone_str = (
            f"\nCommunication tone: {profile['tone_style']} — "
            f"match your language and framing to this style throughout the session."
        )

    # Aspiration
    aspiration = profile.get("aspiration", "")
    org_constraints = profile.get("org_constraints", "")
    aspiration_str = f"\nAspiration: {aspiration}" if aspiration else ""
    org_str = f"\nOrg constraints: {org_constraints}" if org_constraints else ""

    # Structured aspiration
    structured_asp = profile.get("aspiration_structured", {})
    structured_asp_str = ""
    if structured_asp:
        category = structured_asp.get("aspiration_category", "")
        target = structured_asp.get("target_role_archetype", "")
        target_company_type = structured_asp.get("target_company_type", "")
        target_org_context = structured_asp.get("target_org_context", "")
        realism = structured_asp.get("realism_score", "")
        options = structured_asp.get("realistic_trajectory_options", [])
        target_label = f"{target} at {target_company_type}".strip(" at") if target_company_type else target
        if target or category:
            structured_asp_str = f"\nAspiration category: {category} | Target role: {target_label} | Realism: {realism}"
        if target_org_context:
            structured_asp_str += f"\nTarget org context: {target_org_context}"
        if options:
            structured_asp_str += f"\nTrajectory options: {'; '.join(options[:3])}"

    last_session_str = f"\nLast session summary: {last_summary}" if last_summary else ""

    # Build a specific note about what's still needed for returning users
    if is_returning:
        returning_note = (
            "This is a returning user. Their prior profile data is loaded above — use it as context, "
            "but DO NOT skip the HOOK sequence. Every new session starts at HOOK regardless of prior data. "
            "Reasons: aspirations change, org constraints change, and task clusters must be refreshed. "
            "\n\nHOOK sequence for returning users:"
            "\n1. If they upload a resume → call parse_resume, then analyze_role + infer_role_detail to refresh task clusters."
            "\n2. Acknowledge their prior aspiration and ask if it has changed, OR ask the aspiration question fresh."
            "\n   Then call interpret_aspiration with their answer, then call update_profile(aspiration=...)."
            "\n3. Confirm org constraints or ask if anything has changed. Call update_profile(org_constraints=...)."
            "\n4. Only then call generate_use_cases."
            "\n\nDO NOT present use cases in your text at any point before calling generate_use_cases."
            "\nDO NOT assume prior aspiration/constraints are still current — confirm them."
        )
    else:
        returning_note = "This is a new user — first session. Begin the HOOK sequence."

    return f"""You are an expert AI productivity coach — warm, direct, and perceptive. \
You help professionals figure out exactly where AI fits into their actual work — not theory, not hype.

{returning_note}

## Core Rules
- You lead the conversation. The user reacts and corrects — they never navigate or fill forms.
- ONE question per turn. Never stack questions.
- Resumes lie. People bloat titles and achievements. Treat the resume as a starting point, not the truth.
- Generic insights have zero value. "AI can help PMs with data analysis" tells them nothing. \
  "You probably spend 3 hours a week writing PRD updates that three stakeholders will misread anyway — \
  here's how AI changes that" is worth something.
- The org context is everything. A PM at Cigna navigating HIPAA, enterprise IT governance, \
  and a 50,000-person bureaucracy has a completely different AI adoption path than a PM at a Series A startup. \
  Factor this in — always.
- Keep responses under 200 words. Be conversational, not comprehensive.
- Never show raw JSON. Translate everything into natural prose.
- Never announce tool calls. Just use the result to inform what you say next.
- **No tech jargon without explanation.** If you name a tool (e.g. Microsoft Copilot, Azure OpenAI), \
  immediately say in plain words what it does: "Microsoft Copilot (Microsoft's AI writing assistant, \
  built into Word and Outlook)". Never assume the user knows what any tool name means.
- **No engineering language.** A Product Manager does not care about "pipelines", "deployments", \
  "APIs", or "automation workflows". Speak in their language: "instead of manually doing X, \
  you describe what you need and the AI drafts it in seconds."
- **Always connect to their world.** Every observation, use case, and learning step should reference \
  something specific about their role, their company, or their aspiration. \
  "This will help you" is weak. "This is exactly how a Director-level PM at Cigna would frame this \
  to their leadership team" is what builds trust.

## The Real Goal of This Coaching Session
Before recommending anything, you need to understand two things that nobody puts on their resume:

1. **What are they actually trying to accomplish?** Not "learn AI" — that's not a goal. \
   The real answers sound like: "I want to stop staying late writing stakeholder updates", \
   "I want to be the person in the room who knows this stuff", "I'm quietly looking for a new job \
   and want to upskill", "My CEO keeps asking about AI and I have no idea what to say." \
   You need to surface this — ask the right question.

2. **What can they actually use?** A recommendation that violates their company's data policy \
   or requires IT approval that will take 6 months is useless. Large enterprises (healthcare especially) \
   often have strict rules about what tools are approved. You need to know this before recommending anything.

## Coaching Phases

### HOOK
Goal: Build trust by showing you understand their *actual* situation — not just what's on their resume.

Flow (follow this sequence):
1. Get role data (from resume or typed description).
2. Call `analyze_role` once you have title + context.
3. Call `infer_role_detail` immediately after — pass the role as a full description. \
   This reveals what they actually do all day (task clusters + effort %). \
   Do NOT announce this call; use the result to inform your observation.
4. Call `infer_cultural_tone` silently in the same pass. Use the result to calibrate \
   your own voice for the rest of the session — never mention you did this.
5. Mirror back ONE sharp, specific observation. Construction recipe: \
   (a) Find the task cluster with the HIGHEST effort_pct in the task clusters above. \
   (b) Name it, name the percentage. \
   (c) Name the SPECIFIC FRICTION that makes that cluster hard at this company/domain — \
       NOT generic ("regulatory factors are complex") but the actual mechanism: \
       e.g. for a healthcare PM: "every feature has to clear clinical, actuarial, and compliance sign-off before it ships — that's a 3x multiplier on every roadmap decision." \
       e.g. for an enterprise PM: "you're not prioritizing features, you're negotiating stakeholder veto power across 5 org silos." \
   (d) Imply there's a way through — the observation should feel like "yes, that's exactly it" not a performance review. \
   BAD: "30% of your role involves strategizing around healthcare products within regulation constraints." \
   GOOD: "You're spending nearly a third of your week on product strategy — but at Cigna, that's not just roadmap calls, it's threading every decision through clinical, actuarial, and compliance. That approval overhead alone turns a 2-week decision cycle into a 2-month one." \
   Keep it 2-3 sentences. One specific insight, not a list.
6. Ask the aspiration question — the most important question in the whole session: \
   "Before we dig in — what's the actual thing you're hoping this helps you with? \
   Could be totally practical like 'I spend too much time writing' or more about optics like \
   'I want to sound credible when my CEO asks about AI.' No wrong answer."
7. When they answer, you MUST call BOTH tools in sequence — no exceptions: \
   a. `interpret_aspiration` — pass their EXACT statement verbatim. This is the single most \
      important tool call in the session. The structured result (target_role_archetype, \
      aspiration_category, realism_score) powers the quality of everything downstream — \
      use cases, learning path, and personalization framing. Skipping it produces generic output. \
      DO NOT skip it. DO NOT substitute with update_profile alone. \
   b. `update_profile` — pass aspiration = their exact raw statement. \
   If you call update_profile(aspiration=...) without having first called interpret_aspiration, \
   the rest of the session will be generic and fail to connect to their actual goal. \
   This is a critical, unrecoverable mistake.

Transition to CONSTRAINTS: When you have their aspiration.

### CONSTRAINTS (part of HOOK — one follow-up question)
Goal: Understand what AI tools they can realistically use before recommending anything.

Ask ONE question based on their company context. For large enterprises / regulated industries: \
"One practical thing — does [company] have any guidance on AI tools? Some large orgs have approved \
tools lists, others have restrictions on what data you can put into external tools. \
Just want to make sure anything I recommend you can actually use."

CRITICAL: If their answer is vague (e.g. "closed", "restricted", "limited", "yes", "no external tools"), \
do NOT store that vague answer and move on. Ask one follow-up to get specifics: \
"Got it — just to make sure I recommend the right tools: is Microsoft 365 Copilot available? \
Azure OpenAI? Or is it more internal-only tools?" \
Store the specific answer. The org_constraints stored must be specific enough to name \
what IS and IS NOT available (e.g. "Microsoft 365 Copilot approved; no external AI SaaS; \
no uploading data outside Microsoft ecosystem").

Transition to REVEAL: When you have aspiration + org constraints.

### REVEAL
Goal: Surface 3 AI opportunities that feel *specific and slightly surprising* — not obvious.

**HARD REQUIREMENT: Never call `generate_use_cases` unless task_clusters, aspiration, AND \
org_constraints are ALL present in the Current User Context above. \
If any are missing, you MUST complete the HOOK steps to fill them in first. \
The system will return an error and refuse to generate use cases without them.**

**ANTI-HALLUCINATION RULE — this is a common and critical mistake:** \
NEVER write use cases in your text response without having called `generate_use_cases` first. \
If you describe AI opportunities or use cases as prose before calling the tool, the use cases \
will NOT be in the user's profile. When the user then picks one ("tell me more about roadmap \
prioritization"), `prescribe_learning_path` will fail with "No use case found." \
The tool call is mandatory — it is not interchangeable with describing use cases in text. \
When in doubt: call the tool, THEN describe the results.

Steps:
1. Call `generate_use_cases` — it uses task clusters, aspiration, and org_constraints internally.
2. Present the use cases using this narrative structure for each one: \
   **"Right now"** — describe the manual, tedious reality they live today (1 sentence, concrete) \
   **"With AI"** — describe what specifically changes (tool + mechanism, 1-2 sentences) \
   **"Why this matters for [their goal]"** — explicitly connect to their stated aspiration. \
   If they want a promotion: "This frees 3 hours a week you can reinvest in [Director-level work]" \
   or "Demonstrating this capability is exactly what separates PM from Director candidates."
3. Before listing use cases, open with ONE sentence that sets the narrative frame: \
   e.g. "Here's where AI closes the gap between where you are and where you're going." \
   Always tie the setup to their specific aspiration.
4. After the 3 use cases, end with this EXACT line (numbered so the user can reply with 1, 2, or 3): \
   "**Which one do you want to start with — 1, 2, or 3?**"
   Label each use case with its number (1., 2., 3.) in your output. \
   This makes it unambiguous for the user to pick.

Transition to PRESCRIBE: When user picks a number (1, 2, or 3) or clearly engages with one use case.

### PRESCRIBE (Phase B)
When the user picks a use case number or clearly indicates which one — call `prescribe_learning_path`. \
CRITICAL: Always pass `use_case_index` as the integer (0 for "1", 1 for "2", 2 for "3"). \
Do NOT rely on title matching — it fails when the user says a keyword like "prioritization" that \
partially matches the wrong use case. The index is always reliable. \
If the user's reply is ambiguous (e.g. "prioritization" when multiple use cases could match), \
reply with: "Just to confirm — did you mean use case 1 (X), 2 (Y), or 3 (Z)?" Then wait for a number.

**CRITICAL PRESCRIBE RULE:**
When `prescribe_learning_path` returns `formatted_output_delivered: true`, the full personalized \
learning path has ALREADY been delivered to the user as a separate message — it is already on \
their screen. Do NOT repeat it. Do NOT paraphrase it. Do NOT add any intro before it. \
Your ENTIRE response should be exactly this one line: \
"Want me to map out the path for one of the other use cases too?"

If `has_content` is false or `error` is present: \
Say ONLY: "I hit a snag finding resources for that one — want me to try again or look at one of the other use cases?"

## Tool Calling Guide
- `parse_resume`: When user pastes resume text.
- `analyze_role`: Once you have title + company or domain. Do this before any observation.
- `infer_role_detail`: Immediately after analyze_role. Pass the full role description.
- `infer_cultural_tone`: Immediately after analyze_role. Pass org signals. Never announce.
- `interpret_aspiration`: Once user answers the aspiration question. Pass their exact statement.
- `update_profile`: Store aspiration (raw statement) and org_constraints as the user reveals them.
- `generate_use_cases`: At the start of REVEAL, after aspiration + org_constraints are known.
- `prescribe_learning_path`: When user engages with a specific use case. Pass use_case_index (0/1/2).

## Current User Context
Name: {name}
Current phase: {phase}
Profile: {profile_str}{role_archetype_str}{task_cluster_str}{tone_str}{aspiration_str}{structured_asp_str}{org_str}{last_session_str}"""


# ── Coordinator class ──────────────────────────────────────────────────────────

class CoachCoordinator:
    def __init__(self, user_model: dict):
        self.user_model = user_model
        self.user_id = user_model.get("user_id", "default_user")
        self.session_id = f"{self.user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Load durable persona context and merge into profile on init
        persona = get_user_context(self.user_id)
        if persona:
            profile = self.user_model.setdefault("profile", {})
            for key, val in persona.items():
                if val and key not in profile:
                    profile[key] = val

        # Validate stored task_clusters format.
        # The old role_detail_agent produced {name, activities, tools_used} per cluster.
        # The new infer_role_detail produces {name, effort_pct, ai_opportunity, description}.
        # If task_clusters exist but lack effort_pct, they're stale — clear them.
        profile = self.user_model.setdefault("profile", {})
        task_clusters = profile.get("task_clusters", [])
        if task_clusters and not any("effort_pct" in c for c in task_clusters):
            profile.pop("task_clusters", None)
            profile.pop("ai_opportunity_density", None)
            profile.pop("effort_distribution", None)
            profile.pop("work_pattern", None)
            profile.pop("aspiration_structured", None)

        # ALWAYS reset phase to "hook" at the start of a new session, regardless
        # of what phase was saved from the last session. Phase advances during
        # the conversation via _advance_phase(). Returning users with full profile
        # data still run the HOOK sequence — it just goes faster because context
        # is already loaded and the coordinator can reference prior answers.
        coaching_state = self.user_model.setdefault("coaching_state", {})
        coaching_state["current_phase"] = "hook"
        # Also clear use_cases from profile so returning users get fresh use cases
        # generated after confirming their current aspiration and constraints.
        profile.pop("use_cases", None)

        # Start fresh trace for this session
        clear_trace(self.session_id)

        # Callback for emitting intermediate messages (set per-turn in chat())
        # Allows PRESCRIBE to surface the formatted_output as a separate bubble
        # before the LLM writes the follow-up question.
        self._emit = lambda msg: None

        self.messages: list = [
            {"role": "system", "content": _build_system_prompt(user_model)}
        ]

    def get_opening_message(self) -> str:
        """
        Generate the coach's first message.
        - Returning users: LLM generates a personalized welcome-back.
        - New users: canned greeting asking how they'd like to start.
        """
        name = self.user_model.get("name", "there")
        is_returning = bool(self.user_model.get("interaction_history"))

        if is_returning:
            last_summary = self.user_model.get("coaching_state", {}).get("last_conversation_summary", "")
            phase = self.user_model.get("coaching_state", {}).get("current_phase", "hook")
            profile = self.user_model.get("profile", {})
            prior_context = ""
            if profile.get("title"):
                prior_context += f"Role: {profile.get('seniority', '')} {profile['title']}"
            if profile.get("company"):
                prior_context += f" at {profile['company']}"
            if profile.get("aspiration"):
                prior_context += f". Goal: {profile['aspiration']}"
            trigger = (
                f"[SYSTEM: Generate a warm, brief welcome-back message for {name}. "
                f"Current phase: {phase}. Prior context: {prior_context}. "
                f"Last session: {last_summary or 'No summary available'}. "
                f"Keep it under 3 sentences. Reference something specific from their context. "
                f"Do not use brackets or system language in your reply.]"
            )
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=self.messages + [{"role": "user", "content": trigger}],
                temperature=0.7,
            )
            opening = response.choices[0].message.content.strip()
        else:
            opening = (
                f"Hey {name}! I'm your AI productivity coach.\n\n"
                "I'll help you figure out exactly where AI can save you time — "
                "specific to your role, your tools, and your goals. Not generic tips.\n\n"
                "To start: **tell me what you do**, or use the **📎 Attach resume** button below "
                "and I'll read it myself. Which works better for you?"
            )

        self.messages.append({"role": "assistant", "content": opening})
        return opening

    def chat(
        self,
        user_message: str,
        file_bytes: bytes = None,
        filename: str = None,
        on_intermediate_message: callable = None,
    ) -> str:
        """
        Process one user turn. Returns the coach's final response text.
        Also updates self.user_model in place.

        on_intermediate_message: if provided, called with each intermediate
        message string before the final LLM response. Used by the UI to render
        separate chat bubbles for streaming coaching insights (e.g. the full
        PRESCRIBE learning path delivered before the follow-up question).
        """
        # Wire the intermediate-message callback for this turn
        self._emit = on_intermediate_message or (lambda msg: None)

        # Set context vars so the LLM tracer knows which session/phase is active
        set_active_session(self.session_id)
        current_phase = self.user_model.get("coaching_state", {}).get("current_phase", "hook")
        set_active_phase(current_phase)

        # If a file was uploaded, parse it in Python first and inject into the message
        if file_bytes and filename:
            from coach.tools.parse_resume import parse_resume as _parse_file
            parsed = _parse_file(file_bytes, filename)
            if "error" not in parsed:
                self._merge_profile(parsed)
                # Rebuild system prompt with updated profile
                self.messages[0] = {"role": "system", "content": _build_system_prompt(self.user_model)}
                inject = json.dumps(parsed, indent=2)
                full_message = (
                    f"{user_message}\n\n"
                    f"[Resume parsed successfully. Extracted profile:\n{inject}]"
                )
            else:
                full_message = f"{user_message}\n\n[Resume parse failed: {parsed.get('error')}]"
        else:
            full_message = user_message

        self.messages.append({"role": "user", "content": full_message})

        # Tool-calling loop
        response_text = self._run_tool_loop()

        # Update user model state
        self._record_interaction(user_message, response_text)

        return response_text

    # ── Private helpers ────────────────────────────────────────────────────────

    def _run_tool_loop(self) -> str:
        """Run the LLM with tool calling until we get a final text response."""
        while True:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=self.messages,
                tools=_TOOLS,
                tool_choice="auto",
            )
            msg = response.choices[0].message

            if msg.tool_calls:
                # Append the assistant message (with tool_calls)
                assistant_entry = {
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                }
                self.messages.append(assistant_entry)

                # Execute each tool and append results
                for tc in msg.tool_calls:
                    result = self._execute_tool(tc.function.name, tc.function.arguments)
                    self.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": json.dumps(result),
                        }
                    )
                # Rebuild the system prompt so the next LLM call (or final response)
                # sees the freshly updated profile — task_clusters, tone, aspiration, etc.
                self.messages[0] = {"role": "system", "content": _build_system_prompt(self.user_model)}
            else:
                # Final text response
                text = msg.content or ""
                self.messages.append({"role": "assistant", "content": text})
                return text

    def _execute_tool(self, name: str, arguments_json: str) -> dict:
        """Dispatch a tool call and return the result dict."""
        try:
            args = json.loads(arguments_json)
        except json.JSONDecodeError:
            return {"error": "Invalid arguments JSON"}

        profile = self.user_model.get("profile", {})
        _phase = self.user_model.get("coaching_state", {}).get("current_phase", "hook")

        if name == "parse_resume":
            t0 = time.time()
            result = parse_resume_from_text(args.get("resume_text", ""))
            record_event(
                self.session_id, phase=_phase, agent="parse_resume",
                inputs={"text_len": len(args.get("resume_text", ""))},
                outputs={"title": result.get("title"), "company": result.get("company"),
                         "seniority": result.get("seniority"), "domain": result.get("domain")},
                duration_ms=int((time.time() - t0) * 1000),
                status="error" if "error" in result else "ok",
                error=result.get("error"),
            )
            if "error" not in result:
                self._merge_profile(result)

        elif name == "analyze_role":
            t0 = time.time()
            result = analyze_role(
                title=args.get("title", ""),
                company=args.get("company", ""),
                domain=args.get("domain", ""),
                seniority=args.get("seniority", ""),
                company_size=args.get("company_size", ""),
            )
            record_event(
                self.session_id, phase=_phase, agent="analyze_role",
                inputs={"title": args.get("title"), "company": args.get("company")},
                outputs={"role_archetype": result.get("role_archetype"),
                         "org_shape": result.get("org_shape"),
                         "ai_applicability": result.get("ai_applicability")},
                duration_ms=int((time.time() - t0) * 1000),
                status="error" if "error" in result else "ok",
                error=result.get("error"),
            )
            if "error" not in result:
                self._merge_role_context(result)

        elif name == "infer_role_detail":
            t0 = time.time()
            result = infer_role_detail(
                role=args.get("role", profile.get("title", "")),
                company=profile.get("company", ""),
                domain=profile.get("domain", ""),
                seniority=profile.get("seniority", ""),
                resume=profile.get("resume_text"),
                role_context={
                    "role_archetype": profile.get("role_archetype", ""),
                    "org_shape": profile.get("org_shape", ""),
                    "ai_applicability_constraints": profile.get("ai_applicability_constraints", ""),
                },
                user_id=self.user_id,
            )
            record_event(
                self.session_id, phase=_phase, agent="infer_role_detail",
                inputs={"role": args.get("role") or profile.get("title"), "company": profile.get("company")},
                outputs={"task_cluster_count": len(result.get("task_clusters", [])),
                         "work_pattern": result.get("work_pattern"),
                         "ai_opportunity_density": result.get("ai_opportunity_density")},
                duration_ms=int((time.time() - t0) * 1000),
                status="error" if "error" in result else "ok",
                error=result.get("error"),
            )
            if "error" not in result:
                self._merge_role_detail(result)

        elif name == "infer_cultural_tone":
            t0 = time.time()
            result = infer_cultural_tone(
                user_id=self.user_id,
                session_id=self.session_id,
                company=args.get("company", "") or profile.get("company", ""),
                domain=args.get("domain", "") or profile.get("domain", ""),
                seniority=args.get("seniority", "") or profile.get("seniority", ""),
                org_shape=args.get("org_shape", "") or profile.get("org_shape", ""),
            )
            record_event(
                self.session_id, phase=_phase, agent="infer_cultural_tone",
                inputs={"company": profile.get("company"), "seniority": profile.get("seniority")},
                outputs={"tone_style": result.get("tone_style"),
                         "learning_style": result.get("learning_style"),
                         "cultural_profile_tag": result.get("cultural_profile_tag")},
                duration_ms=int((time.time() - t0) * 1000),
                status="error" if "error" in result else "ok",
                error=result.get("error"),
            )
            if "error" not in result:
                self._merge_cultural_tone(result)

        elif name == "interpret_aspiration":
            t0 = time.time()
            aspiration_statement = args.get("aspiration_statement", "")
            result = interpret_aspiration(
                user_id=self.user_id,
                session_id=self.session_id,
                aspiration_statement=aspiration_statement,
                profile=profile,
            )
            record_event(
                self.session_id, phase=_phase, agent="interpret_aspiration",
                inputs={"aspiration_statement": aspiration_statement[:100]},
                outputs={"target_role_archetype": result.get("target_role_archetype"),
                         "aspiration_category": result.get("aspiration_category"),
                         "realism_score": result.get("realism_score")},
                duration_ms=int((time.time() - t0) * 1000),
                status="error" if "error" in result else "ok",
                error=result.get("error"),
            )
            if "error" not in result:
                self._merge_aspiration(result)

        elif name == "generate_use_cases":
            # Hard guard: refuse to generate use cases without the minimum required context.
            # Without these, the LLM produces generic, role-inappropriate use cases.
            missing_prereqs = []
            if not profile.get("task_clusters"):
                missing_prereqs.append("task_clusters (call infer_role_detail first)")
            if not profile.get("aspiration"):
                missing_prereqs.append("aspiration (ask the aspiration question and call interpret_aspiration first)")
            if not profile.get("org_constraints"):
                missing_prereqs.append("org_constraints (ask the org constraints question and call update_profile first)")
            if missing_prereqs:
                result = {
                    "error": "Prerequisites missing — cannot generate use cases yet.",
                    "missing": missing_prereqs,
                    "instruction": "Complete the HOOK phase first. " + " | ".join(missing_prereqs),
                }
                record_event(
                    self.session_id, phase=_phase, agent="generate_use_cases",
                    inputs={"title": profile.get("title"), "missing_prereqs": missing_prereqs},
                    outputs={},
                    duration_ms=0,
                    status="skip",
                    error="Prerequisites missing: " + ", ".join(missing_prereqs),
                )
            else:
                t0 = time.time()
                result = generate_use_cases(
                    title=args.get("title", "") or profile.get("title", ""),
                    seniority=args.get("seniority", "") or profile.get("seniority", ""),
                    domain=args.get("domain", "") or profile.get("domain", ""),
                    tools_known=args.get("tools_known") or profile.get("tools_known", []),
                    aspiration=profile.get("aspiration", ""),
                    org_constraints=profile.get("org_constraints", ""),
                    company=profile.get("company", ""),
                    task_clusters=profile.get("task_clusters", []),
                    session_id=self.session_id,
                    aspiration_structured=profile.get("aspiration_structured", {}),
                    archetype_id=profile.get("archetype_id"),
                )
                use_cases = result if isinstance(result, list) else []
                record_event(
                    self.session_id, phase=_phase, agent="generate_use_cases",
                    inputs={"title": profile.get("title"), "aspiration": profile.get("aspiration"),
                            "task_cluster_count": len(profile.get("task_clusters", []))},
                    outputs={"use_case_count": len(use_cases),
                             "titles": [uc.get("title") for uc in use_cases[:3]]},
                    duration_ms=int((time.time() - t0) * 1000),
                    status="error" if not use_cases else "ok",
                    error=None if use_cases else "No use cases returned",
                )
                self._advance_phase("reveal")
                self.user_model["profile"]["use_cases"] = use_cases

        elif name == "prescribe_learning_path":
            use_cases = profile.get("use_cases", [])
            use_case_index = args.get("use_case_index", 0)
            # Find use case by index or by title match
            use_case = None
            if use_cases:
                if isinstance(use_case_index, int) and 0 <= use_case_index < len(use_cases):
                    use_case = use_cases[use_case_index]
                elif args.get("use_case_title"):
                    title_hint = args["use_case_title"].lower()
                    use_case = next(
                        (uc for uc in use_cases if title_hint in uc.get("title", "").lower()),
                        use_cases[0] if use_cases else None,
                    )
                else:
                    use_case = use_cases[0]
            if not use_case:
                result = {"error": "No use case found. Run generate_use_cases first.", "has_content": False}
                record_event(
                    self.session_id, phase="prescribe", agent="prescribe_learning_path",
                    inputs={}, outputs={},
                    duration_ms=0, status="error",
                    error="No use case found. Run generate_use_cases first.",
                )
            else:
                # Emit pre-message so the user sees this BEFORE the learning path narrative
                uc_title = use_case.get("title", "this use case")
                self._emit(
                    f"On it — putting together your personalized learning path for **{uc_title}**. "
                    f"I'm searching YouTube tutorials, articles, and GitHub repos "
                    f"and filtering for what's actually relevant to your role and goal..."
                )

                t0 = time.time()
                try:
                    result = prescribe_learning_path(
                        use_case=use_case,
                        user_id=self.user_id,
                        session_id=self.session_id,
                        profile=profile,
                    )
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    result = {"error": f"prescribe_learning_path raised: {e}", "has_content": False}
                record_event(
                    self.session_id, phase="prescribe", agent="prescribe_learning_path",
                    inputs={"use_case_title": use_case.get("title"),
                            "suggested_tool": use_case.get("suggested_tool")},
                    outputs={"has_content": result.get("has_content"),
                             "module_count": len(result.get("learning_modules", [])),
                             "output_len": len(result.get("formatted_output", ""))},
                    duration_ms=int((time.time() - t0) * 1000),
                    status="error" if "error" in result else "ok",
                    error=result.get("error"),
                )
                if "error" not in result:
                    self._merge_learning_path(result)
                    self._advance_phase("prescribe")

                # If we have a good formatted_output, emit it as an intermediate
                # message (separate bubble) so the LLM's follow-up question
                # appears as a second, shorter bubble after the full narrative.
                if result.get("has_content") and result.get("formatted_output"):
                    self._emit(result["formatted_output"])
                    # Signal to the LLM that the output was already delivered —
                    # its only job now is to write the follow-up question.
                    result = {
                        k: v for k, v in result.items()
                        if k != "formatted_output"
                    }
                    result["formatted_output_delivered"] = True

        elif name == "update_profile":
            profile = self.user_model.setdefault("profile", {})
            for key in ("aspiration", "org_constraints", "title", "company", "domain"):
                if args.get(key):
                    profile[key] = args[key]
            # Write durable fields to persona_context
            durable = {k: args[k] for k in ("aspiration", "org_constraints", "title", "company", "domain") if args.get(k)}
            if durable:
                update_shared_context(self.user_id, durable)
            result = {"status": "profile updated", "fields": list(args.keys())}
            record_event(
                self.session_id, phase=_phase, agent="update_profile",
                inputs=args,
                outputs={"fields_updated": list(durable.keys()) if durable else list(args.keys())},
                duration_ms=0, status="ok",
            )

        else:
            result = {"error": f"Unknown tool: {name}"}

        # Rebuild system prompt after any profile update
        self.messages[0] = {"role": "system", "content": _build_system_prompt(self.user_model)}
        return result

    def _merge_profile(self, parsed: dict):
        profile = self.user_model.setdefault("profile", {})
        for key, val in parsed.items():
            if val:
                profile[key] = val
        # Write stable identity fields to persona_context
        durable = {k: parsed[k] for k in ("title", "company", "domain", "seniority") if parsed.get(k)}
        if durable:
            update_shared_context(self.user_id, durable)

    def _merge_role_context(self, context: dict):
        profile = self.user_model.setdefault("profile", {})
        profile["role_archetype"] = context.get("role_archetype", "")
        profile["role_archetype_tag"] = context.get("role_archetype_tag", "")
        profile["org_shape"] = context.get("org_shape", "")
        profile["cross_functional_density"] = context.get("cross_functional_density", "")
        profile["ai_applicability"] = context.get("ai_applicability", "")
        profile["ai_applicability_constraints"] = context.get("ai_applicability_constraints", "")
        # Write to persona_context for cross-session persistence
        update_shared_context(self.user_id, {
            "role_archetype": profile["role_archetype"],
            "org_shape": profile["org_shape"],
            "ai_applicability_constraints": profile["ai_applicability_constraints"],
        })

    def _merge_role_detail(self, result: dict):
        profile = self.user_model.setdefault("profile", {})
        profile["task_clusters"] = result.get("task_clusters", [])
        profile["ai_opportunity_density"] = result.get("ai_opportunity_density", 0.5)
        profile["effort_distribution"] = result.get("effort_distribution", {})
        profile["work_pattern"] = result.get("work_pattern", "")
        # Phase C: store matched archetype_id so generate_use_cases + flywheel_writer can use it
        if result.get("archetype_id"):
            profile["archetype_id"] = result["archetype_id"]

    def _merge_cultural_tone(self, result: dict):
        profile = self.user_model.setdefault("profile", {})
        profile["cultural_profile_tag"] = result.get("cultural_profile_tag", "")
        profile["tone_style"] = result.get("tone_style", "")
        profile["learning_style"] = result.get("learning_style", "")
        profile["working_style_summary"] = result.get("working_style_summary", "")
        # Sync to preferences
        prefs = self.user_model.setdefault("preferences", {})
        prefs["tone"] = result.get("tone_style", "")
        prefs["learning_style"] = result.get("learning_style", "")

    def _merge_aspiration(self, result: dict):
        profile = self.user_model.setdefault("profile", {})
        profile["aspiration_structured"] = result
        profile["target_role_archetype"] = result.get("target_role_archetype", "")
        # Write to persona_context — includes new target org fields
        update_shared_context(self.user_id, {
            "aspiration_category": result.get("aspiration_category", ""),
            "target_role_archetype": result.get("target_role_archetype", ""),
            "target_company_type": result.get("target_company_type", ""),
            "target_org_context": result.get("target_org_context", ""),
            "realism_score": result.get("realism_score", ""),
        })

    def _merge_learning_path(self, result: dict):
        profile = self.user_model.setdefault("profile", {})
        profile["last_learning_path"] = {
            "use_case_title": result.get("use_case_title", ""),
            "formatted_output": result.get("formatted_output", ""),
            "intro_text": result.get("intro_text", ""),
            "closing_cta": result.get("closing_cta", ""),
            "module_count": len(result.get("learning_modules", [])),
            "has_content": result.get("has_content", False),
        }

    def _advance_phase(self, phase: str):
        self.user_model["coaching_state"]["current_phase"] = phase
        set_active_phase(phase)

    def _record_interaction(self, user_message: str, assistant_response: str):
        phase = self.user_model["coaching_state"].get("current_phase", "hook")

        # Append to interaction history
        self.user_model["interaction_history"].append(
            {
                "date": datetime.utcnow().isoformat(),
                "phase": phase,
                "user_message": user_message[:200],
                "assistant_summary": assistant_response[:300],
            }
        )

        # Keep last 50 interactions
        self.user_model["interaction_history"] = self.user_model["interaction_history"][-50:]

        # Update last conversation summary with the most recent assistant turn
        self.user_model["coaching_state"]["last_conversation_summary"] = (
            assistant_response[:400] if assistant_response else None
        )
