from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from enhanced_app.config import Config, MONGODB_URI, DB_NAME
import ssl
import logging
import json
from datetime import datetime

client = MongoClient(MONGODB_URI, server_api=ServerApi('1'), tls=True, tlsAllowInvalidCertificates=True)
db = client[DB_NAME]

logger = logging.getLogger(__name__)

def create_indexes():
    db[Config.CORE_CATEGORIES_COLLECTION].create_index([("name", 1)], unique=True)
    db[Config.CATEGORIES_COLLECTION].create_index([("name", 1)], unique=True)
    db[Config.CATEGORIES_COLLECTION].create_index([("core_category_id", 1)])
    db[Config.COURSES_COLLECTION].create_index([("name", 1)], unique=True)
    db[Config.COURSES_COLLECTION].create_index([("category_id", 1)])
    db[Config.TOPICS_COLLECTION].create_index([("course_id", 1)])
    db[Config.TOPICS_COLLECTION].create_index([("topic_order", 1)])
    db[Config.SUBTOPICS_COLLECTION].create_index([("topic_id", 1)])
    db[Config.SUBTOPICS_COLLECTION].create_index([("subtopic_order", 1)])
    db[Config.VIDEOS_COLLECTION].create_index([("subtopic_id", 1)])
    db[Config.VIDEOS_COLLECTION].create_index([("video_order", 1)])
    db[Config.QUIZZES_COLLECTION].create_index([("subtopic_id", 1)])
    db[Config.QUIZZES_COLLECTION].create_index([("quiz_order", 1)])
    db[Config.ASSIGNMENTS_COLLECTION].create_index([("subtopic_id", 1)])
    db[Config.ASSIGNMENTS_COLLECTION].create_index([("assignment_order", 1)])

async def store_roadmap_and_content(roadmap, videos, quizzes, assignments):
    try:
        logger.info(f"Storing roadmap and content for course: {roadmap.get('course_name', 'Unknown')}")

        # Insert or get core category
        core_category_id = insert_core_category({"name": roadmap['core_category']})
        logger.info(f"Core category ID: {core_category_id}")

        # Insert or get category
        category_data = {
            "name": roadmap['category'],
            "core_category_id": ObjectId(core_category_id)  # Convert to ObjectId
        }
        category_id = insert_category(category_data)
        logger.info(f"Category ID: {category_id}")

        # Insert or update course
        course_data = {
            "title": roadmap.get('course_name', ''),  # Ensure this matches the generated output
            "description": roadmap.get('description', ''),
            "category_id": ObjectId(category_id),  # Ensure this is an ObjectId
            "core_category_id": ObjectId(core_category_id),  # Ensure this is an ObjectId
            "tags": roadmap.get('tags', []),
            "level": roadmap.get('level', ''),
            "requirements": roadmap.get('requirements', []),
            "outcomes": roadmap.get('outcomes', [])
        }
        logger.info(f"Course data before insertion: {course_data}")
        course_id = insert_course(course_data)
        logger.info(f"Inserted course with ID: {course_id}")

        # Process main topics
        for topic in roadmap['main_topics']:
            topic_data = {
                "course_id": ObjectId(course_id),  # Ensure this is an ObjectId
                "title": topic['topic_title'],
                "order": topic.get('order', 0)  # Assuming you have an order field
            }
            topic_id = insert_topic(topic_data)
            logger.info(f"Inserted topic: {topic['topic_title']}, ID: {topic_id}")

            # Process subtopics
            for subtopic in topic['subtopics']:
                subtopic_data = {
                    "topic_id": ObjectId(topic_id),  # Ensure this is an ObjectId
                    "title": subtopic['subtopic_title'],
                    "description": subtopic['description'],
                    "order": subtopic.get('order', 0)  # Assuming you have an order field
                }
                subtopic_id = insert_subtopic(subtopic_data)
                logger.info(f"Inserted subtopic: {subtopic['subtopic_title']}, ID: {subtopic_id}")

                # Insert quizzes for this subtopic
                quiz_data = {
                    "sub_topic_id": ObjectId(subtopic_id),
                    "questions": quizzes.get(subtopic['subtopic_title'], []),  # Assuming quizzes are keyed by subtopic title
                    "quiz_order": 1  # Assuming one quiz per subtopic
                }
                insert_quiz(quiz_data)

                # Insert assignments for this subtopic
                assignment_data = {
                    "sub_topic_id": ObjectId(subtopic_id),
                    "instructions": assignments.get(subtopic['subtopic_title'], []),  # Assuming assignments are keyed by subtopic title
                    "assignment_order": 1  # Assuming one assignment per subtopic
                }
                insert_assignment(assignment_data)

        logger.info(f"Successfully stored roadmap for course: {roadmap['course_name']}")
        return course_id  # Return the course ID for reference

    except Exception as e:
        logger.error(f"Failed to store roadmap and content: {str(e)}")
        raise


# async def store_roadmap_and_content(roadmap, videos, quizzes, assignments):
#     try:
#         logger.info(f"Storing roadmap and content for course: {roadmap.get('course_name', 'Unknown')}")

#         # Insert or get core category
#         core_category_id = insert_core_category({"name": roadmap['core_category']})
#         logger.info(f"Core category ID: {core_category_id}")

#         # Insert or get category
#         category_data = {
#             "name": roadmap['category'],
#             "core_category_id": ObjectId(core_category_id)  # Convert to ObjectId
#         }
#         category_id = insert_category(category_data)
#         logger.info(f"Category ID: {category_id}")

#         # Insert or update course
#         course_data = {
#             "title": roadmap.get('course_name', ''),  # Ensure this matches the generated output
#             "description": roadmap.get('description', ''),
#             "category_id": ObjectId(category_id),  # Ensure this is an ObjectId
#             "core_category_id": ObjectId(core_category_id),  # Ensure this is an ObjectId
#             "tags": roadmap.get('tags', []),
#             "level": roadmap.get('level', ''),
#             "requirements": roadmap.get('requirements', []),
#             "outcomes": roadmap.get('outcomes', [])
#         }
#         logger.info(f"Course data before insertion: {course_data}")
#         course_id = insert_course(course_data)
#         logger.info(f"Inserted course with ID: {course_id}")

#         # Process main topics
#         for topic in roadmap['main_topics']:
#             topic_data = {
#                 "course_id": course_id,
#                 "title": topic['topic_title'],
#                 "order": topic.get('order', 0)  # Assuming you have an order field
#             }
#             topic_id = insert_topic(topic_data)
#             logger.info(f"Inserted topic: {topic['topic_title']}, ID: {topic_id}")

#             # Process subtopics
#             for subtopic in topic['subtopics']:
#                 subtopic_data = {
#                     "topic_id": topic_id,
#                     "title": subtopic['subtopic_title'],
#                     "description": subtopic['description'],
#                     "order": subtopic.get('order', 0)  # Assuming you have an order field
#                 }
#                 subtopic_id = insert_subtopic(subtopic_data)
#                 logger.info(f"Inserted subtopic: {subtopic['subtopic_title']}, ID: {subtopic_id}")

#                 # Insert quizzes for this subtopic
#                 quiz_data = {
#                     "sub_topic_id": subtopic_id,
#                     "questions": quizzes.get(subtopic['subtopic_title'], []),  # Assuming quizzes are keyed by subtopic title
#                     "quiz_order": 1  # Assuming one quiz per subtopic
#                 }
#                 insert_quiz(quiz_data)

#                 # Insert assignments for this subtopic
#                 assignment_data = {
#                     "sub_topic_id": subtopic_id,
#                     "instructions": assignments.get(subtopic['subtopic_title'], []),  # Assuming assignments are keyed by subtopic title
#                     "assignment_order": 1  # Assuming one assignment per subtopic
#                 }
#                 insert_assignment(assignment_data)

#         logger.info(f"Successfully stored roadmap for course: {roadmap['course_name']}")
#         return course_id  # Return the course ID for reference

#     except Exception as e:
#         logger.error(f"Failed to store roadmap and content: {str(e)}")
#         raise


def insert_core_category(core_category_data):
    try:
        result = db[Config.CORE_CATEGORIES_COLLECTION].update_one(
            {"name": core_category_data['name']},
            {"$set": core_category_data},
            upsert=True
        )
        return str(result.upserted_id) if result.upserted_id else str(db[Config.CORE_CATEGORIES_COLLECTION].find_one({"name": core_category_data['name']})['_id'])
    except Exception as e:
        logger.error(f"Error inserting/updating core category: {e}")
        raise

def insert_category(category_data):
    try:
        result = db[Config.CATEGORIES_COLLECTION].update_one(
            {"name": category_data['name']},
            {"$set": category_data},
            upsert=True
        )
        return str(result.upserted_id) if result.upserted_id else str(db[Config.CATEGORIES_COLLECTION].find_one({"name": category_data['name']})['_id'])
    except Exception as e:
        logger.error(f"Error inserting/updating category: {e}")
        raise

def insert_course(course_data):
    try:
        logger.info(f"Inserting course: {course_data}")
        
        # If title is None or an empty string, generate a temporary title
        if not course_data.get('title'):
            temp_title = f"Untitled Course {datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            logger.warning(f"Course title was null or empty. Using temporary title: {temp_title}")
            course_data['title'] = temp_title

        result = db[Config.COURSES_COLLECTION].update_one(
            {"title": course_data['title']},
            {"$set": course_data},
            upsert=True
        )
        inserted_id = result.upserted_id if result.upserted_id else db[Config.COURSES_COLLECTION].find_one({"title": course_data['title']})['_id']
        
        # If we used a temporary title, log this for future reference
        if course_data['title'].startswith("Untitled Course"):
            logger.info(f"Inserted course with temporary title. ID: {inserted_id}, Title: {course_data['title']}")
        
        logger.info(f"Successfully inserted/updated course: {course_data['title']}, ID: {inserted_id}")
        return str(inserted_id)
    except Exception as e:
        logger.error(f"Error inserting/updating course: {e}")
        logger.error(f"Course data: {course_data}")
        raise

def insert_topic(topic_data):
    try:
        result = db[Config.TOPICS_COLLECTION].insert_one(topic_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting topic: {e}")
        raise

def insert_subtopic(subtopic_data):
    try:
        result = db[Config.SUBTOPICS_COLLECTION].insert_one(subtopic_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting subtopic: {e}")
        raise

def insert_video(video_data):
    try:
        result = db[Config.VIDEOS_COLLECTION].insert_one(video_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting video: {e}")
        raise

def insert_quiz(quiz_data):
    try:
        result = db[Config.QUIZZES_COLLECTION].insert_one(quiz_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting quiz: {e}")
        raise

def insert_assignment(assignment_data):
    try:
        result = db[Config.ASSIGNMENTS_COLLECTION].insert_one(assignment_data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting assignment: {e}")
        raise

def get_course_by_id(course_id):
    course = db[Config.COURSES_COLLECTION].find_one({"_id": ObjectId(course_id)})
    if not course:
        return None

    topics = list(db[Config.TOPICS_COLLECTION].find({"course_id": str(course["_id"])}).sort("topic_order", 1))
    for topic in topics:
        subtopics = list(db[Config.SUBTOPICS_COLLECTION].find({"topic_id": str(topic["_id"])}).sort("subtopic_order", 1))
        for subtopic in subtopics:
            subtopic["videos"] = list(db[Config.VIDEOS_COLLECTION].find({"subtopic_id": str(subtopic["_id"])}).sort("video_order", 1))
            subtopic["quiz"] = db[Config.QUIZZES_COLLECTION].find_one({"subtopic_id": str(subtopic["_id"])})
            subtopic["assignment"] = db[Config.ASSIGNMENTS_COLLECTION].find_one({"subtopic_id": str(subtopic["_id"])})
        topic["subtopics"] = subtopics
    course["topics"] = topics

    return course

def get_all_courses():
    return list(db[Config.COURSES_COLLECTION].find())

def get_courses_by_category(category_name):
    category = db[Config.CATEGORIES_COLLECTION].find_one({"name": category_name})
    if not category:
        return []
    return list(db[Config.COURSES_COLLECTION].find({"category_id": ObjectId(category["_id"])}))  # Use ObjectId

# Call this function when your application starts
def setup_database():
    create_indexes()

# Add this line at the end of the file
setup_database()