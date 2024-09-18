
from app.main.mongodb_service import push_to_mongodb
from app.main.roadmap_service import generate_roadmap
from flask import request 

def push_to_mongodb_test():
    course_name = "Machine Learning"
    roadmap = generate_roadmap(course_name)
    roadmap_with_links = roadmap
    push_to_mongodb(course_name, roadmap, roadmap_with_links)