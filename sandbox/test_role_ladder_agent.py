"""
🧪 Role Ladder Agent — Test Harness
Location: test/test_role_ladder_agent.py

Purpose:
--------
This test suite simulates multiple user profiles and ensures the Role Ladder Agent:
- Pulls the correct prompt template
- Merges context appropriately
- Produces valid structured output
- Logs the prompt and response for verification
"""

import asyncio
import json
from agents.gap_analysis_agent.role_ladder_agent.role_ladder_agent import infer_ladder_position
from agent_core.global_agent_memory import _memory_store as memory_store

# Define mock test cases
TEST_CASES = [{
    "user_id": "test_ic3",
    "session_id": "session_ic3",
    "context": {
        "current_title": "Associate Product Manager",
        "company_type": "startup",
        "years_experience": 2,
        "target_role_archetype": "Product Manager",
        "org_type": "tech",
        "team_size": 3,
        "persona_tone": "direct"
    }
}, {
    "user_id": "test_ic4",
    "session_id": "session_ic4",
    "context": {
        "current_title": "Product Manager",
        "company_type": "mid-market",
        "years_experience": 5,
        "target_role_archetype": "Senior PM",
        "org_type": "enterprise",
        "team_size": 6,
        "persona_tone": "confident"
    }
}, {
    "user_id": "test_manager",
    "session_id": "session_mgr",
    "context": {
        "current_title": "Senior Product Manager",
        "company_type": "enterprise",
        "years_experience": 8,
        "target_role_archetype": "Product Lead",
        "org_type": "enterprise",
        "team_size": 12,
        "persona_tone": "assertive"
    }
}, {
    "user_id": "test_switcher",
    "session_id": "session_switch",
    "context": {
        "current_title": "Design Lead",
        "company_type": "consultancy",
        "years_experience": 10,
        "target_role_archetype": "Head of Product",
        "org_type": "tech",
        "team_size": 4,
        "persona_tone": "strategic"
    }
}]


async def test_all_role_ladders():
    for case in TEST_CASES:
        print(f"\n--- Running Test for: {case['user_id']} ---\n")
        # Initialize with full context
        # Initialize with complete context structure
        memory_store[(case["user_id"], case["session_id"])] = case["context"]
        print("\n=== Testing Prompt Builder Directly ===")
        from agent_core.prompt_builder import build_prompt_from_context
        test_prompt = build_prompt_from_context(
            task="ladder_inference",
            agent_role="You are a senior career strategist with expertise in org-level leveling",
            task_instruction="Infer normalized ladder position",
            user_context=case["context"],
            memory_context=case["context"],
            considerations=["Avoid inflated titles", "Use company context"]
        )
        print("Direct Prompt Builder Output:", json.dumps(test_prompt, indent=2))
        
        result = await infer_ladder_position(case["user_id"],
                                             case["session_id"])
        print("\n--- Final Output ---\n")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(test_all_role_ladders())
