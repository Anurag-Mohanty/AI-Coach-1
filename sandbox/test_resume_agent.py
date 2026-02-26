
import sys
import os
sys.path.append('/home/runner/workspace')

from tools.resume.resume_agent import analyze_resume

def test_resume_agent():
    # Test with sample resume text
    sample_resume = """
    John Doe
    Senior Product Manager
    
    Experience:
    - Led cross-functional teams of 8+ people at Google
    - Built ML-powered recommendation systems
    - Used Python, SQL, Tableau for data analysis
    - 5 years experience in healthcare technology
    
    Skills: Product Management, Machine Learning, Python, SQL, Tableau
    """
    
    try:
        result = analyze_resume(
            user_id="test_user",
            session_id="test_session", 
            resume_text=sample_resume
        )
        print("✅ Resume analysis successful!")
        print("Result:", result)
        return True
    except Exception as e:
        print("❌ Resume analysis failed:", str(e))
        return False

if __name__ == "__main__":
    test_resume_agent()
