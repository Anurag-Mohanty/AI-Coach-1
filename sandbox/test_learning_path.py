
import asyncio
from agents.recommendation_agent.learning_path.learning_path_agent import recommend_learning_path

async def run_test(test_case):
    print(f"\nTesting learning path for: {test_case['persona']['role']}")
    # Add default user_id and session_id
    result = await recommend_learning_path(test_case, "test_user", "test_session")
    print("\nGenerated Learning Path:")
    print(result)

async def main():
    print("Starting learning path generation...")

    test_case_1 = {
        "persona": {
            "role": "Senior Product Manager",
            "domain": "Healthcare",
            "impact_scale": "Org-wide"
        },
        "aspiration": {
            "aspiration_category": "switch",
            "target_role_archetype": "AI Product Manager",
            "target_company": "Google"
        },
        "use_case": {
            "title": "Build GPT-powered decision dashboards",
            "cluster": "Internal Tools for Decision-Making"
        },
        "subtask": {
            "title": "Design stakeholder-facing dashboards powered by GPT",
            "description": "Structure GPT outputs and embed them in dashboards using Streamlit or Tableau"
        },
        "skill_delta": {
            "missing_skills": ["prompt engineering", "RAG architecture"],
            "ai_enabler_gaps": ["LLM orchestration", "data grounding"]
        },
        "content": {
            "curated_training": [
                {
                    "title": "Strategic Prompting for Business Impact",
                    "link": "https://youtube.com/prompt",
                    "duration": "12 min",
                    "source": "YouTube"
                },
                {
                    "title": "LangChain 101: Using GPT with Your Own Data",
                    "link": "https://youtube.com/langchain", 
                    "duration": "14 min",
                    "source": "YouTube"
                },
                {
                    "title": "Build a ChatGPT Dashboard with Streamlit",
                    "link": "https://youtube.com/streamlit",
                    "duration": "12 min", 
                    "source": "YouTube"
                },
                {
                    "title": "Prompt Engineering for Tableau",
                    "link": "https://github.com/tableau-prompts",
                    "duration": "Repo",
                    "source": "GitHub"
                },
                {
                    "title": "AI Health Data Visualizations in Tableau",
                    "link": "https://youtube.com/healthdash",
                    "duration": "15 min",
                    "source": "YouTube"
                }
            ],
            "query_plan": [
                "How to frame GPT prompts for dashboard tasks",
                "LangChain + Chroma setup for company data grounding",
                "Using GPT output to build Streamlit dashboards",
                "Generate visual charts from GPT output in Tableau",
                "Domain-specific dashboard case study: healthcare"
            ],
            "reflection_summary": "This subtask is essential for enabling AI-augmented product ownership at scale."
        },
        "user_mode": "explorer"
    }

    test_case_2 = {
        "persona": {
            "role": "Operations Analyst",
            "domain": "Financial Services",
            "missing_skills": ["Process Automation", "Data Pipeline Development"],
            "tool_familiarity": ["Excel", "PowerBI", "Basic Python"],
            "seniority": "Mid-Level"
        },
        "aspiration": {
            "aspiration_category": "Operations Technology Leader",
            "target_role_archetype": "Operations Automation Manager",
            "target_company": "FinTech Company"
        },
        "content": {
            "curated_training": [
                {
                    "title": "Python for Process Automation",
                    "duration": "3 hours",
                    "source": "FinTech Academy",
                    "link": "https://example.com/automation",
                    "type": "Course"
                },
                {
                    "title": "Data Pipeline Architecture",
                    "duration": "2 hours",
                    "source": "Data Engineering Fundamentals",
                    "link": "https://example.com/pipelines",
                    "type": "Workshop"
                }
            ]
        }
    }

    await run_test(test_case_1)
    await run_test(test_case_2)

if __name__ == "__main__":
    asyncio.run(main())
