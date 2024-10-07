from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from enhanced_app.config import MONGODB_URI, DB_NAME

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

class Subtopic(BaseModel):
    title: str
    description: str
    key_points: List[str]

class MainTopic(BaseModel):
    title: str
    subtopics: List[Subtopic]

class Video(BaseModel):
    title: str
    description: str
    video_id: str
    thumbnail: str

class Roadmap(BaseModel):
    course_name: str
    category: str
    main_topics: List[MainTopic]
    related_videos: Optional[List[Video]] = None
    title: str
    description: str
    category_id: str
    topics: List[Dict[str, Any]]  # This should contain the topic structure we defined

class Category:
    collection = db.categories

    @classmethod
    def create(cls, name, description, is_core=False, parent_id=None, icon_url=None):
        category = {
            "name": name,
            "slug": name.lower().replace(" ", "-"),
            "description": description,
            "parent_id": ObjectId(parent_id) if parent_id else None,
            "is_core": is_core,
            "order": cls.collection.count_documents({}) + 1,
            "icon_url": icon_url,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = cls.collection.insert_one(category)
        return result.inserted_id

    @classmethod
    def get_by_id(cls, category_id):
        return cls.collection.find_one({"_id": ObjectId(category_id)})

    @classmethod
    def get_core_categories(cls):
        return list(cls.collection.find({"is_core": True}))

    @classmethod
    def get_all_categories(cls):
        return list(cls.collection.find())

    @classmethod
    def update(cls, category_id, **kwargs):
        kwargs["updated_at"] = datetime.utcnow()
        cls.collection.update_one({"_id": ObjectId(category_id)}, {"$set": kwargs})

    @classmethod
    def delete(cls, category_id):
        cls.collection.delete_one({"_id": ObjectId(category_id)})

    @classmethod
    def get_or_create(cls, name, description="", is_core=False, parent_id=None):
        existing = cls.collection.find_one({"name": name})
        if existing:
            return existing
        return cls.create(name, description, is_core, parent_id)

class Roadmap:
    collection = db.roadmaps

    @classmethod
    def create(cls, course_name, category, description, category_id, topics):
        roadmap = {
            "course_name": course_name,
            "category": category,
            "description": description,
            "category_id": ObjectId(category_id),
            "topics": topics,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = cls.collection.insert_one(roadmap)
        return str(result.inserted_id)
