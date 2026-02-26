
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.skill_assessment_agent.cultural_alignment_agent.tone_profile_engine import infer_learning_tone_profile

def test_tone_profile():
    print("\n=== Testing Tone Profile Engine ===")

    # Test case 1: Direct profile
    print("\nTest Case 1: Direct Communication Style")
    result = infer_learning_tone_profile(
        ethnicity="North American",
        work_style="Direct",
        collab_pattern="Async",
        tone_preference="Directive"
    )
    print(f"Input: North American, Direct, Async, Directive")
    print(f"Output: {result}")

    # Test case 2: Collaborative style
    print("\nTest Case 2: Collaborative Style")
    result = infer_learning_tone_profile(
        ethnicity="East Asian",
        work_style="Collaborative",
        collab_pattern="Sync",
        tone_preference="Warm"
    )
    print(f"Input: East Asian, Collaborative, Sync, Warm")
    print(f"Output: {result}")

    # Test case 3: Mixed cultural background with educational history
    print("\nTest Case 3: Mixed Cultural Background")
    result = infer_learning_tone_profile(
        ethnicity=None,
        work_style="Exploratory",
        collab_pattern="Mixed",
        tone_preference="Motivational",
        education_list=[
            {"institution": "Stanford University", "location": "USA"},
            {"institution": "IIT Delhi", "location": "India"}
        ],
        work_history=[
            {"company": "Google", "location": "USA"},
            {"company": "Tata", "location": "India"}
        ],
        location="Singapore"
    )
    print(f"Input: Mixed background with USA/India education and work history")
    print(f"Output: {result}")

    # Test case 4: Minimal input test
    print("\nTest Case 4: Minimal Input")
    result = infer_learning_tone_profile(
        ethnicity=None,
        work_style=None,
        collab_pattern=None,
        tone_preference=None,
        location="London"
    )
    print(f"Input: Minimal input with only location")
    print(f"Output: {result}")

if __name__ == "__main__":
    test_tone_profile()
