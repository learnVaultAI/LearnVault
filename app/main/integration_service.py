# app/main/integration_service.py
import logging
from app.main.youtube_service import get_youtube_search_results
from app.main.video_ranking import rank_videos_by_relevance
from app.main.subtopic_refactor_service import refactor_subtopic

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def integrate_roadmap_with_youtube(roadmap):
    # Log the start of the process
    logger.info("Starting integration of roadmap with YouTube.")

    if not isinstance(roadmap, dict):
        logger.error("Expected roadmap to be a dictionary, got %s instead", type(roadmap))
        raise ValueError("Expected roadmap to be a dictionary")

    integrated_roadmap = roadmap.copy()

    print("integrated_roadmap", integrated_roadmap)

    # Iterate through each topic section in the roadmap
    for topic_section in integrated_roadmap.get('roadmap', {}).get('topics', []):
        if not isinstance(topic_section, dict):
            logger.error("Expected topic_section to be a dictionary, got %s", type(topic_section))
            raise ValueError("Expected topic_section to be a dictionary")

        sections = topic_section.get('sections', [])
        if not isinstance(sections, list):
            logger.error("Expected sections to be a list, got %s", type(sections))
            raise ValueError("Expected sections to be a list")

        for section in sections:
            if not isinstance(section, dict):
                logger.error("Expected section to be a dictionary, got %s", type(section))
                raise ValueError("Expected section to be a dictionary")

            subtopics = section.get('subtopics', [])
            if not isinstance(subtopics, list):
                logger.error("Expected subtopics to be a list, got %s", type(subtopics))
                raise ValueError("Expected subtopics to be a list")

            for subtopic in subtopics:
                if isinstance(subtopic, str):
                    logger.info("Fetching videos for subtopic: %s", subtopic)
                    try:
                        # Get YouTube search results
                        refactored_subtopic = refactor_subtopic(subtopic, course_name=topic_section.get('course_name', ''))
                        logger.info("Refactored subtopic: %s", refactored_subtopic)

                        videos = get_youtube_search_results(refactored_subtopic)
                        logger.info("Fetched %d videos for subtopic: %s", len(videos), subtopic)

                        # Rank videos by relevance
                        ranked_videos = rank_videos_by_relevance(subtopic, videos)
                        logger.info("Ranked videos for subtopic: %s", subtopic)

                        if 'videos' not in topic_section:
                            topic_section['videos'] = []

                        # Append ranked videos to the topic section
                        topic_section['videos'].append({'subtopic': subtopic, 'videos': ranked_videos})
                        logger.info("Added ranked videos for subtopic: %s", subtopic)

                    except Exception as e:
                        # Log any errors that occur during the YouTube search and ranking process
                        logger.error("Error processing subtopic '%s': %s", subtopic, str(e))
                        continue
                else:
                    logger.error("Expected subtopic to be a string, got %s", type(subtopic))


    logger.info("Completed integration of roadmap with YouTube.")
    return integrated_roadmap
