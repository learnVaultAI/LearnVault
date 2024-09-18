# Roadmap Project

This project generates a learning roadmap for a given course, integrates YouTube video links related to the course, and stores the data in MongoDB. It is a Flask-based application containerized using Docker.

## Features

- Generate a learning roadmap for a course.
- Fetch and rank relevant YouTube videos for each subtopic in the roadmap.
- Store the roadmap and related data in MongoDB.
- API endpoints to generate the roadmap and integrate YouTube links.

## Folder Structure

```plaintext
roadmap_project/
│
├── app/
│   ├── __init__.py        # Initialize the Flask app and its extensions
│   ├── config.py          # Configuration settings
│   ├── main/
│   │   ├── __init__.py    # Initialize the main module
│   │   ├── roadmap_service.py  # Functions related to roadmap generation
│   │   ├── youtube_service.py   # Functions for interacting with YouTube
│   │   ├── video_ranking.py      # Functions for ranking videos
│   │   ├── integration_service.py# Functions for integrating roadmap with YouTube
│   │   └── mongodb_service.py    # Functions for MongoDB operations
│   └── routes/
│       ├── __init__.py    # Initialize the routes module
│       ├── roadmap_routes.py  # API routes for roadmap generation
│       └── integration_routes.py  # API routes for integrating YouTube links
│
├── tests/
│   ├── __init__.py        # Initialize the tests module
│   ├── test_roadmap_service.py # Tests for roadmap_service
│   ├── test_youtube_service.py  # Tests for youtube_service
│   ├── test_video_ranking.py    # Tests for video_ranking
│   └── test_integration_service.py # Tests for integration_service
│
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── Dockerfile             # Dockerfile for containerizing the application
├── docker-compose.yml     # Docker Compose configuration
├── run.py                 # Entry point to start the application
└── README.md              # This file
```

## Setup

### Prerequisites

- Docker and Docker Compose installed on your machine.
- Python 3.12 (if not using Docker).

### Installing Dependencies

Clone the repository:

```bash
git clone <repository-url>
cd roadmap_project
```

Build and run the Docker container:

```bash
docker-compose up --build
```

This will build the Docker image and start the container.

### Configuration

Environment Variables: Create a `.env` file in the root directory with the following variables:

```env
GEMINI_API_KEY=<your-generative-ai-api-key>
MONGODB_URI=<your-mongodb-uri>
```

## API Endpoints

### Generate Roadmap

- **URL**: `/api/roadmap`
- **Method**: `POST`
- **Body**:
```json
{
  "course_name": "Machine Learning"
}
```
- **Response**:
```json
{
  "roadmap": { ... }
}
```

### Integrate Roadmap with YouTube

- **URL**: `/api/integrate`
- **Method**: `POST`
- **Body**:
```json
{
  "course_name": "Machine Learning"
}
```
- **Response**:
```json
{
  "roadmap_with_links": { ... }
}
```

## Running the Application

### Local Development

If you're not using Docker, you can run the application directly with:

```bash
pip install -r requirements.txt
python run.py
```

### Docker

Use the Docker Compose command provided above to start the application.

## Testing

Run tests using:

```bash
pytest
```

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
