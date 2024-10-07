import asyncio
import json
from enhanced_app.services.enhanced_roadmap_service import create_enhanced_roadmap
from enhanced_app.services.excel_service import read_excel_data
from enhanced_app.services.enhanced_youtube_service import get_enhanced_videos_for_roadmap, safe_log
from enhanced_app.services.db_service import create_indexes, upsert_course, insert_video_content, link_video_to_section, get_course_with_videos
from enhanced_app.utils.logging_config import logger
from datetime import datetime
from enhanced_app.services.category_service import get_all_categories, get_core_categories

async def process_course(category, course_data):
    course_name = course_data['course_name']
    examples = course_data['examples']
    
    logger.info(f"Generating roadmap for {course_name} in {category}")
    roadmap = await create_enhanced_roadmap(course_name, category, examples)
    if not roadmap:
        logger.error(f"Failed to generate roadmap for {course_name}")
        return None

    logger.info(f"Roadmap generated successfully for {course_name}. Fetching related videos...")

    try:
        videos = await get_enhanced_videos_for_roadmap(roadmap)
    except Exception as e:
        logger.error(f"Error fetching videos for {course_name}: {e}")
        videos = []

    logger.info(f"Fetched {len(videos)} videos for {course_name}")

    course_data = {
        "title": roadmap['course_name'],
        "description": roadmap['description'],
        "category": category,
        "tags": roadmap['tags'],
        "topics": roadmap['topics'],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "status": "published"
    }

    course_id = upsert_course(course_data)

    subtopics_without_videos = []

    for topic in roadmap['topics']:
        for section in topic['sections']:
            topic_name = section['topic']
            for subtopic in section['subtopics']:
                subtopic_videos = [v for v in videos if v['topic'] == topic_name and v['subtopic'] == subtopic]
                
                if not subtopic_videos:
                    logger.warning(f"No videos found for {topic_name} - {subtopic}")
                    subtopics_without_videos.append(f"{topic_name} - {subtopic}")
                    # Add a placeholder video
                    placeholder_video = {
                        "title": f"Placeholder for {subtopic}",
                        "url": "https://www.youtube.com/watch?v=placeholder",
                        "duration": "N/A",
                        "views": "N/A",
                        "channel": "Placeholder",
                        "topic": topic_name,
                        "subtopic": subtopic
                    }
                    subtopic_videos.append(placeholder_video)
                
                for video in subtopic_videos:
                    video_data = {
                        "course_id": course_id,
                        "type": "video",
                        "title": video['title'],
                        "metadata": {
                            "duration": video.get('duration', 'N/A'),
                            "file_url": video['url'],
                            "views": video.get('views', 'N/A'),
                            "channel": video.get('channel', 'N/A')
                        },
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    video_id = insert_video_content(video_data)
                    link_video_to_section(course_id, topic_name, subtopic, video_id)
                    safe_log(f"Inserted video: {video['title']} for {topic_name} - {subtopic}")

    if subtopics_without_videos:
        logger.warning("The following subtopics have placeholder videos and may need manual review:")
        for subtopic in subtopics_without_videos:
            logger.warning(f"- {subtopic}")

    return course_id

async def main():
    excel_file_path = r'C:\Users\parag\Desktop\learnVault\Worksheet.xlsx'
    
    try:
        excel_data = read_excel_data(excel_file_path)
        if not excel_data:
            logger.error("Failed to read Excel data")
            return
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return

    # Database operations
    create_indexes()

    # Process only the first course
    first_category = next(iter(excel_data))
    first_course = excel_data[first_category][0]
    
    logger.info(f"Processing category: {first_category}")
    course_id = await process_course(first_category, first_course)
    
    if course_id:
        full_course = get_course_with_videos(course_id)
        print(f"\nCourse structure for {full_course['title']}:")
        print(json.dumps(full_course, indent=2, default=str))

        # Save the complete roadmap with videos to a JSON file
        filename = f"{full_course['title'].replace(' ', '_')}_roadmap.json"
        with open(filename, 'w') as f:
            json.dump(full_course, f, indent=2, default=str)
        print(f"\nComplete roadmap for {full_course['title']} saved to '{filename}'")

    print("\nFirst course processed and stored in MongoDB.")

# Add these functions or integrate them into your existing CLI structure
def list_categories():
    categories = get_all_categories()
    for category in categories:
        print(f"{category['name']}: {category['description']}")

def list_core_categories():
    categories = get_core_categories()
    for category in categories:
        print(f"{category['name']}: {category['description']}")

# Update your main CLI loop or command handling to include these new functions
# For example:
# if command == "list_categories":
#     list_categories()
# elif command == "list_core_categories":
#     list_core_categories()

if __name__ == "__main__":
    asyncio.run(main())
