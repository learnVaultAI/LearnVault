# app/main/roadmap_service.py

import json
import google.generativeai as genai  # type:ignore
from app.config import Config
from app.main.prompts import json_data_roadmap, prompt

# Configure the API key for Generative AI
api_key = Config.GEMINI_API_KEY
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

def generate_roadmap(core_category, category, course_name):
    roadmap_template = json_data_roadmap + prompt.replace("{userInput}", course_name)
    chat_session = model.start_chat(
        history=[{"role": "user", "parts": [roadmap_template]}]
    )
    response = chat_session.send_message("Generate a roadmap for " + course_name)
    try:
        print(roadmap_template)
        roadmap = json.loads(response.text)
    except json.JSONDecodeError as e:
        print(f"Failed to decode response as JSON: {e}")
        return None
    
        # Ensure roadmap structure exists
    if "roadmap" in roadmap:
        # Add core_category_title and category_title at the right levels
        roadmap["roadmap"]["core_category"] = core_category
        roadmap["roadmap"]["category"] = category

    return roadmap


# import json
# import google.generativeai as genai  # type:ignore
# from app.config import Config
# from app.main.prompts import json_data_roadmap, prompt

# # Configure the API key for Generative AI
# api_key = Config.GEMINI_API_KEY
# genai.configure(api_key=api_key)
# generation_config = {
#     "temperature": 1,
#     "top_p": 0.95,
#     "top_k": 64,
#     "max_output_tokens": 8192,
#     "response_mime_type": "application/json"
# }
# model = genai.GenerativeModel(
#     model_name="gemini-1.5-flash",
#     generation_config=generation_config
# )

# def generate_roadmap(core_category, category, course_name):
#     # Replace placeholders in the prompt
#     roadmap_prompt = prompt.replace("{core_category_title}", core_category)
#     roadmap_prompt = roadmap_prompt.replace("{category_title}", category)
#     roadmap_prompt = roadmap_prompt.replace("{userInput}", course_name)

#     print("roadmap_prompt", roadmap_prompt)
#     print("json_data_roadmap", json_data_roadmap)

#     # Start the chat session
#     chat_session = model.start_chat(
#         history=[{"role": "user", "parts": [roadmap_prompt]}]
#     )
    
#     # Send the message and get the response
#     response = chat_session.send_message("Generate a roadmap for " + course_name)

#     # Parse the response
#     try:
#         response_data = json.loads(response.text)
#         # Output the response for verification
#         print("Response:", response.text)
#         roadmap = response_data
#     except json.JSONDecodeError as e:
#         print(f"Failed to decode response as JSON: {e}")
#         return None

#     return roadmap
