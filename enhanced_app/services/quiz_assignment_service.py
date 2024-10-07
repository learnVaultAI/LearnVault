import google.generativeai as genai
from enhanced_app.config import Config
import time
import json
import logging
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

logger = logging.getLogger(__name__)

def extract_json_from_markdown(text):
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    return match.group(1).strip() if match else text

def parse_assignment_questions(text):
    # Try to parse as JSON first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # If JSON parsing fails, try to extract questions manually
        questions = re.findall(r'"([^"]+)"', text)
        if questions:
            return questions
        else:
            # If no quoted strings found, split by newlines and clean up
            return [q.strip() for q in text.split('\n') if q.strip()]

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

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(Exception)
)
def generate_quiz(subtopic_description):
    while not token_bucket.consume(1):
        time.sleep(1)
    try:
        logger.info(f"Generating quiz for subtopic: {subtopic_description[:50]}...")
        prompt = f"""
        Based on the following subtopic description, generate up to 10 multiple-choice questions for a quiz.
        Each question should have 4 options with one correct answer.
        Format the output as a JSON array of objects, where each object has the following structure:
        [
            {{
                "question": "What is the capital of France?",
                "options": ["London", "Berlin", "Paris", "Madrid"],
                "correct_answer": 2
            }},
            {{
                "question": "Which planet is known as the Red Planet?",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "correct_answer": 1
            }}
        ]
        Return only the JSON array, without any additional text or formatting.

        Subtopic description:
        {subtopic_description}
        """
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 8092,
            "response_mime_type": "application/json"
        }
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config
        )
        response = model.generate_content(prompt)
        
        if "Resource has been exhausted" in str(response):
            logger.warning("Resource exhausted. Retrying...")
            raise Exception("Resource exhausted")
        
        json_text = extract_json_from_markdown(response.text)
        quiz_questions = json.loads(json_text)
        
        # Ensure the output is structured correctly for the database
        quiz_questions = [{"question": q['question'], "options": q['options'], "correct_answer": q['correct_answer']} for q in quiz_questions]
        
        logger.info(f"Successfully generated {len(quiz_questions)} quiz questions")
        return quiz_questions
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise  # This will trigger the retry

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(Exception)
)
def generate_assignment(subtopic_description):
    while not token_bucket.consume(1):
        time.sleep(1)
    try:
        logger.info(f"Generating assignment for subtopic: {subtopic_description[:50]}...")
        prompt = f"""
        Based on the following subtopic description, generate up to 10 open-ended questions for an assignment.
        Each question should require a short paragraph answer.
        Format the output as a JSON array of strings, where each string is a question.
        Example:
        [
            "Explain the concept of object-oriented programming and its main principles.",
            "Describe the differences between a list and a tuple in Python, including use cases for each.",
            "What are the benefits of using version control systems like Git in software development?"
        ]
        Return only the JSON array, without any additional text or formatting.

        Subtopic description:
        {subtopic_description}
        """
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
            "response_mime_type": "application/json"
        }
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config
        )
        response = model.generate_content(prompt)
        
        if "Resource has been exhausted" in str(response):
            logger.warning("Resource exhausted. Retrying...")
            raise Exception("Resource exhausted")
        
        json_text = extract_json_from_markdown(response.text)
        assignment_questions = parse_assignment_questions(json_text)
        
        # Ensure the output is structured correctly for the database
        assignment_questions = [{"instructions": q} for q in assignment_questions]
        
        if not assignment_questions:
            logger.warning("Failed to parse assignment questions. Retrying...")
            raise Exception("Empty assignment questions")
        
        logger.info(f"Successfully generated {len(assignment_questions)} assignment questions")
        return assignment_questions
    except Exception as e:
        logger.error(f"Error generating assignment: {e}")
        raise  # This will trigger the retry