import pandas as pd
import asyncio
import json
import sys
import os
import re
import traceback
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from enhanced_app.config import Config
import asyncio
from functools import lru_cache
from enhanced_app.services.enhanced_youtube_service import get_youtube_search_results
from enhanced_app.models.roadmap import Roadmap
from enhanced_app.services.category_service import get_category_by_id

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

def read_excel_data(file_path):
    df = pd.read_excel(file_path, sheet_name='Programming')
    return df.to_dict('records')

def get_course_examples(course_name, excel_data):
    for row in excel_data:
        if row['Course Name'] == course_name:
            return row['Examples'].split(', ')
    return []

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_with_gemini(prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            },
            stream=False,
            safety_settings=[],
        )
        
        if response.text:
            # Remove code block markers and leading/trailing whitespace
            cleaned_text = re.sub(r'```json\s*|\s*```', '', response.text).strip()
            try:
                # Try to parse the cleaned text as JSON
                return json.loads(cleaned_text)
            except json.JSONDecodeError:
                # If it's still not valid JSON, wrap the text in a JSON structure
                return {"text": response.text}
        else:
            raise ValueError("Empty response from Gemini API")
    except Exception as e:
        print(f"Error generating content: {e}")
        raise

@lru_cache(maxsize=100)
def cached_generate_with_gemini(prompt):
    return generate_with_gemini(prompt)

async def generate_initial_outline(course_name, category, examples):
    prompt = f"""Create a comprehensive outline for a course on {course_name} in the {category} category.
    Include the following main topics:
    1. Fundamentals of {course_name}
    2. Advanced {course_name} Concepts
    3-5. Cover the following technologies/frameworks: {', '.join(examples)}
    6-7. Best Practices and Real-world Applications

    For each main topic, provide 3-5 subtopics.
    Format the output as a JSON object with the following structure:
    {{
        "course_name": "{course_name}",
        "category": "{category}",
        "main_topics": [
            {{
                "title": "Main Topic 1",
                "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3"]
            }},
            // ... more main topics
        ]
    }}
    Ensure the content is detailed and covers both the core language/technology and the specific frameworks/libraries."""
    
    outline = await asyncio.to_thread(cached_generate_with_gemini, prompt)
    return outline

async def expand_topic(topic, course_name):
    prompt = f"""For the topic '{topic['title']}' in the course on {course_name}, provide a detailed expansion.
    For each subtopic, give a brief description and list 3-5 key points or concepts to be covered.
    Format the output as a JSON object with the following structure:
    {{
        "title": "{topic['title']}",
        "subtopics": [
            {{
                "title": "Subtopic 1",
                "description": "Brief description of subtopic 1",
                "key_points": ["Point 1", "Point 2", "Point 3"]
            }},
            // ... more subtopics
        ]
    }}
    Ensure the content is comprehensive and at an appropriate depth for the course level."""
    
    expanded = await asyncio.to_thread(cached_generate_with_gemini, prompt)
    return expanded

async def generate_comprehensive_roadmap(course_name, category, excel_data):
    examples = get_course_examples(course_name, excel_data)
    
    # Step 1: Generate initial outline
    outline_task = asyncio.create_task(generate_initial_outline(course_name, category, examples))
    
    # Step 2: Expand each main topic (will be executed after outline is generated)
    outline = await outline_task
    expansion_tasks = [asyncio.create_task(expand_topic(topic, course_name)) for topic in outline.get('main_topics', [])]
    
    expanded_topics = await asyncio.gather(*expansion_tasks)
    
    complete_roadmap = {
        "course_name": course_name,
        "category": category,
        "main_topics": expanded_topics
    }
    
    return complete_roadmap

async def create_enhanced_roadmap(course_name, category, excel_data):
    try:
        roadmap = await generate_comprehensive_roadmap(course_name, category, excel_data)
        return roadmap
    except Exception as e:
        print(f"Error generating enhanced roadmap: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return None

async def generate_enhanced_roadmap(category_id, course_name, examples=""):
    category = get_category_by_id(category_id)
    if not category:
        raise ValueError("Invalid category")

    # Convert examples to a list if it's a string
    if isinstance(examples, str):
        examples = [example.strip() for example in examples.split(',') if example.strip()]

    # Use the existing create_enhanced_roadmap function
    roadmap = await create_enhanced_roadmap(course_name, category['name'], examples)
    
    if roadmap is None:
        raise ValueError("Failed to generate roadmap")

    # Fetch videos for each topic and subtopic
    for topic in roadmap.get('topics', []):
        topic_title = topic['topic_title']
        topic_videos = await get_youtube_search_results(course_name, topic_title, "", max_results=3)
        topic['videos'] = topic_videos

        for section in topic.get('sections', []):
            section_title = section['topic']
            section_videos = await get_youtube_search_results(course_name, topic_title, section_title, max_results=2)
            section['videos'] = section_videos

    # Create a new roadmap with the generated content and videos
    roadmap_data = {
        "title": course_name,
        "description": f"A comprehensive roadmap for {course_name} within the {category['name']} category",
        "category_id": category_id,
        "topics": roadmap.get('topics', [])  # Now includes videos
    }
    roadmap_id = Roadmap.create(**roadmap_data)

    return roadmap_id

if __name__ == "__main__":
    # Use raw string for Windows path
    excel_file_path = r'C:\Users\parag\Desktop\learnVault\New Microsoft Excel Worksheet.xlsx'
    
    # Check if file exists
    if not os.path.exists(excel_file_path):
        print(f"Error: File not found at {excel_file_path}")
        sys.exit(1)
    
    try:
        excel_data = read_excel_data(excel_file_path)
    except PermissionError:
        print(f"Error: Unable to open the file. Make sure it's not open in another program.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)
    
    course_name = "Python"
    category = "Programming"
    
    roadmap = asyncio.run(create_enhanced_roadmap(course_name, category, excel_data))
    print(json.dumps(roadmap, indent=2))
