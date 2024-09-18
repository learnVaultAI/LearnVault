# app\main\mongodb_service.py

from pymongo import MongoClient # type:ignore
from app.config import Config
from pymongo import MongoClient, ASCENDING

# MongoDB connection setup
client = MongoClient(Config.MONGODB_URI)
db = client['roadmap_database']  # Database name
collection = db['roadmaps']      # Collection name

def push_to_mongodb(course_name, roadmap, roadmap_with_links):
    # Create a document with the course name as the key
    document = {
        "course_name": course_name,
        "roadmap": roadmap,
        "roadmap_with_links": roadmap_with_links
    }
    
    # Insert the document into the collection
    result = collection.insert_one(document)
    print(f"Inserted document ID: {result.inserted_id}")



# from pymongo import MongoClient # type:ignore
# from app.config import Config
# from pymongo import MongoClient, ASCENDING

# # MongoDB connection setup
# client = MongoClient(Config.MONGODB_URI)
# db = client['roadmap_indexed_database']  # Database name
# collection = db['roadmaps']      # Collection name

# def push_to_mongodb(course_name, roadmap, roadmap_with_links):
#     # Create a document with the course name as the key
#     document = {
#         "course_name": course_name,
#         "roadmap": roadmap,
#         "roadmap_with_links": roadmap_with_links
#     }
    
#     # Insert the document into the collection
#     result = collection.insert_one(document)
#     print(f"Inserted document ID: {result.inserted_id}")

# def create_indexes():
#     # Create index on core_category
#     collection.create_index([("core_category", ASCENDING)])
#     # Create index on categories.name
#     collection.create_index([("categories.name", ASCENDING)])
#     # Create index on courses.name
#     collection.create_index([("categories.courses.name", ASCENDING)])
#     print("Indexes created successfully.")

# def drop_indexes():
#     # Drop all indexes
#     collection.drop_indexes()
#     print("All indexes dropped.")

# def list_indexes():
#     # List all indexes
#     indexes = collection.list_indexes()
#     for index in indexes:
#         print(index)

# # Example usage
# create_indexes()  # Call this when you want to create indexes
# # drop_indexes()  # Call this to remove all indexes if needed
# # list_indexes()  # Call this to list current indexes
