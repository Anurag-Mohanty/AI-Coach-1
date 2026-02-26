
"""
Resume Utils
Provides utility functions for extracting fields from resume text
"""
from typing import Dict, Any
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_all_fields(resume_text: str) -> Dict[str, Any]:
    """Extract all relevant fields from resume text using OpenAI"""
    
    prompt = f"""Analyze this resume and extract the following fields:
    - title: Current job title
    - seniority: Seniority level (IC, Lead, Director, VP, etc.) 
    - years_experience: Total years of work experience
    - company_name: Current/most recent company name 
    - company_size: Company size (estimate if not stated)
    - domain: Industry/domain
    - previous_companies: List of previous companies with years
    - team_size: Size of team led/worked with
    - impact_scale: Scale of impact (users, revenue etc)
    - leadership_scope: Leadership responsibilities
    - education: List of degrees with institutions and years
    - education_locations: Countries/regions where education was obtained
    - work_locations: Countries/regions of work experience
    - region: Current region/country
    - languages: Languages mentioned
    - ai_keywords: AI-related terms/tools
    - tools: All technologies/tools mentioned
    - skills: All skills/competencies mentioned
    - certifications: Professional certifications if any
    
    Resume text:
    {resume_text}
    
    Return only a JSON object with these exact keys."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a precise resume field extractor. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        return {
            "error": str(e),
            "title": "unknown",
            "seniority": "unknown", 
            "company_name": "unknown",
            "company_size": "unknown",
            "domain": "unknown",
            "team_size": "unknown",
            "impact_scale": "unknown",
            "leadership_scope": "unknown",
            "ai_keywords": [],
            "tools": []
        }
