# import asyncio
# import json
# from enhanced_app.services.enhanced_roadmap_service import create_enhanced_roadmap
# from enhanced_app.services.excel_service import read_excel_data
# from enhanced_app.services.enhanced_youtube_service import get_enhanced_videos_for_roadmap
# from enhanced_app.utils.logging_config import logger
# from pymongo import MongoClient

# async def main():
#     excel_file_path = r'C:\Users\parag\Desktop\learnVault\New Microsoft Excel Worksheet.xlsx'
    
#     excel_data = read_excel_data(excel_file_path)
#     if not excel_data:
#         logger.error("Failed to read Excel data")
#         return

#     course_name = "Python for Data Science"
#     category = "Data Science"
    
#     roadmap = await create_enhanced_roadmap(course_name, category, excel_data)
#     if not roadmap:
#         logger.error("Failed to generate roadmap")
#         return

#     print("Roadmap generated successfully. Fetching related videos...")

#     try:
#         videos = await get_enhanced_videos_for_roadmap(roadmap)
#         roadmap["videos"] = videos
        
#         # Count videos per subtopic
#         video_counts = {}
#         for video in videos:
#             key = f"{video['topic']} - {video['subtopic']}"
#             video_counts[key] = video_counts.get(key, 0) + 1
        
#         print("\nVideo counts per subtopic:")
#         for key, count in video_counts.items():
#             print(f"{key}: {count} videos")
        
#     except Exception as e:
#         logger.error(f"Error fetching videos: {e}")
#         roadmap["videos"] = []

#     # Save to MongoDB
#     client = MongoClient('mongodb://localhost:27017/')
#     db = client['learnvault']
#     collection = db['roadmaps']
    
#     # Insert or update the roadmap
#     result = collection.update_one(
#         {'course_name': roadmap['course_name']},
#         {'$set': roadmap},
#         upsert=True
#     )
    
#     print(f"\nRoadmap {'inserted' if result.upserted_id else 'updated'} in MongoDB")

#     # Save the complete roadmap with videos to a JSON file (optional)
#     with open('integrated_roadmap.json', 'w') as f:
#         json.dump(roadmap, f, indent=2)
#     print("\nComplete roadmap with videos saved to 'integrated_roadmap.json'")

# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
from enhanced_app.main import main
from enhanced_app.utils.logging_config import logger

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"An error occurred during roadmap generation and database storage: {e}")