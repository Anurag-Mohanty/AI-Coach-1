
from agents.recommendation_agent.content_recommendation.query_planner_agent import generate_search_queries

def test_query_generation():
    test_cases = [
        {
            "name": "Dashboard Summarization",
            "subtask": "Use GPT to summarize Tableau dashboards into exec-ready insights",
            "context": {
                "domain": "healthcare",
                "tool_familiarity": ["GPT-4", "Tableau", "SQL"],
                "missing_skills": ["prompt engineering", "data storytelling"],
                "seniority": "Senior PM"
            }
        },
        {
            "name": "Anomaly Detection",
            "subtask": "Use AI to detect anomalies in medical claim records",
            "context": {
                "domain": "healthcare",
                "tool_familiarity": ["Python", "SQL", "Tableau"],
                "missing_skills": ["anomaly detection", "ML modeling"],
                "seniority": "Data Analyst"
            }
        },
        {
            "name": "Cold Outreach",
            "subtask": "Generate cold outreach email copy using customer attributes",
            "context": {
                "domain": "sales",
                "tool_familiarity": ["GPT-4", "CRM", "Excel"],
                "missing_skills": ["prompt engineering", "email automation"],
                "seniority": "Sales Ops"
            }
        },
        {
            "name": "Onboarding Plans",
            "subtask": "Use GPT to generate personalized onboarding plans",
            "context": {
                "domain": "product",
                "tool_familiarity": ["GPT-4", "Notion", "Jira"],
                "missing_skills": ["workflow automation", "LLM integration"],
                "seniority": "Product Manager"
            }
        },
        {
            "name": "Customer Feedback",
            "subtask": "Analyze customer feedback and auto-tag themes with GPT",
            "context": {
                "domain": "product",
                "tool_familiarity": ["Python", "GPT-4", "SQL"],
                "missing_skills": ["sentiment analysis", "data clustering"],
                "seniority": "Product Analyst"
            }
        },
        {
            "name": "Support Tickets",
            "subtask": "Summarize support tickets for weekly leadership review",
            "context": {
                "domain": "customer support",
                "tool_familiarity": ["Zendesk", "GPT-4", "Excel"],
                "missing_skills": ["automation", "data visualization"],
                "seniority": "Support Lead"
            }
        }
    ]

    print("\n🔍 Running Query Planner Tests\n")
    
    for case in test_cases:
        print(f"\n=== Test Case: {case['name']} ===")
        print(f"Subtask: {case['subtask']}")
        print(f"Context: {case['context']}\n")
        
        queries = generate_search_queries(case['subtask'], case['context'], n=3, print_debug=True)
        print(f"\nGenerated {len(queries)} queries:")
        for i, q in enumerate(queries, 1):
            print(f"{i}. {q}")
        print("\n" + "="*50)

if __name__ == "__main__":
    test_query_generation()
