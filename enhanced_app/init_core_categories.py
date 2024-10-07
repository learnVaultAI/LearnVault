from enhanced_app.services.category_service import create_category

def init_core_categories():
    core_categories = [
        {"name": "Programming", "description": "Learn various programming languages and concepts"},
        {"name": "Data Science", "description": "Explore data analysis, machine learning, and statistics"},
        {"name": "Web Development", "description": "Master front-end and back-end web technologies"},
        {"name": "Mobile Development", "description": "Build apps for iOS and Android platforms"},
        {"name": "DevOps", "description": "Learn about continuous integration, deployment, and operations"}
    ]

    for category in core_categories:
        create_category(**category, is_core=True)

    print("Core categories initialized successfully")

if __name__ == "__main__":
    init_core_categories()
