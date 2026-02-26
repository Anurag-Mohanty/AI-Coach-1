
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.skill_assessment_agent.cultural_alignment_agent.cultural_utils import infer_cultural_context_llm

def test_cultural_utils():
    # Test case 1: Education and work in North America
    print("\n=== Test Case 1: North American Background ===")
    education_list = [
        {"institution": "Stanford University", "location": "California, USA"},
        {"institution": "MIT", "location": "Massachusetts, USA"}
    ]
    work_history = [
        {"company": "Google", "location": "Mountain View, USA"},
        {"company": "Microsoft", "location": "Seattle, USA"}
    ]
    location = "San Francisco, USA"
    
    print("Input Data:")
    print(f"Education: {education_list}")
    print(f"Work History: {work_history}")
    print(f"Current Location: {location}")
    
    result = infer_cultural_context_llm(education_list, work_history, location)
    print(f"LLM Output: {result}")

    # Test case 2: Education and work in South Asia
    print("\n=== Test Case 2: South Asian Background ===")
    education_list = [
        {"institution": "IIT Delhi", "location": "New Delhi, India"},
        {"institution": "BITS Pilani", "location": "Rajasthan, India"}
    ]
    work_history = [
        {"company": "Infosys", "location": "Bangalore, India"},
        {"company": "TCS", "location": "Mumbai, India"}
    ]
    location = "Bangalore, India"
    
    print("Input Data:")
    print(f"Education: {education_list}")
    print(f"Work History: {work_history}")
    print(f"Current Location: {location}")
    
    result = infer_cultural_context_llm(education_list, work_history, location)
    print(f"LLM Output: {result}")

    # Test case 3: Mixed international background
    print("\n=== Test Case 3: Mixed International Background ===")
    education_list = [
        {"institution": "University of Tokyo", "location": "Tokyo, Japan"},
        {"institution": "ETH Zurich", "location": "Zurich, Switzerland"}
    ]
    work_history = [
        {"company": "Samsung", "location": "Seoul, South Korea"},
        {"company": "Deutsche Bank", "location": "Frankfurt, Germany"}
    ]
    location = "Singapore"
    
    print("Input Data:")
    print(f"Education: {education_list}")
    print(f"Work History: {work_history}")
    print(f"Current Location: {location}")
    
    result = infer_cultural_context_llm(education_list, work_history, location)
    print(f"LLM Output: {result}")

    # Test case 4: Latin American background
    print("\n=== Test Case 4: Latin American Background ===")
    education_list = [
        {"institution": "Universidad de São Paulo", "location": "São Paulo, Brazil"},
        {"institution": "Tecnológico de Monterrey", "location": "Mexico City, Mexico"}
    ]
    work_history = [
        {"company": "Mercado Libre", "location": "Buenos Aires, Argentina"},
        {"company": "Globant", "location": "Bogotá, Colombia"}
    ]
    location = "Santiago, Chile"
    
    print("Input Data:")
    print(f"Education: {education_list}")
    print(f"Work History: {work_history}")
    print(f"Current Location: {location}")
    
    result = infer_cultural_context_llm(education_list, work_history, location)
    print(f"LLM Output: {result}")

    # Test case 5: Middle Eastern background
    print("\n=== Test Case 5: Middle Eastern Background ===")
    education_list = [
        {"institution": "American University of Beirut", "location": "Beirut, Lebanon"},
        {"institution": "King Saud University", "location": "Riyadh, Saudi Arabia"}
    ]
    work_history = [
        {"company": "Emirates NBD", "location": "Dubai, UAE"},
        {"company": "Qatar Airways", "location": "Doha, Qatar"}
    ]
    location = "Dubai, UAE"
    
    print("Input Data:")
    print(f"Education: {education_list}")
    print(f"Work History: {work_history}")
    print(f"Current Location: {location}")
    
    result = infer_cultural_context_llm(education_list, work_history, location)
    print(f"LLM Output: {result}")

    # Test case 6: African background
    print("\n=== Test Case 6: African Background ===")
    education_list = [
        {"institution": "University of Cape Town", "location": "Cape Town, South Africa"},
        {"institution": "University of Nairobi", "location": "Nairobi, Kenya"}
    ]
    work_history = [
        {"company": "Safaricom", "location": "Nairobi, Kenya"},
        {"company": "MTN Group", "location": "Johannesburg, South Africa"}
    ]
    location = "Lagos, Nigeria"
    
    print("Input Data:")
    print(f"Education: {education_list}")
    print(f"Work History: {work_history}")
    print(f"Current Location: {location}")
    
    result = infer_cultural_context_llm(education_list, work_history, location)
    print(f"LLM Output: {result}")

    # Test case 7: Central European background
    print("\n=== Test Case 7: Central European Background ===")
    education_list = [
        {"institution": "Charles University", "location": "Prague, Czech Republic"},
        {"institution": "Vienna University of Technology", "location": "Vienna, Austria"}
    ]
    work_history = [
        {"company": "Skoda Auto", "location": "Mladá Boleslav, Czech Republic"},
        {"company": "Budapest Bank", "location": "Budapest, Hungary"}
    ]
    location = "Warsaw, Poland"
    
    print("Input Data:")
    print(f"Education: {education_list}")
    print(f"Work History: {work_history}")
    print(f"Current Location: {location}")
    
    result = infer_cultural_context_llm(education_list, work_history, location)
    print(f"LLM Output: {result}")

    # Test case 8: Australian/Oceanian background
    print("\n=== Test Case 8: Australian/Oceanian Background ===")
    education_list = [
        {"institution": "University of Western Australia", "location": "Perth, Australia"},
        {"institution": "University of Queensland", "location": "Brisbane, Australia"}
    ]
    work_history = [
        {"company": "BHP", "location": "Perth, Australia"},
        {"company": "Woodside Energy", "location": "Perth, Australia"}
    ]
    location = "Perth, Australia"
    
    print("Input Data:")
    print(f"Education: {education_list}")
    print(f"Work History: {work_history}")
    print(f"Current Location: {location}")
    
    result = infer_cultural_context_llm(education_list, work_history, location)
    print(f"LLM Output: {result}")

if __name__ == "__main__":
    test_cultural_utils()
