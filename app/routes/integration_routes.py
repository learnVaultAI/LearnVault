# app/routes/integration_routes.py

import logging
from flask import Blueprint, request, jsonify, Flask # type: ignore
from app.main.roadmap_service import generate_roadmap
from app.main.integration_service import integrate_roadmap_with_youtube
from app.main.mongodb_service import push_to_mongodb
import json

integration_bp = Blueprint('integration', __name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@integration_bp.route('/integration_roadmap', methods=['POST'])
def integration_roadmap():
    data = request.json
    course_name = data.get('course_name')
    category= data.get('category')
    core_category = data.get('core_category')

    if not course_name:
        return jsonify({"error": "Course name is required"}), 400
    
    logger.info("Generating roadmap")
    # Generate roadmap
    try:
        roadmap = generate_roadmap(core_category, category, course_name)
        if roadmap is None:
            return jsonify({"error": "Failed to generate roadmap"}), 500
    except Exception as e:
        logger.error(f"Error generating roadmap: {e}")
        return jsonify({"error": "Error generating roadmap"}), 500
    
    logger.info("Integrating roadmap with YouTube")
    # Integrate with YouTube
    try:
        integrated_roadmap = integrate_roadmap_with_youtube(roadmap)
        with open('integrated_roadmap.json', 'w') as f:
            json.dump(integrated_roadmap, f)

    except Exception as e:
        logger.error(f"Error integrating roadmap with YouTube: {e}")
        return jsonify({"error": "Error integrating roadmap with YouTube"}), 500

    logger.info("Pushing to MongoDB")
    # Push to MongoDB
    try:
        push_to_mongodb(course_name, roadmap, integrated_roadmap)
    except Exception as e:
        logger.error(f"Error pushing to MongoDB: {e}")
        return jsonify({"error": "Error pushing to MongoDB"}), 500

    return jsonify(integrated_roadmap), 200

from app.routes.push_route_test import push_to_mongodb_test
@integration_bp.route('/push_test', methods=['POST'])
def push_test():
    data = request.json
    course_name = data.get('course_name')

    try:
        roadmap = generate_roadmap(course_name)
    
    except Exception as e:
        logger.error(f"Error generating roadmap: {e}")
        return jsonify({"error": "Error generating roadmap"}), 500
    
    try: 
        integrated_roadmap = roadmap
        logger.info("Roadmap integrated successfully")

    except Exception as e:
        logger.error(f"Error integrating roadmap with YouTube: {e}")

    push_to_mongodb_test()
    return jsonify({"message": "Test successful"}), 200


# # Run the Flask application or the function directly
# if __name__ == '__main__':
#     import sys
#     with apps.test_client() as client:
#         if len(sys.argv) > 1 and sys.argv[1] == 'test':
#             # Simulate a request with JSON data
#             response = client.post('/integration-roadmap', json={"course_name": "Data Science"})
#             print("Status Code:", response.status_code)
#             print("Result:", response.get_json())
#         else:
#             # Run the Flask application
#             apps.run(debug=True)