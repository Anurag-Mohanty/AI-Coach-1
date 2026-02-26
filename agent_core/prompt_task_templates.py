"""
📚 Prompt Task Template Library
Location: agent_core/prompt_task_templates.py

Purpose:
--------
A centralized library of task-specific prompt scaffolds. These define what each task expects in terms of:
- Required and optional input fields
- Agent role description
- Task instructions
- Output formatting
- Special considerations or nudges

These templates drive consistency across the Prompt Builder and allow agents to invoke prompts declaratively by task name.
"""

TASK_TEMPLATES = {
    "domain_jump_analysis": {
        "required_fields": [
            "current_domain", 
            "target_domain", 
            "project_keywords", 
            "tools_used", 
            "skills_from_resume", 
            "skills_from_linkedin", 
            "skills_by_use_case"
        ],
        "optional_fields": ["persona_context", "impact_scale", "use_cases_by_domain"],
        "task_instruction": """Evaluate how transferable a user’s skills, mindsets, and experience are from their current domain to a new target domain.

    Your role is not to make a go/no-go judgment, but to equip downstream agents with:
    - Reusable strengths that can be reframed
    - Specific gaps that require attention
    - Strategic narrative insight about the transition
    - Any shifts in thinking that the user will need

    Use analogical reasoning: look for shared functional patterns even if terminology differs. Avoid scoring or vagueness. Focus on actionable distinctions in tools, workflows, and cultural framing.""",
        "agent_role": "You are a cross-domain diagnostic agent in a modular AI coaching platform. You analyze the user's professional background, map reusable strengths across domains, and flag specific gaps and mindset shifts needed to succeed in the new context.",
        "output_format": """{
        "transferable_skills": ["skill_1", "skill_2"],
        "domain_specific_gaps": ["gap_1", "gap_2"],
        "bridge_insight_summary": "Strategic narrative connecting current domain experience to target domain expectations",
        "suggested_mindset_shifts": ["shift_1", "shift_2"]
    }""",
        "considerations": [
            "Draw from resume and known use cases to assess real overlap",
            "Focus on tools, mental models, and stakeholder expectations — not just titles",
            "Use fallback defaults if data is partial, but clearly flag limited confidence",
            "Suggested mindset shifts should feel real — not generic business platitudes",
            "The summary should help a Learning Path Agent or Skill Delta Agent pick up cleanly from here"
        ],
        "examples": [
            {
                "input": {
                    "current_domain": "healthcare",
                    "target_domain": "adtech",
                    "project_keywords": ["compliance systems", "analytics dashboard"],
                    "tools_used": ["Tableau", "PostgreSQL"],
                    "skills_from_resume": ["A/B testing", "privacy-sensitive design", "SQL"],
                    "skills_by_use_case": {
                        "adtech": ["real-time bidding", "audience segmentation", "campaign optimization"]
                    }
                },
                "output": {
                    "transferable_skills": ["A/B testing", "SQL"],
                    "domain_specific_gaps": ["real-time bidding", "ad auction optimization"],
                    "bridge_insight_summary": "Your experience in privacy-sensitive analytics in healthcare maps well to adtech's performance experimentation culture. However, you’ll need to understand how real-time auctions work and shift your mindset from compliance-centric design to growth-driven iteration.",
                    "suggested_mindset_shifts": ["From safety-first to growth-first framing", "From scheduled releases to always-on optimization"]
                }
            }
        ]
    },
    "ladder_inference": {
        "required_fields": ["current_title", "company_type", "years_experience", "target_role_archetype"],
        "optional_fields": ["org_type", "team_size", "persona_tone", "resume_highlights"],
        "task_instruction": """You are analyzing a professional's role to determine their true normalized level on the IC/Management ladder.

Key Analysis Points:
1. Look beyond the title - analyze scope, impact, and team context
2. Consider company type's influence on titles (startups inflate, enterprises standardize)
3. Use team size and cross-functional leadership as key signals
4. Years of experience should validate but not determine level
5. Provide detailed reasoning for the level assessment

Map to standard levels:
- IC1: Junior/Associate 
- IC2: Mid-level
- IC3: Senior (smaller scope)
- IC4: Senior/Staff (larger scope/strategic)
- IC5: Principal/Distinguished
- M1: First-level manager (managing ICs)
- M2: Senior manager (managing managers)
- M3: Director+ (org leadership)""",
        "agent_role": "You are an expert in organizational design and career leveling who helps normalize job levels across different company types and industries. You have extensive experience in both startup and enterprise environments.",
        "output_format": """{
    "inferred_ladder_level": "Current normalized level (IC1-IC5 or M1-M3)",
    "next_logical_level": "Next realistic career step with specific title examples",
    "progression_velocity": "Slow/Moderate/Fast with reasoning",
    "ladder_alignment_flag": "Title/Experience/Scope with specific misalignments noted",
    "normalization_explanation": "Detailed analysis of why this level, addressing title inflation/deflation",
    "management_signal": "Clear IC vs Management trajectory with specific evidence"
}""",
        "considerations": [
            "Startup titles often inflate by 1-2 levels - normalize based on scope/impact",
            "Enterprise titles are more standardized but vary by org size", 
            "Team size >10 suggests leadership but isn't automatic management track",
            "Years of experience validate but don't determine level",
            "Look for strategic scope and org-wide impact for IC4+",
            "Years of experience should align with level",
            "Consider company stage/size in normalization"
        ],
        "examples": [
            {
                "input": {
                    "current_title": "Senior Product Manager",
                    "company_type": "enterprise",
                    "years_experience": 8,
                    "team_size": 12,
                    "target_role_archetype": "Product Lead"
                },
                "output": {
                    "inferred_ladder_level": "IC4",
                    "next_logical_level": "M1 (Group Product Manager or Lead PM managing PMs)",
                    "progression_velocity": "Moderate",
                    "ladder_alignment_flag": "Scope-based",
                    "normalization_explanation": "Despite 'Senior PM' title, leading team of 12 in enterprise suggests ownership over substantial area. However, without clear PM reports, this aligns with high-scope IC4.",
                    "management_signal": "Strong management track signal - team size implies cross-functional leadership"
                }
            },
            {
                "input": {
                    "current_title": "Product Manager",
                    "company_type": "startup",
                    "years_experience": 3,
                    "team_size": 4,
                    "target_role_archetype": "Senior PM"
                },
                "output": {
                    "inferred_ladder_level": "IC2",
                    "next_logical_level": "IC3 (Senior Product Manager)",
                    "progression_velocity": "Fast",
                    "ladder_alignment_flag": "Title-Experience",
                    "normalization_explanation": "Early startup PM title normalized to IC2 based on years of experience and team size. Startup context often inflates titles.",
                    "management_signal": "IC track currently - build depth before considering management"
                }
            }
        ]
    },
    "role_detail_analysis": {
        "required_fields": ["role"],
        "optional_fields": ["resume", "linkedin", "role_context", "aspiration"],
        "task_instruction": "Analyze the user's work structure and identify key task clusters, skill requirements, and AI automation opportunities. Focus on actionable insights that can guide skill development.",
        "agent_role": "You are an expert productivity analyst specializing in modern work patterns and AI transformation opportunities.",
        "output_format": """{
            "task_clusters": [
                {
                    "name": "Cluster name",
                    "activities": ["Activity 1", "Activity 2"],
                    "tools_used": ["Tool 1", "Tool 2"]
                }
            ],
            "effort_distribution": {
                "cluster_name": "percentage as integer"
            },
            "frequency_map": {
                "cluster_name": "daily|weekly|monthly|quarterly"
            },
            "ai_opportunity_density": {
                "cluster_name": {
                    "score": "1-10 integer",
                    "rationale": "Brief explanation"
                }
            },
            "skills_detected": {
                "technical": ["skill1", "skill2"],
                "domain": ["skill1", "skill2"],
                "soft": ["skill1", "skill2"]
            }
        }""",
        "considerations": [
            "Group related tasks into 4-6 meaningful clusters",
            "Consider both current tasks and aspirational direction",
            "Be specific about tools and technologies used",
            "Focus on patterns that reveal skill gaps",
            "Identify areas where AI could augment vs replace",
            "Ground analysis in resume/context when available"
        ],
        "examples": [
            {
                "input": {
                    "role": "Product Manager",
                    "resume": "3 years experience in SaaS products...",
                    "aspiration": "Move into AI product leadership"
                },
                "output": {
                    "task_clusters": [
                        {
                            "name": "Product Strategy",
                            "activities": ["Roadmap planning", "Market research"],
                            "tools_used": ["Aha!", "Amplitude"]
                        }
                    ],
                    "effort_distribution": {
                        "Product Strategy": 30
                    },
                    "frequency_map": {
                        "Product Strategy": "weekly"
                    },
                    "ai_opportunity_density": {
                        "Product Strategy": {
                            "score": 8,
                            "rationale": "AI can enhance market analysis and feature prioritization"
                        }
                    },
                    "skills_detected": {
                        "technical": ["SQL", "Analytics"],
                        "domain": ["SaaS", "B2B"],
                        "soft": ["Strategic thinking", "Stakeholder management"]
                    }
                }
            }
        ]
    },
    "role_context_analysis": {
        "required_fields": ["title", "company", "domain"],
        "optional_fields": ["company_size", "team_size", "cross_functional_density", "task_clusters", "effort_distribution"],
        "task_instruction": "Analyze the user role and org setup to infer cross-functional scope, ops-strategy bias, and structure.",
        "agent_role": "You are an expert in organizational role profiling.",
        "output_format": """
        JSON with:
        - contextualized_role_type
        - org_shape_inference
        - cross_functional_density
        - ops_or_strategy_bias
        - ai_applicability_constraints
        - role_archetype_tag
        - confidence_score
        - reasoning_log
        """,
        "considerations": [
            "Avoid assumptions if fields are missing",
            "Ground in company size + team setup"
        ]
    },
    "tool_familiarity_mapping": {
        "required_fields": ["title", "domain", "tech_comfort"],
        "optional_fields": ["tools_used", "task_clusters"],
        "task_instruction": "Infer a user's familiarity with modern tools and group them by work function.",
        "agent_role": "You are an AI Workflow Tool Analyst.",
        "output_format": """
        JSON with:
        - tools_by_function
        - ai_tools_detected
        - initial_tool_depth_estimate
        """,
        "considerations": [
            "Use defaults for task clusters if missing",
            "Group tools based on logical function buckets"
        ]
    },
    "aspiration_analysis": {
        "required_fields": ["resume_data", "linkedin_data", "role_detail", "role_context"],
        "optional_fields": [],
        "task_instruction": "Suggest 3–5 realistic growth trajectories for the user over the next 2–3 years.",
        "agent_role": "You are a career counselor helping define user growth options.",
        "output_format": """
        JSON with:
        - target_role_archetype
        - aspiration_category
        - role_delta_summary
        - domain_shift_signal
        - risk_of_misalignment
        - aspiration_cluster
        - realism_score
        - reflective_prompt
        - realistic_trajectory_options
        """,
        "considerations": [
            "Favor grounded suggestions over aspirational leaps",
            "Call out missing leadership signals or AI readiness"
        ]
    }
}

def get_task_template(task_name):
    return TASK_TEMPLATES.get(task_name)