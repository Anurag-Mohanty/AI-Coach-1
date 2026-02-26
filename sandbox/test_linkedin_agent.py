
#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.linkedin.linkedin_agent import analyze_linkedin_profile

def test_linkedin_agent():
    # Sample LinkedIn profile text
    sample_profile = """
    John Doe - Senior Data Scientist at TechCorp
    
    About: Passionate about machine learning and AI. Currently working on NLP projects 
    and deep learning applications. Love sharing insights about the future of AI.
    
    Recent Activity:
    - Shared article about GPT-4 and its implications
    - Commented on Andrew Ng's post about AI education
    - Posted about attending NeurIPS conference
    
    Follows: Andrew Ng, Yann LeCun, Andrej Karpathy
    
    Skills: Python, TensorFlow, PyTorch, Machine Learning, Deep Learning
    """
    
    try:
        result = analyze_linkedin_profile(
            user_id="test_user_123",
            session_id="test_session_456", 
            profile_text=sample_profile
        )
        
        print("✅ LinkedIn analysis successful!")
        print(f"Result: {result}")
        
        # Basic validation
        assert "ai_interests" in result
        assert "activity_level" in result
        assert "confidence" in result
        assert isinstance(result["confidence"], (int, float))
        
        print("✅ All basic validations passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    test_linkedin_agent()
