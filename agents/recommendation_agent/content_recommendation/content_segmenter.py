# content_segmenter.py

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import requests
from bs4 import BeautifulSoup
import re
import time
from random import uniform

# --------------------------------------
# 🧠 Extract relevant segment from content
# --------------------------------------
def extract_relevant_segment(item, use_case, skills):
    if item["format"] == "Video" and "YouTube" in item["source"]:
        return extract_from_youtube(item, use_case, skills)
    elif item["format"] == "Code" and "GitHub" in item["source"]:
        return extract_from_github(item, use_case, skills)
    else:
        return None

# --------------------------------------
# 🎬 YouTube Transcript Parsing
# --------------------------------------
def extract_from_youtube(item, use_case, skills):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api.formatters import TextFormatter
        import requests
        import time
        from random import uniform

        # Extract video ID
        video_id = item["link"].split("v=")[-1] if "v=" in item["link"] else item["link"].split("/")[-1]

        # First try without proxy
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            time.sleep(uniform(1.0, 2.0))  # Random delay between requests
        except Exception as e:
            # If direct access fails, try with metadata
            try:
                metadata = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript = metadata.find_transcript(['en']).fetch()
                time.sleep(uniform(1.0, 2.0))
            except:
                # Finally try with description only
                return f"Video description: {item.get('description', 'No description available')}"

        formatter = TextFormatter()
        transcript_text = formatter.format_transcripts(transcript)
        return transcript_text

    except Exception as e:
        print(f"Video extraction error: {e}")
        return None


# --------------------------------------
# 📘 GitHub README or Notebook Parsing
# --------------------------------------
def extract_from_github(item, use_case, skills):
    try:
        url = item["link"]
        response = requests.get(url)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        readme_sections = soup.find_all("article") or soup.find_all("p")
        text = "\n".join([s.get_text() for s in readme_sections])
        matched_lines = [line for line in text.split("\n") if any(k.lower() in line.lower() for k in skills + [use_case])]

        snippet = "\n".join(matched_lines[:5]) if matched_lines else "No relevant section found."
        return snippet
    except Exception as e:
        print("GitHub parse error:", e)
        return None