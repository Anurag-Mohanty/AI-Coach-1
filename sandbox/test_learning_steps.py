
import asyncio
from agents.recommendation_agent.learning_path.learning_steps_agent import generate_learning_steps

async def test_learning_steps():
    print("Testing learning steps generation...")
    
    test_context = {
        "content": {
            "curated_training": [
                {
                    "title": "Strategic Prompting for Business Impact",
                    "link": "https://youtube.com/prompt",
                    "duration": "12 min",
                    "source": "YouTube",
                    "description": "Learn how to craft effective prompts for business use cases",
                    "format": "Video"
                },
                {
                    "title": "Build a ChatGPT Dashboard with Streamlit",
                    "link": "https://youtube.com/streamlit", 
                    "duration": "25 min",
                    "source": "YouTube",
                    "description": "Step-by-step guide to creating interactive AI dashboards",
                    "format": "Tutorial"
                },
                {
                    "title": "AI Output Visualization Best Practices",
                    "link": "https://medium.com/ai-viz",
                    "duration": "15 min",
                    "source": "Medium",
                    "description": "Learn how to present AI insights effectively",
                    "format": "Article"
                }
            ],
            "query_plan": [
                "How to frame GPT prompts for dashboard tasks",
                "Using GPT output to build Streamlit dashboards",
                "Best practices for visualizing AI insights"
            ],
            "reflection_summary": "Focus on practical implementation and stakeholder communication"
        },
        "subtask": {
            "title": "Design stakeholder-facing dashboards powered by GPT",
            "description": "Structure GPT outputs and embed them in dashboards for maximum impact",
            "id": "gpt_dashboard_design"
        },
        "use_case": {
            "title": "Build GPT-powered decision dashboards",
            "cluster": "AI Visualization"
        },
        "missing_skills": ["prompt engineering", "data visualization", "stakeholder management"],
        "tool_familiarity": ["Python", "GPT-4"],
        "persona": {
            "role": "Senior Product Manager",
            "domain": "Healthcare",
            "seniority": "Senior"
        },
        "user_id": "test_user",
        "session_id": "test_session",
        "subtask_id": "test_subtask"
    }

    try:
        print("\nCalling generate_learning_steps...")
        result = await generate_learning_steps(test_context, return_structured_output=True)
        print("\nAPI call completed")
        
        print("\nInput context:")
        print("- Subtask:", test_context["subtask"]["title"])
        print("- Use case:", test_context["use_case"]["title"])
        print("- Number of training items:", len(test_context["content"]["curated_training"]))
        
        print("\nGenerated Learning Steps:")
        print(result)
        
        if not result or (isinstance(result, dict) and not result.get("steps")):
            print("\nWarning: No steps were generated")
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(test_learning_steps())
