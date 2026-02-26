from typing import List, Dict, Any
import os
from googleapiclient.discovery import build
import asyncio
from youtube_transcript_api import YouTubeTranscriptApi
from agent_core.timing_utils import timed_function

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

@timed_function("YouTube Retrieval", display=True)
async def search_youtube_for_task(query: str, context: Dict[str, Any], max_results: int = 3) -> List[Dict]:
    """
    Asynchronously search YouTube for relevant content
    """
    try:
        # Run YouTube API call in a thread pool since it's blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: youtube.search().list(
                q=query,
                type='video',
                part='id,snippet',
                maxResults=max_results
            ).execute()
        )

        results = []
        for item in response.get('items', []):
            video_id = item['id']['videoId']

            # Get video details including duration
            video_response = await loop.run_in_executor(
                None,
                lambda: youtube.videos().list(
                    part='contentDetails,statistics',
                    id=video_id
                ).execute()
            )

            if video_response['items']:
                video_details = video_response['items'][0]

                # Get transcript if available
                try:
                    transcript = await loop.run_in_executor(
                        None,
                        lambda: YouTubeTranscriptApi.get_transcript(video_id)
                    )
                    transcript_text = ' '.join([entry['text'] for entry in transcript])
                except:
                    transcript_text = ''

                results.append({
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'link': f'https://www.youtube.com/watch?v={video_id}',
                    'thumbnail': item['snippet']['thumbnails']['default']['url'],
                    'duration': video_details['contentDetails']['duration'],
                    'views': video_details['statistics']['viewCount'],
                    'transcript': transcript_text,
                    'source': 'YouTube',
                    'format': 'Video'
                })

        return results

    except Exception as e:
        print(f"YouTube search error: {str(e)}")
        return []