import pandas as pd
import asyncio
import json
import sys
import os
import re
import traceback
import logging
from logging.handlers import RotatingFileHandler
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import google.generativeai as genai
from enhanced_app.config import Config
from functools import lru_cache
from enhanced_app.services.enhanced_youtube_service import get_enhanced_videos_for_roadmap
from enhanced_app.models.roadmap import Roadmap
from enhanced_app.services.category_service import get_category_by_id
from enhanced_app.services.db_service import store_roadmap_and_content
from enhanced_app.services.quiz_assignment_service import generate_quiz, generate_assignment
from bson import ObjectId
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

# Configure logging
log_file = 'roadmap_generation.log'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Configuration for delays
QUIZ_ASSIGNMENT_DELAY = 3  # seconds

# Add this constant
ROADMAP_GENERATION_DELAY = 3  # seconds

# Implement a simple token bucket
class TokenBucket:
    def __init__(self, tokens, fill_rate):
        self.capacity = tokens
        self.tokens = tokens
        self.fill_rate = fill_rate
        self.timestamp = time.time()

    def consume(self, tokens):
        now = time.time()
        self.tokens += (now - self.timestamp) * self.fill_rate
        self.tokens = min(self.tokens, self.capacity)
        self.timestamp = now
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

# Create a token bucket with 60 tokens (requests) per minute
token_bucket = TokenBucket(60, 1)

def generate_with_gemini(prompt, category, core_category):
    try:
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json"
        }
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config
        )

        time.sleep(5)
        response = model.generate_content(prompt)
        
        logger.debug(f"Raw response from API: {response.text}")  # Log the raw response
        
        if response.text:
            try:
                parsed_json = json.loads(response.text)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse entire response as JSON: {e}. Attempting to extract partial JSON.")
                # Implement logic to extract and parse partial JSON if possible
                return None
            
            # Validate the parsed JSON structure
            if 'course_name' not in parsed_json or 'main_topics' not in parsed_json:
                logger.error(f"Invalid JSON structure: {parsed_json}")
                return None
            
            return parsed_json
        else:
            logger.error("Empty response from Gemini API")
            return None
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")  # Improved logging
        logger.exception("Traceback:")  # Log the traceback for better debugging
        return None

@lru_cache(maxsize=100)
def cached_generate_with_gemini(prompt, category, core_category):
    return generate_with_gemini(prompt, category, core_category)

def generate_metadata_with_gemini(prompt, category, core_category):
    try:
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json"
        }
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config
        )

        time.sleep(5)
        response = model.generate_content(prompt)
        
        if response.text:
            try:
                parsed_json = json.loads(response.text)
            except json.JSONDecodeError:
                # If full response isn't valid JSON, try to extract JSON part
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                if match:
                    try:
                        parsed_json = json.loads(match.group(0))
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON from metadata response: {response.text[:500]}...")
                        return None
                else:
                    logger.error(f"No JSON object found in metadata response: {response.text[:500]}...")
                    return None
            
            # Ensure the parsed JSON has the expected structure for metadata
            expected_keys = ['tags', 'level', 'requirements', 'outcomes']
            if all(key in parsed_json for key in expected_keys):
                return parsed_json
            else:
                logger.error(f"Invalid metadata structure: {parsed_json}")
                return None
        else:
            logger.error("Empty response from Gemini API for metadata generation")
            return None
    except Exception as e:
        logger.error(f"Error generating metadata: {e}")  # Improved logging
        logger.exception("Traceback:")  # Log the traceback for better debugging
        return None

def generate_metadata(course_name, category, core_category):
    prompt = f"""Generate metadata for the course "{course_name}" in the category "{category}" (Core: {core_category}).
    Include the following:
    1. A list of relevant tags (5-10 tags)
    2. The difficulty level (Beginner, Intermediate, or Advanced)
    3. A list of prerequisites or requirements (2-5 items)
    4. A list of learning outcomes (3-5 items)

    Format the output as a JSON object with the following structure:

    {{
        "tags": ["tag1", "tag2", ...],
        "level": "Difficulty level",
        "requirements": ["requirement1", "requirement2", ...],
        "outcomes": ["outcome1", "outcome2", ...]
    }}"""

    metadata = generate_metadata_with_gemini(prompt, category, core_category)
    if metadata and isinstance(metadata, dict):
        return json.dumps(metadata)
    return None

def post_process_roadmap(roadmap):
    try:
        metadata_json = generate_metadata(roadmap['course_name'], roadmap['category'], roadmap['core_category'])
        if metadata_json:
            metadata = json.loads(metadata_json)
            roadmap.update(metadata)

        # Rest of the function remains the same
        for i, topic in enumerate(roadmap['main_topics'], 1):
            topic['topic_order'] = i
            for j, subtopic in enumerate(topic['subtopics'], 1):
                subtopic['subtopic_order'] = j

        logger.info("Post-processed roadmap:")
        logger.info(json.dumps(roadmap, indent=2, default=str))

        return roadmap
    except Exception as e:
        logger.error(f"Error in post-processing roadmap: {str(e)}")
        logger.exception("Traceback:")
        return roadmap

class JSONParseError(Exception):
    pass

def parse_partial_json(partial_json):
    try:
        # Try to parse the partial JSON
        return json.loads(partial_json)
    except json.JSONDecodeError as e:
        # If parsing fails, try to find the last complete object
        last_brace_index = partial_json.rfind('}')
        if last_brace_index != -1:
            try:
                return json.loads(partial_json[:last_brace_index+1])
            except json.JSONDecodeError:
                # If that fails too, raise the original error
                raise e
        else:
            raise e

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((Exception, json.JSONDecodeError))
)
async def generate_comprehensive_roadmap(course_name, category, core_category, examples):
    while not token_bucket.consume(1):
        time.sleep(1)
    try:
        logger.info(f"Creating enhanced roadmap for {course_name} in category {category} (Core: {core_category})")
        
        outline_prompt = f"""Create a comprehensive outline for a course on {course_name} in the {category} category (Core: {core_category}).
        Include the following main topics:
        1. Fundamentals of {course_name}
        2. Advanced {course_name} Concepts
        3-5. Cover the following technologies/frameworks: {', '.join(examples)}
        6-7. Best Practices and Real-world Applications

        For each main topic, include 3-5 subtopics. For each subtopic, provide a brief description and 2-3 key points.

        Format the output as a JSON object with the following structure:
        {{
            "course_name": "{course_name}",
            "category": "{category}",
            "core_category": "{core_category}",
            "main_topics": [
                {{
                    "topic_title": "Main Topic Title",
                    "subtopics": [
                        {{
                            "subtopic_title": "Subtopic Title",
                            "description": "Brief description of the subtopic",
                            "key_points": ["Key point 1", "Key point 2", "Key point 3"]
                        }}
                    ]
                }}
            ]
        }}
        """

        response = generate_with_gemini(outline_prompt, category, core_category)
        
        if response:
            logger.info(f"Generated initial outline for {course_name}:")
            logger.info(json.dumps(response, indent=2))
            return response
        else:
            logger.error(f"Failed to generate initial outline for {course_name}")
            return None

    except Exception as e:
        logger.error(f"Error generating enhanced roadmap for {course_name}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None

async def generate_enhanced_roadmaps(excel_data):
    results = []
    for row in excel_data:
        course_name = row['Course Name']
        category = row['Category']
        core_category = row['Core Category']
        examples = row['Examples'].split(', ') if isinstance(row['Examples'], str) else []
        
        try:
            logger.info(f"Starting enhanced roadmap generation for {course_name} in category {category} (Core: {core_category})")
            
            roadmap = await generate_comprehensive_roadmap(course_name, category, core_category, examples)
            if roadmap:
                videos = await get_enhanced_videos_for_roadmap(roadmap)
                
                quizzes = {}
                assignments = {}
                
                for topic in roadmap['main_topics']:
                    for subtopic in topic['subtopics']:
                        # Generate quiz
                        logger.info(f"Generating quiz for {topic['topic_title']} - {subtopic['subtopic_title']}")
                        quiz = generate_quiz(subtopic['description'])
                        quizzes[subtopic['subtopic_title']] = quiz
                        
                        # Generate assignment
                        logger.info(f"Generating assignment for {topic['topic_title']} - {subtopic['subtopic_title']}")
                        assignment = generate_assignment(subtopic['description'])
                        assignments[subtopic['subtopic_title']] = assignment

                try:
                    logger.info(f"Storing roadmap, videos, quizzes, and assignments for {course_name} in database")
                    await store_roadmap_and_content(roadmap, videos, quizzes, assignments)
                except Exception as e:
                    logger.error(f"An error occurred during database storage for {course_name}: {e}")
                    continue
                
                results.append({"roadmap": roadmap, "videos": videos, "quizzes": quizzes, "assignments": assignments})
                logger.info(f"Successfully generated roadmap and content for {course_name}")
            else:
                logger.error(f"Failed to generate roadmap for {course_name}")
        except Exception as e:
            logger.error(f"Error generating roadmap and content for {course_name}: {e}")  # Improved logging
            logger.exception("Traceback:")  # Log the traceback for better debugging
        
    return results

def read_excel_data(file_path):
    try:
        excel_file = pd.ExcelFile(file_path)
        
        all_data = []
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Print column names for debugging
            print(f"Columns in sheet '{sheet_name}': {df.columns.tolist()}")
            
            # Check if required columns exist
            required_columns = ['Category', 'Course Name', 'Examples']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns in sheet '{sheet_name}': {', '.join(missing_columns)}")
            
            # Only select the columns we actually need
            df = df[required_columns]
            
            # Add the sheet name (core category) to each row
            df['Core Category'] = sheet_name
            
            all_data.append(df)
        
        if not all_data:
            raise ValueError("No data found in the Excel file")
        
        combined_df = pd.concat(all_data, ignore_index=True)
        
        return combined_df.to_dict('records')
    except Exception as e:
        logger.error(f"Error reading Excel file: {str(e)}")
        return None

def custom_json_serializer(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return str(obj)  # Default to string representation for unknown types

if __name__ == "__main__":
    # Use raw string for Windows path
    excel_file_path = r'C:\Users\parag\Desktop\learnVault\Worksheet.xlsx'
    
    # Check if file exists
    if not os.path.exists(excel_file_path):
        print(f"Error: File not found at {excel_file_path}")
        sys.exit(1)
    
    try:
        excel_data = read_excel_data(excel_file_path)
        if excel_data is None or len(excel_data) == 0:
            print("Error: No valid data found in the Excel file.")
            sys.exit(1)
    except PermissionError:
        print(f"Error: Unable to open the file. Make sure it's not open in another program.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        logger.error(f"Error reading Excel file: {e}")  # Log the error
        sys.exit(1)
    
    print("Excel data structure:")
    for row in excel_data[:2]:  # Print first two rows
        print(json.dumps(row, indent=2))
    
    try:
        results = asyncio.run(generate_enhanced_roadmaps(excel_data))
        for result in results:
            print("Roadmap:")
            print(json.dumps(result['roadmap'], indent=2, default=custom_json_serializer))
            print("\nVideos:")
            print(json.dumps(result['videos'], indent=2, default=custom_json_serializer))
            print("\nQuizzes:")
            print(json.dumps(result['quizzes'], indent=2, default=custom_json_serializer))
            print("\nAssignments:")
            print(json.dumps(result['assignments'], indent=2, default=custom_json_serializer))
    except Exception as e:
        print(f"Error generating roadmaps and content: {e}")
        print(f"Traceback: {traceback.format_exc()}")