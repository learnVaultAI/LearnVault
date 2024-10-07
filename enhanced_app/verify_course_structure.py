import pymongo
from bson import ObjectId
import json
from pprint import pprint

# MongoDB connection details
MONGO_URI = "mongodb+srv://admin:support2024@cluster0.9uwbitt.mongodb.net/"
DB_NAME = "learnvault"

def connect_to_mongodb():
    client = pymongo.MongoClient(MONGO_URI)
    return client[DB_NAME]

def verify_course_structure(db):
    course = db.courses.find_one(sort=[("created_at", pymongo.DESCENDING)])
    
    if not course:
        print("No courses found in the database.")
        return

    print("Verifying course structure:")
    print(f"Course ID: {course['_id']}")
    print(f"Title: {course['title']}")
    print(f"Description: {course['description']}")
    print(f"Number of topics: {len(course['topics'])}")

    for topic in course['topics']:
        print(f"\nTopic structure: {topic.keys()}")
        if 'topic' in topic:
            print(f"Topic: {topic['topic']}")
        elif 'title' in topic:
            print(f"Topic: {topic['title']}")
        else:
            print("Topic name not found")

        if 'sections' in topic:
            for section in topic['sections']:
                print(f"  Subtopic structure: {section.keys()}")
                if 'topic' in section:
                    print(f"  Subtopic: {section['topic']}")
                elif 'title' in section:
                    print(f"  Subtopic: {section['title']}")
                else:
                    print("  Subtopic name not found")

                content_count = db.content.count_documents({"course_id": course['_id'], "subtopic": section.get('topic') or section.get('title')})
                print(f"    Number of content items: {content_count}")

                content = db.content.find_one({"course_id": course['_id'], "subtopic": section.get('topic') or section.get('title')})
                if content:
                    print(f"    Sample content:")
                    print(f"      Title: {content['title']}")
                    print(f"      Type: {content['type']}")
                    print(f"      URL: {content.get('metadata', {}).get('file_url', 'N/A')}")
        else:
            print("  No sections found in this topic")

    print("\nFull course structure:")
    pprint(course)

def main():
    db = connect_to_mongodb()
    verify_course_structure(db)

if __name__ == "__main__":
    main()
