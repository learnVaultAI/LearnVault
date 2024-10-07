import json
import re
from functools import lru_cache
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from enhanced_app.config import Config
from enhanced_app.utils.logging_config import logger

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)

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
            cleaned_text = re.sub(r'```json\s*|\s*```', '', response.text).strip()
            try:
                return json.loads(cleaned_text)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON: {cleaned_text}")
                return {"error": "Invalid JSON response"}
        else:
            logger.error("Empty response from Gemini API")
            raise ValueError("Empty response from Gemini API")
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise

@lru_cache(maxsize=100)
def cached_generate_with_gemini(prompt):
    return generate_with_gemini(prompt)
