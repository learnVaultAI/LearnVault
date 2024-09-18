# import json
# from app.main.roadmap_service import generate_roadmap
# from app.main.integration_service import integrate_roadmap_with_youtube
# from app.main.mongodb_service import push_to_mongodb

# def main():
#     course_name = "Machine Learning"
#     roadmap = generate_roadmap(course_name)
#     print(json.dumps(roadmap, indent=2))  # Debug print to check roadmap structure
#     integrated_roadmap = integrate_roadmap_with_youtube(roadmap)
#     print(json.dumps(integrated_roadmap, indent=2))
    
#     # Push to MongoDB
#     push_to_mongodb(course_name, roadmap, integrated_roadmap)

# if __name__ == "__main__":
#     main()

# from app import create_app

# app = create_app()

# if __name__ == "__main__":
#     app.run(debug=True)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)


# import os
# import json
# import sys
# from app import create_app
# from app.main.roadmap_service import generate_roadmap
# from app.main.integration_service import integrate_roadmap_with_youtube
# from app.main.mongodb_service import push_to_mongodb



# Programming_Languages = ['Python - Django Flask FastAPI PyTorch TensorFlow',
#  'JavaScript - React Angular Vue.js Node.js Express.js',
#  'Java - Spring Hibernate JavaServer Faces (JSF) Apache Struts',
#  'C++ - Qt Boost POCO',
#  'Ruby - Ruby on Rails Sinatra',
#  'C# - .NET Framework ASP.NET Entity Framework Xamarin',
#  'PHP - Laravel Symfony CodeIgniter',
#  'Go - Gin Echo Revel',
#  'Swift - SwiftUI Vapor',
#  'Rust - Actix Rocket',
#  'Kotlin - Ktor Spring Boot Exposed',
#  'TypeScript - Angular NestJS Next.js',
#  'Scala - Akka Play Framework Apache Spark',
#  'R - Shiny R Markdown',
#  'Dart - Flutter',
#  'MATLAB - Simulink']


# # Define Flask app
# app = create_app()

# def save_course_json(course_name, category, roadmap):
#     # Create category directory if it doesn't exist
#     category_dir = os.path.join('courses', category)
#     os.makedirs(category_dir, exist_ok=True)
    
#     # Define file path
#     file_path = os.path.join(category_dir, f'{course_name}.json')
    
#     # Save JSON file
#     with open(file_path, 'w') as f:
#         json.dump(roadmap, f, indent=2)
#     print(f"Saved {course_name} to {file_path}")

# def run_custom_logic():
#     for category, courses in categories.items():
#         for course_name in courses:
#             print(f"Processing {course_name} in category {category}")
#             roadmap = generate_roadmap(course_name)
#             print(json.dumps(roadmap, indent=2))  # Debug print to check roadmap structure

#             integrated_roadmap = integrate_roadmap_with_youtube(roadmap)
#             print(json.dumps(integrated_roadmap, indent=2))

#             # Save JSON to file
#             save_course_json(course_name, category, integrated_roadmap)
            
#             # Push to MongoDB
#             push_to_mongodb(course_name, roadmap, integrated_roadmap)
#             print(f"Finished processing {course_name}.")

# if __name__ == "__main__":
#     if len(sys.argv) > 1 and sys.argv[1] == 'custom':
#         # Run custom logic
#         run_custom_logic()
#     else:
#         # Run the Flask application
#         app.run(host='0.0.0.0', port=5000, debug=True)
