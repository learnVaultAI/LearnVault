# app/routes/roadmap_routes.py

from flask import Blueprint, request, jsonify # type: ignore
from app.main.roadmap_service import generate_roadmap
from app.main.integration_service import integrate_roadmap_with_youtube
from app.main.mongodb_service import push_to_mongodb

roadmap_bp = Blueprint('roadmap', __name__)

@roadmap_bp.route('/generate_roadmap', methods=['POST'])
def generate_roadmap_route():
    data = request.json
    core_category = data.get('core_category')
    category = data.get('category')
    course_name = data.get('course_name')

    if not course_name:
        return jsonify({'error': 'course_name is required'}), 400

    roadmap = generate_roadmap(core_category=core_category, category=category, course_name=course_name)
    if roadmap is None:
        return jsonify({'error': 'Failed to generate roadmap'}), 500


    # integrated_roadmap = integrate_roadmap_with_youtube(roadmap)
    # push_to_mongodb(course_name, roadmap, integrated_roadmap)
    
    return jsonify(roadmap), 200

# # app/routes/roadmap_routes.py

# from flask import Blueprint, request, jsonify # type: ignore
# from app.main.roadmap_service import generate_roadmap
# from app.main.integration_service import integrate_roadmap_with_youtube
# from app.main.mongodb_service import push_to_mongodb

# roadmap_bp = Blueprint('roadmap', __name__)

# @roadmap_bp.route('/generate_roadmap', methods=['POST'])
# def generate_roadmap_route():
#     data = request.json
#     core_category = data.get('core_category')
#     category = data.get('category')
#     course_name = data.get('course_name')

#     if not course_name:
#         return jsonify({'error': 'course_name is required'}), 400

#     roadmap = generate_roadmap(core_category=core_category, category=category, course_name=course_name)
#     if roadmap is None:
#         return jsonify({'error': 'Failed to generate roadmap'}), 500


#     # integrated_roadmap = integrate_roadmap_with_youtube(roadmap)
#     # push_to_mongodb(course_name, roadmap, integrated_roadmap)
    
#     return jsonify(roadmap), 200
