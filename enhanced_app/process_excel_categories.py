import asyncio
import csv
import json
from enhanced_app.services.enhanced_roadmap_service import create_enhanced_roadmap
from enhanced_app.services.excel_service import read_excel_data
from enhanced_app.services.enhanced_youtube_service import get_enhanced_videos_for_roadmap
from enhanced_app.services.db_service import create_indexes, upsert_course, insert_video_content, link_video_to_section
from enhanced_app.utils.logging_config import logger
from datetime import datetime

async def process_course(category, course_data, csv_writer):
    course_name = course_data['course_name']
    examples = course_data['examples']
    
    logger.info(f"Generating roadmap for {course_name} in {category}")
    roadmap = await create_enhanced_roadmap(course_name, category, examples)
    if not roadmap:
        logger.error(f"Failed to generate roadmap for {course_name}")
        csv_writer.writerow([category, 'N/A', course_name, examples, 'Failed'])
        return None

    logger.info(f"Roadmap generated successfully for {course_name}. Roadmap structure: {json.dumps(roadmap, indent=2)}")
    logger.info(f"Fetching related videos...")

    try:
        videos = await get_enhanced_videos_for_roadmap(roadmap)
    except Exception as e:
        logger.error(f"Error fetching videos for {course_name}: {e}")
        videos = []

    logger.info(f"Fetched {len(videos)} videos for {course_name}")

    course_data = {
        "title": roadmap.get('course_name', course_name),
        "description": roadmap.get('description', ''),
        "category": category,
        "tags": roadmap.get('tags', []),
        "topics": roadmap.get('topics', roadmap.get('main_topics', [])),  # Try both 'topics' and 'main_topics'
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "status": "published"
    }

    course_id = upsert_course(course_data)

    all_subtopics_covered = True
    topics = course_data['topics']
    
    if not topics:
        logger.warning(f"No topics found in roadmap for {course_name}")
        csv_writer.writerow([category, 'N/A', course_name, examples, 'No Topics'])
        return course_id

    for topic in topics:
        sections = topic.get('sections', [topic])  # If 'sections' doesn't exist, treat the topic itself as a section
        for section in sections:
            topic_name = section.get('topic', section.get('title', ''))
            subtopics = section.get('subtopics', [{'title': topic_name}])  # If no subtopics, use the topic as a subtopic
            for subtopic in subtopics:
                subtopic_name = subtopic.get('title', '')
                logger.info(f"Topic: {topic_name}, Subtopic: {subtopic_name}")
                
                subtopic_videos = [v for v in videos if v['topic'] == topic_name and v['subtopic'] == subtopic_name]
                
                if not subtopic_videos:
                    all_subtopics_covered = False
                    logger.warning(f"No videos found for {topic_name} - {subtopic_name}")
                else:
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
                        link_video_to_section(course_id, topic_name, subtopic_name, video_id)
                        logger.info(f"Inserted video: {video['title']} for {topic_name} - {subtopic_name}")

    status = 'Complete' if all_subtopics_covered else 'Partial'
    csv_writer.writerow([category, 'Core Category', course_name, examples, status])
    return course_id

async def process_excel_file(file_path):
    try:
        excel_data = read_excel_data(file_path)
        if not excel_data:
            logger.error("Failed to read Excel data")
            return
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return

    create_indexes()

    with open('course_processing_log.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Category', 'Core Category', 'Course Name', 'Examples', 'Status'])

        for category, courses in excel_data.items():
            logger.info(f"Processing category: {category}")
            for course in courses:
                await process_course(category, course, csv_writer)

async def main():
    excel_file_path = r'C:\Users\parag\Desktop\learnVault\Worksheet.xlsx'
    await process_excel_file(excel_file_path)
    print("\nAll courses processed. Check 'course_processing_log.csv' for details.")

if __name__ == "__main__":
    asyncio.run(main())
