
from openai import OpenAI
import os
import json
from typing import Dict, Any

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm_model(prompt: str, model_params: Dict[str, Any] = None) -> str:
    """
    Call OpenAI LLM model with given prompt and parameters
    """
    print("\n=== LLM Input ===")
    print("Prompt:", prompt)
    print("Model Params:", json.dumps(model_params, indent=2))
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            **(model_params or {})
        )
        output = response.choices[0].message.content
        print("\n=== LLM Output ===")
        print(output)
        return output
    except Exception as e:
        print(f"Error calling LLM: {str(e)}")
        return ""
