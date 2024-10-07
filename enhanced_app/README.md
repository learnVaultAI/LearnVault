LearnVault
LearnVault is an innovative online learning platform that leverages AI to generate comprehensive course roadmaps and curate relevant educational content.
Features
AI-powered course roadmap generation
Automatic content curation from YouTube
Hierarchical course structure with topics and subtopics
User-friendly interface for course exploration and learning
Getting Started
Prerequisites
Python 3.8+
MongoDB
pip
Installation
Clone the repository:
```
git clone https://github.com/yourusername/learnvault.git
cd learnvault
```
Install dependencies:
```
pip install -r requirements.txt
```
Set up environment variables:
Create a .env file in the root directory and add the following:
```
MONGODB_URI=your_mongodb_connection_string
OPENAI_API_KEY=your_openai_api_key
```
Run the application:
```
python main.py
```
Project Structure
```
learnvault/
│
├── enhanced_app/
│ ├── services/
│ │ ├── course_generation_service.py
│ │ ├── enhanced_youtube_service.py
│ │ └── openai_service.py
│ ├── utils/
│ │ ├── database.py
│ │ └── logging_config.py
│ └── main.py
│
├── tests/
│ ├── test_course_generation.py
│ └── test_youtube_service.py
│
├── .env
├── requirements.txt
└── README.md
```
Database Schema
Our application uses MongoDB with the following main collections:
Courses Collection
```json
{
"id": ObjectId,
"title": String,
"description": String,
"category": String,
"tags": [String],
"status": String, // e.g., "published", "draft"
"topics": [
{
"topic_title": String,
"sections": [
{
"topic": String, // Subtopic title
"subtopics": [String],
"videos": [ObjectId] // References to Content collection
}
]
}
],
"created_at": Date,
"updated_at": Date
}
```
Content Collection
```json
{
"id": ObjectId,
"course_id": ObjectId,
"type": String, // e.g., "video"
"title": String,
"metadata": {
"duration": String,
"file_url": String,
"views": String
},
"created_at": Date,
"updated_at": Date
}
```
API Documentation
(Include API endpoints and their descriptions here)
Contributing
Fork the repository
Create your feature branch (```git checkout -b feature/AmazingFeature```)
Commit your changes (```git commit -m 'Add some AmazingFeature'```)
Push to the branch (```git push origin feature/AmazingFeature```)
Open a pull request
License
This project is licensed under the MIT License - see the LICENSE.md file for details.
Acknowledgments
OpenAI for providing the GPT model used in course generation
YouTube for being a source of educational content
All contributors and supporters of the project