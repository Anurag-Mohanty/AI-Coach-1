"""
seed_archetypes.py — Generate or refresh role archetype seed data.

Run this script once (or when refreshing archetypes) to populate seed.json
using the live pipeline. It calls infer_role_detail and find_ai_blind_spots
for synthetic profiles representing each target archetype.

Usage:
    cd /path/to/AI-Coach-1
    python3 coach/intelligence/seed_archetypes.py

Output: coach/intelligence/archetypes/seed.json (overwrites existing)

NOTE: This makes real LLM calls (GPT-4o + GPT-4) for each archetype.
Cost: ~12 archetypes × ~2 LLM calls = ~24 API calls (~$0.10-0.20 total).
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Ensure project root is on the path
_PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from coach.intelligence.archetype_store import RoleArchetypeStore
from agents.gap_analysis_agent.use_case_miss_agent import find_ai_blind_spots

# Synthetic profiles for each archetype
# Each entry: (archetype_id, metadata, resume_data, role_context)
SEED_PROFILES = [
    {
        "archetype_id": "senior_pm_healthcare_enterprise",
        "seniority": "Senior",
        "domain": "Healthcare",
        "org_shape": "hierarchical",
        "role_examples": [
            "Senior Product Manager at Cigna",
            "Senior PM at Anthem",
            "Senior PM at UnitedHealth"
        ],
        "aspiration_patterns": [
            "Director of Product at healthcare enterprise",
            "VP of Product at healthcare startup",
            "Head of Product at digital health company"
        ],
        "resume_data": {
            "title": "Senior Product Manager",
            "seniority": "Senior",
            "company": "Anthem",
            "domain": "Healthcare",
            "experience": "5 years in healthcare tech product management",
            "skills": ["product strategy", "stakeholder management", "agile", "clinical workflow analysis"],
        },
        "role_context": {
            "role_archetype": "Senior Product Manager at a large healthcare insurance enterprise",
            "org_shape": "hierarchical",
            "cross_functional_density": "high",
            "ai_applicability_constraints": "Microsoft 365 Copilot approved; HIPAA compliance required for all AI tools; no external SaaS with PHI access",
            "ops_or_strategy_bias": "balanced",
        },
    },
    {
        "archetype_id": "director_healthcare_hierarchical",
        "seniority": "Director",
        "domain": "Healthcare",
        "org_shape": "hierarchical",
        "role_examples": [
            "Director of Product Management at Cigna",
            "Director of Product at Elevance Health",
            "Director PM at Kaiser"
        ],
        "aspiration_patterns": [
            "VP of Product at healthcare enterprise",
            "VP of Product at healthcare startup",
            "SVP Product at digital health company"
        ],
        "resume_data": {
            "title": "Director of Product Management",
            "seniority": "Director",
            "company": "Cigna",
            "domain": "Healthcare",
            "experience": "10 years in healthcare product, managing 4 PMs across 2 product lines",
            "skills": ["portfolio management", "stakeholder strategy", "regulatory navigation", "team leadership"],
        },
        "role_context": {
            "role_archetype": "Director of Product Management at a large healthcare enterprise with regulatory constraints",
            "org_shape": "hierarchical",
            "cross_functional_density": "high",
            "ai_applicability_constraints": "Microsoft 365 Copilot approved; HIPAA and CMS regulatory constraints; AI outputs require clinical review before patient-facing use",
            "ops_or_strategy_bias": "strategy-leaning",
        },
    },
    {
        "archetype_id": "vp_product_enterprise",
        "seniority": "VP",
        "domain": "Healthcare",
        "org_shape": "hierarchical",
        "role_examples": [
            "VP of Product at Cigna",
            "VP Product at Salesforce",
            "VP Product Management at UnitedHealth"
        ],
        "aspiration_patterns": [
            "SVP or Chief Product Officer at enterprise",
            "VP at FAANG tech company",
            "Founding CPO at growth-stage startup"
        ],
        "resume_data": {
            "title": "Vice President of Product",
            "seniority": "VP",
            "company": "Salesforce",
            "domain": "SaaS",
            "experience": "15 years in product leadership, managing Directors across 3 product divisions",
            "skills": ["executive communication", "portfolio strategy", "organizational design", "market positioning"],
        },
        "role_context": {
            "role_archetype": "VP of Product at a large enterprise SaaS company managing multiple product lines",
            "org_shape": "hierarchical",
            "cross_functional_density": "very high",
            "ai_applicability_constraints": "Enterprise AI policies under development; approved vendors include Microsoft Copilot; use of AI in customer-facing features requires legal review",
            "ops_or_strategy_bias": "strategy-dominant",
        },
    },
    {
        "archetype_id": "vp_product_startup",
        "seniority": "VP",
        "domain": "SaaS",
        "org_shape": "flat",
        "role_examples": [
            "VP of Product at Series B SaaS",
            "VP Product at health tech startup",
            "VP Product at fintech startup"
        ],
        "aspiration_patterns": [
            "CPO at growth-stage startup",
            "VP Product at larger company",
            "Co-founder with product responsibilities"
        ],
        "resume_data": {
            "title": "VP of Product",
            "seniority": "VP",
            "company": "GrowthStack",
            "domain": "SaaS",
            "experience": "8 years in product, joined as first PM, now leading product at 80-person B2B SaaS company",
            "skills": ["product-market fit", "hands-on execution", "GTM collaboration", "investor communication"],
        },
        "role_context": {
            "role_archetype": "VP of Product at a growth-stage B2B SaaS startup with lean team and high ownership",
            "org_shape": "flat",
            "cross_functional_density": "high",
            "ai_applicability_constraints": "No formal AI policy; team uses ChatGPT, Notion AI, and Perplexity freely; any AI tool that doesn't touch customer PII is approved",
            "ops_or_strategy_bias": "balanced",
        },
    },
    {
        "archetype_id": "senior_pm_saas_startup",
        "seniority": "Senior",
        "domain": "SaaS",
        "org_shape": "flat",
        "role_examples": [
            "Senior PM at B2B SaaS startup",
            "Senior Product Manager at early-stage enterprise SaaS"
        ],
        "aspiration_patterns": [
            "Head of Product at SaaS startup",
            "Director of Product at enterprise SaaS",
            "VP Product at growth-stage startup"
        ],
        "resume_data": {
            "title": "Senior Product Manager",
            "seniority": "Senior",
            "company": "DevTools Inc",
            "domain": "SaaS",
            "experience": "4 years in B2B SaaS product management at startups under 100 people",
            "skills": ["customer discovery", "roadmap prioritization", "agile delivery", "GTM support"],
        },
        "role_context": {
            "role_archetype": "Senior PM at a B2B SaaS startup, owns an entire product area end-to-end",
            "org_shape": "flat",
            "cross_functional_density": "medium",
            "ai_applicability_constraints": "No restrictions; team actively uses AI tools; ChatGPT, Notion AI, Linear AI all in use",
            "ops_or_strategy_bias": "execution-leaning",
        },
    },
    {
        "archetype_id": "senior_pm_fintech_enterprise",
        "seniority": "Senior",
        "domain": "Fintech",
        "org_shape": "hierarchical",
        "role_examples": [
            "Senior PM at JPMorgan Chase",
            "Senior Product Manager at Fidelity",
            "Senior PM at Capital One"
        ],
        "aspiration_patterns": [
            "Director of Product at fintech enterprise",
            "VP Product at fintech startup",
            "Head of Product at payments company"
        ],
        "resume_data": {
            "title": "Senior Product Manager",
            "seniority": "Senior",
            "company": "JPMorgan Chase",
            "domain": "Fintech",
            "experience": "6 years in financial services product, focused on consumer banking and payments features",
            "skills": ["regulatory navigation", "compliance documentation", "data analysis", "stakeholder alignment"],
        },
        "role_context": {
            "role_archetype": "Senior PM at a large financial services enterprise with strong regulatory constraints",
            "org_shape": "hierarchical",
            "cross_functional_density": "high",
            "ai_applicability_constraints": "OCC and Fed oversight; AI tools require risk and compliance review; no AI use in credit decisioning; approved for internal productivity tools only",
            "ops_or_strategy_bias": "balanced",
        },
    },
    {
        "archetype_id": "director_product_saas_matrix",
        "seniority": "Director",
        "domain": "SaaS",
        "org_shape": "matrix",
        "role_examples": [
            "Director of Product at Salesforce",
            "Director PM at ServiceNow",
            "Director of Product at Adobe"
        ],
        "aspiration_patterns": [
            "VP of Product at enterprise SaaS",
            "VP Product at growth-stage startup",
            "Head of Product at AI-native company"
        ],
        "resume_data": {
            "title": "Director of Product",
            "seniority": "Director",
            "company": "ServiceNow",
            "domain": "SaaS",
            "experience": "9 years in enterprise SaaS, now directing 3 PMs across workflow automation products",
            "skills": ["portfolio strategy", "cross-functional leadership", "competitive intelligence", "executive communication"],
        },
        "role_context": {
            "role_archetype": "Director of Product at a large enterprise SaaS company in a matrixed org structure",
            "org_shape": "matrix",
            "cross_functional_density": "very high",
            "ai_applicability_constraints": "Microsoft Copilot approved; Salesforce Einstein in pilot; all AI in customer-facing features requires legal and InfoSec review",
            "ops_or_strategy_bias": "strategy-leaning",
        },
    },
    {
        "archetype_id": "mid_pm_saas_enterprise",
        "seniority": "Mid",
        "domain": "SaaS",
        "org_shape": "matrix",
        "role_examples": [
            "Product Manager at Workday",
            "PM at HubSpot",
            "Product Manager at Zendesk"
        ],
        "aspiration_patterns": [
            "Senior PM at SaaS company",
            "Senior PM at startup",
            "Director of Product at enterprise"
        ],
        "resume_data": {
            "title": "Product Manager",
            "seniority": "Mid",
            "company": "HubSpot",
            "domain": "SaaS",
            "experience": "3 years in B2B SaaS product management, owns a specific feature set in a mid-size org",
            "skills": ["feature scoping", "user stories", "sprint management", "customer discovery"],
        },
        "role_context": {
            "role_archetype": "Product Manager at a mid-to-large B2B SaaS company, matrixed org",
            "org_shape": "matrix",
            "cross_functional_density": "medium",
            "ai_applicability_constraints": "HubSpot AI tools approved; ChatGPT for internal work only; no AI in customer data analysis without legal approval",
            "ops_or_strategy_bias": "execution-leaning",
        },
    },
    {
        "archetype_id": "senior_pm_retail_enterprise",
        "seniority": "Senior",
        "domain": "Retail",
        "org_shape": "hierarchical",
        "role_examples": [
            "Senior PM at Walmart",
            "Senior Product Manager at Target",
            "Senior PM at Amazon Retail"
        ],
        "aspiration_patterns": [
            "Director of Product at retail/e-commerce",
            "Head of Product at D2C brand",
            "VP Product at retail tech company"
        ],
        "resume_data": {
            "title": "Senior Product Manager",
            "seniority": "Senior",
            "company": "Walmart",
            "domain": "Retail",
            "experience": "5 years in retail tech, managing digital products that bridge physical store and e-commerce experiences",
            "skills": ["omnichannel product management", "merchandising collaboration", "large-scale data analysis", "stakeholder alignment"],
        },
        "role_context": {
            "role_archetype": "Senior PM at a large retail enterprise navigating physical-digital product complexity",
            "org_shape": "hierarchical",
            "cross_functional_density": "high",
            "ai_applicability_constraints": "Microsoft 365 Copilot approved; AI in personalization features requires Walmart data governance review; no AI-driven pricing changes without approval",
            "ops_or_strategy_bias": "balanced",
        },
    },
    {
        "archetype_id": "senior_pm_ai_focused",
        "seniority": "Senior",
        "domain": "AI",
        "org_shape": "flat",
        "role_examples": [
            "Senior PM at OpenAI",
            "Senior Product Manager at Cohere",
            "Senior PM at AI-native startup"
        ],
        "aspiration_patterns": [
            "Head of AI Product at tech company",
            "Director of Product AI at enterprise",
            "VP Product at AI-native startup"
        ],
        "resume_data": {
            "title": "Senior Product Manager",
            "seniority": "Senior",
            "company": "Cohere",
            "domain": "AI",
            "experience": "4 years in ML/AI product, working directly with research and engineering on model-facing products",
            "skills": ["model capability scoping", "AI evaluation frameworks", "developer product management", "safety and responsible AI"],
        },
        "role_context": {
            "role_archetype": "Senior PM at an AI-native company building LLM-powered products for enterprise customers",
            "org_shape": "flat",
            "cross_functional_density": "high",
            "ai_applicability_constraints": "No restrictions on internal AI use; all external products go through safety review; red-teaming required before launch",
            "ops_or_strategy_bias": "balanced",
        },
    },
    {
        "archetype_id": "director_product_fintech",
        "seniority": "Director",
        "domain": "Fintech",
        "org_shape": "hierarchical",
        "role_examples": [
            "Director of Product at Capital One",
            "Director PM at Stripe",
            "Director of Product at Plaid"
        ],
        "aspiration_patterns": [
            "VP of Product at fintech company",
            "CPO at fintech startup",
            "Head of Product at payments company"
        ],
        "resume_data": {
            "title": "Director of Product",
            "seniority": "Director",
            "company": "Capital One",
            "domain": "Fintech",
            "experience": "10 years in financial services product, directing 4 PMs across payments and lending products",
            "skills": ["regulatory strategy", "risk-adjusted product management", "API platform product", "executive communication"],
        },
        "role_context": {
            "role_archetype": "Director of Product at a large financial services company with regulatory complexity",
            "org_shape": "hierarchical",
            "cross_functional_density": "high",
            "ai_applicability_constraints": "CFPB and OCC oversight; AI in lending or credit decisions prohibited without model risk governance review; approved for internal productivity and documentation workflows",
            "ops_or_strategy_bias": "strategy-leaning",
        },
    },
    {
        "archetype_id": "head_of_product_startup",
        "seniority": "Head",
        "domain": "SaaS",
        "org_shape": "flat",
        "role_examples": [
            "Head of Product at Series A startup",
            "Head of Product at AI startup",
            "First PM / Head of Product at early-stage company"
        ],
        "aspiration_patterns": [
            "VP of Product at growth-stage startup",
            "CPO at Series B+ company",
            "Co-founder with product responsibilities"
        ],
        "resume_data": {
            "title": "Head of Product",
            "seniority": "Head",
            "company": "EarlyStage AI",
            "domain": "SaaS",
            "experience": "6 years in product, first PM hire at current company, now leading all product work at a 30-person startup",
            "skills": ["product strategy", "customer development", "hands-on execution", "fundraising narrative"],
        },
        "role_context": {
            "role_archetype": "Head of Product (first PM) at an early-stage startup with high ownership and lean team",
            "org_shape": "flat",
            "cross_functional_density": "very high",
            "ai_applicability_constraints": "No restrictions; team uses AI tools freely; AI in customer-facing features ships without formal review process",
            "ops_or_strategy_bias": "balanced",
        },
    },
]


def _run_infer_role_detail(resume_data: dict, role_context: dict) -> dict:
    """
    Call the infer_role_detail logic directly (without coordinator wrapper).
    Returns task_clusters and ai_opportunity_density.
    """
    import json as _json
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    role_str = f"{resume_data.get('seniority', '')} {resume_data.get('title', '')}".strip()
    company = resume_data.get("company", "a company")
    domain = resume_data.get("domain", "")

    prompt = f"""
You are an expert organizational consultant analyzing a product role.

Role: {role_str} at {company} in the {domain} domain
Role context: {_json.dumps(role_context, indent=2)}
Background: {resume_data.get('experience', '')}
Key skills: {', '.join(resume_data.get('skills', []))}

Identify 4-5 major task clusters that represent how this person actually spends their time.
For each cluster, estimate the % of working time and rate the AI opportunity (high/medium/low).

Return JSON only:
{{
  "task_clusters": [
    {{
      "name": "Short descriptive name (3-5 words)",
      "effort_pct": <integer, clusters should sum to ~100>,
      "ai_opportunity": "<high|medium|low>",
      "description": "One sentence describing what this cluster involves day-to-day"
    }}
  ],
  "ai_opportunity_density": <float 0.0-1.0>
}}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You analyze product management roles and return structured JSON."},
            {"role": "user", "content": prompt.strip()},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def generate_seed_data():
    """
    Generate seed archetype records by running the live pipeline for each profile.
    Overwrites seed.json with fresh LLM-generated data.
    """
    store = RoleArchetypeStore()
    results = []

    for profile in SEED_PROFILES:
        archetype_id = profile["archetype_id"]
        print(f"\n[seed] Generating: {archetype_id}")

        try:
            # Step 1: Get task_clusters from infer_role_detail logic
            print(f"  → Running infer_role_detail...")
            role_detail = _run_infer_role_detail(profile["resume_data"], profile["role_context"])
            task_clusters = role_detail.get("task_clusters", [])
            ai_density = role_detail.get("ai_opportunity_density", 0.7)
            print(f"  → Got {len(task_clusters)} task clusters")

            # Step 2: Get blind spots from use_case_miss_agent
            print(f"  → Running find_ai_blind_spots...")
            role_ctx = {
                "role_archetype": profile["role_context"].get("role_archetype", ""),
                "company": profile["resume_data"].get("company", ""),
                "domain": profile["resume_data"].get("domain", ""),
                "org_shape": profile["role_context"].get("org_shape", ""),
                "ai_applicability_constraints": profile["role_context"].get("ai_applicability_constraints", ""),
            }
            blind_spots_raw = find_ai_blind_spots(task_clusters, role_ctx)
            print(f"  → Got {len(blind_spots_raw)} blind spots")

            record = {
                "archetype_id": archetype_id,
                "seniority": profile["seniority"],
                "domain": profile["domain"],
                "org_shape": profile["org_shape"],
                "role_examples": profile["role_examples"],
                "task_clusters": task_clusters,
                "ai_opportunity_density": ai_density,
                "common_blind_spots": blind_spots_raw,
                "aspiration_patterns": profile["aspiration_patterns"],
                "session_count": 0,
                "use_cases_chosen": [],
            }
            results.append(record)
            print(f"  ✓ {archetype_id} complete")

        except Exception as e:
            print(f"  ✗ {archetype_id} FAILED: {e}")
            # Keep the existing seed data for this archetype if available
            existing = store.get(archetype_id)
            if existing:
                results.append(existing)
                print(f"  → Kept existing seed data for {archetype_id}")

    # Write all results to seed.json
    output_path = Path(__file__).parent / "archetypes" / "seed.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Seed data written to {output_path}")
    print(f"   {len(results)} archetypes generated")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set")
        sys.exit(1)
    generate_seed_data()
