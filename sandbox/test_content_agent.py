
import asyncio
from agents.recommendation.content_recommendation.content_recommender_agent import recommend_learning_content

mock_input = {
    "focused_subtask": "Summarize healthcare claims data using AI for Monthly Business Review",
    "use_case": "How to use AI for Monthly Business Review in healthcare claims",
    "tool_familiarity": ["Power BI", "GPT-4", "LangChain"],
    "missing_skills": ["Prompt engineering", "chart automation"],
    "domain": "healthcare",
    "persona": "Product Manager",
    "seniority": "Senior"
}

async def main():
    results = await recommend_learning_content(mock_input)
    for res in results:
        print(f"{res['type'].upper()} → {res['title']}\n{res['link']}\nReason: {res.get('why', 'No reason provided')}\n")

if __name__ == "__main__":
    asyncio.run(main())
