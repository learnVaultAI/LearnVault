import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
import json

def get_youtube_search_results(query, channel=None, max_results=5):
    if channel:
        query = f"{query} {channel}"

    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch YouTube search results. Status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    videos = []

    for script in soup.find_all('script'):
        if 'var ytInitialData =' in script.text:
            try:
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

                        video_headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        }
                        video_response = requests.get(video_url, headers=video_headers)

                        if video_response.status_code == 200:
                            video_soup = BeautifulSoup(video_response.text, 'html.parser')
                            description_tag = video_soup.find('meta', {'name': 'description'})
                            description = description_tag.get('content', '') if description_tag else ""
                        else:
                            description = ""

                        if title:
                            videos.append({
                                'title': title,
                                'url': video_url,
                                'channel_name': channel_name,
                                'duration': duration,
                                'view_count': view_count,
                                'description': description
                            })
                            if len(videos) >= max_results:
                                break
                if len(videos) >= max_results:
                    break
            except (json.JSONDecodeError, IndexError, KeyError) as e:
                print(f"Error parsing JSON data: {e}")
            break

    return videos
