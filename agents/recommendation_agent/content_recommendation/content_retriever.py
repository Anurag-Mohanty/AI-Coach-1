
# content_retriever.py (v3 - Full Context-Aware Search)

import os
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from github import Github
from openai import OpenAI

GITHUB_TOKEN = None
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------------------------
# 🎯 STEP 1: Generate smart LLM-based search queries using full context
# ------------------------------------------------
def generate_search_queries_v2(inputs):
    prompt = f"""
You are an expert AI search strategist.
Your job is to generate 5 highly specific, high-signal search queries for finding instructional public content (YouTube, GitHub, blogs) to help a product manager upskill.

Here is the user's full context:
- Use Case: {inputs['use_case']}
- Tools: {', '.join(inputs.get('recommended_tools', []))}
- Missing Skills: {', '.join(inputs.get('missing_skills', []))}
- Domain: {inputs.get('domain', 'general')}
- Persona: {inputs.get('persona', 'professional')}

Only output smart, intent-rich, query strings that would return **instructional** content relevant to this user.
Avoid fluff.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=300
        )
        raw_text = response.choices[0].message.content
        queries = [line.strip("-• ") for line in raw_text.strip().split("\n") if line.strip()]
        return queries[:5]
    except Exception as e:
        print("LLM query gen error:", e)
        return [inputs['use_case']]

# ------------------------------------------------
# 🔍 STEP 2: Retrieve content using those queries
# ------------------------------------------------
def retrieve_content(inputs, max_results=10):
    smart_queries = generate_search_queries_v2(inputs)
    youtube_results = []
    github_results = []

    for q in smart_queries:
        youtube_results.extend(search_youtube(q, max_results=2))
        github_results.extend(search_github(q, max_results=2))

    return youtube_results + github_results

# ----------------------------------------
# 🔎 YouTube and GitHub search logic
# ----------------------------------------
def search_youtube(query, max_results=5):
    if not YOUTUBE_API_KEY:
        print("Warning: YOUTUBE_API_KEY not found in environment variables")
        return []
        
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    try:
        search_response = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=max_results,
            type='video'
        ).execute()

        results = []
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            snippet = item['snippet']
            
            results.append({
                "title": snippet['title'],
                "link": f"https://www.youtube.com/watch?v={video_id}",
                "format": "Video",
                "channel": snippet['channelTitle'],
                "source": "YouTube",
                "description": snippet['description'],
                "id": video_id,
            })
        return results
    except Exception as e:
        print(f"YouTube API error: {e}")
        return []

def search_github(query, max_results=5):
    g = Github(GITHUB_TOKEN) if GITHUB_TOKEN else Github()
    try:
        code_results = g.search_repositories(query=query, sort="stars")
        results = []
        for repo in code_results[:max_results]:
            results.append({
                "title": repo.name,
                "link": repo.html_url,
                "format": "Code", 
                "source": "GitHub",
                "description": repo.description,
                "owner": repo.owner.login,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "id": repo.id
            })
        return results
    except Exception as e:
        print("GitHub search failed:", e)
        return []
