import requests
from bs4 import BeautifulSoup
import json
import asyncio
from enhanced_app.utils.logging_config import logger

async def get_youtube_search_results(course_name, topic, subtopic, max_results=5):
    query = f"{course_name} {topic} {subtopic}"
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        videos = []

        for script in soup.find_all('script'):
            if 'var ytInitialData =' in script.text:
                start = script.text.find('var ytInitialData =') + len('var ytInitialData =')
                end = script.text.find('};', start) + 1
                json_data = script.text[start:end]

                data = json.loads(json_data)

                contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
                for item in contents:
                    video_items = item.get('itemSectionRenderer', {}).get('contents', [])
                    for video_item in video_items:
                        video = video_item.get('videoRenderer', {})
                        title = video.get('title', {}).get('runs', [{}])[0].get('text', '')
                        video_id = video.get('videoId', '')
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        channel_name = video.get('ownerText', {}).get('runs', [{}])[0].get('text', '')
                        duration = video.get('lengthText', {}).get('simpleText', '')
                        view_count = video.get('viewCountText', {}).get('simpleText', '')

                        if title:
                            videos.append({
                                'title': title,
                                'url': video_url,
                                'channel': channel_name,
                                'duration': duration,
                                'views': view_count,
                            })
                            if len(videos) >= max_results:
                                return videos

        return videos

    except requests.RequestException as e:
        logger.error(f"Error fetching YouTube results for {query}: {str(e)}")
        return []

async def get_enhanced_videos_for_roadmap(roadmap, max_retries=3):
    videos = []
    for topic in roadmap.get('main_topics', []):
        topic_title = topic.get('topic_title', '')
        for subtopic in topic.get('subtopics', []):
            subtopic_title = subtopic.get('subtopic_title', '')
            for attempt in range(max_retries):
                try:
                    search_results = await get_youtube_search_results(roadmap['course_name'], topic_title, subtopic_title, max_results=5)

                    if search_results:
                        for video in search_results:
                            video['topic'] = topic_title
                            video['subtopic'] = subtopic_title
                            videos.append(video)
                        logger.info(f"Added {len(search_results)} videos for {topic_title} - {subtopic_title}")
                        break  # Success, move to next subtopic
                    else:
                        logger.warning(f"No videos found for {topic_title} - {subtopic_title} (Attempt {attempt + 1}/{max_retries})")
                except Exception as e:
                    logger.error(f"Error fetching videos for {topic_title} - {subtopic_title} (Attempt {attempt + 1}/{max_retries}): {str(e)}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

    logger.info(f"Fetched a total of {len(videos)} videos for {roadmap['course_name']}")
    return videos

def safe_log(message):
    try:
        logger.info(message)
    except UnicodeEncodeError:
        logger.info(message.encode('ascii', 'ignore').decode('ascii'))
