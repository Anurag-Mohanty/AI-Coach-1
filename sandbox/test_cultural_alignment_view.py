
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.skill_assessment_agent.cultural_alignment_agent.cultural_alignment_agent import run_cultural_alignment_agent

def test_cultural_alignment():
    print("\n=== Testing Cultural Alignment View ===")

    # Test case 1: East Asian tech professional
    print("\nTest Case 1: East Asian Tech Background")
    context = {
        "ethnicity": "East Asian",
        "work_style": "Collaborative",
        "collab_pattern": "Sync",
        "tone_preference": "Warm",
        "education_list": [
            {"institution": "Stanford University", "location": "California, USA"},
            {"institution": "Tsinghua University", "location": "Beijing, China"}
        ],
        "work_history": [
            {"company": "Microsoft", "location": "Seattle, USA"},
            {"company": "Alibaba", "location": "Hangzhou, China"}
        ],
        "location": "Singapore",
        "collaboration_score": "75"
    }
    
    result = run_cultural_alignment_agent("test_user", "test_session", context)
    print(f"Output: {result}")

    # Test case 2: Western professional
    print("\nTest Case 2: Western Background")
    context = {
        "ethnicity": "North American",
        "work_style": "Direct",
        "collab_pattern": "Async",
        "tone_preference": "Directive",
        "education_list": [
            {"institution": "MIT", "location": "Massachusetts, USA"},
            {"institution": "Berkeley", "location": "California, USA"}
        ],
        "work_history": [
            {"company": "Google", "location": "Mountain View, USA"},
            {"company": "Amazon", "location": "Seattle, USA"}
        ],
        "location": "New York, USA"
    }
    
    result = run_cultural_alignment_agent("test_user", "test_session", context)
    print(f"Output: {result}")

if __name__ == "__main__":
    test_cultural_alignment()
