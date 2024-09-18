
import json
import google.generativeai as genai  # type:ignore
# from app.config import Config
# from app.main.prompts import json_data_roadmap, prompt

# # Configure the API key for Generative AI
# api_key = Config.GEMINI_API_KEY
# api_key = 

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)
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

def refactor_subtopic(subtopic, course_name):
    json_format = """ {
        {subtopic}: "single_search_term_for_youtube_video"
    }

"""
    prompt = f"""
        I am providing you the subtopic name which {subtopic}, for which you have write a precise single search term.
        To create this serach term, I am providing you with a course name which is {course_name}.
        This search term will be used to fetch the video from the youtube and it all depends on your single_search_term as this will be passed to youtube search.
        subtopic: The specific topic within the course you want to search for.
        course_name: The name of the course the subtopic belongs to.
        Make sure that you provide a single term only and not the complete roadmap. The output should be in a JSON format.
        Example:
        {json_format}

    """
    prompt = prompt.replace("{subtopic}", subtopic)
    prompt = prompt.replace("{course_name}", course_name)


    chat_session = model.start_chat(
        history=[{"role": "user", "parts": [prompt]}]
    )
    response = chat_session.send_message("Follow the prompt stictly")
    try:
        # print(prompt)
        keywords = json.loads(response.text)
        print(keywords[subtopic]) 
    except json.JSONDecodeError as e:
        print(f"Failed to decode response as JSON: {e}")
        return None
    return keywords[subtopic]

# if __name__ == "__main__":
#     subtopic = "Gradients and swatches"
#     keywords = refactor_subtopic(subtopic, "Motion Graphics")
#     print(keywords)