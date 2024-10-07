import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    MONGODB_URI = "mongodb+srv://admin:support2024@cluster0.9uwbitt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    DB_NAME = "structured_vault"
    
    # Collection names
    CORE_CATEGORIES_COLLECTION = "core_categories"  # New collection
    CATEGORIES_COLLECTION = "categories"
    COURSES_COLLECTION = "courses"
    TOPICS_COLLECTION = "topics"
    SUBTOPICS_COLLECTION = "subtopics"
    VIDEOS_COLLECTION = "videos"
    QUIZZES_COLLECTION = "quizzes"
    ASSIGNMENTS_COLLECTION = "assignments"

# Create instances of the configuration variables
MONGODB_URI = Config.MONGODB_URI
DB_NAME = Config.DB_NAME
