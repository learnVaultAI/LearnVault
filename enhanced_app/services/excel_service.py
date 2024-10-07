import pandas as pd
from enhanced_app.utils.logging_config import logger

def read_excel_data(file_path):
    try:
        # Read the 'Development' sheet
        df = pd.read_excel(file_path, sheet_name='Development')
        
        # Process the data
        categories = {}
        current_category = None
        
        for _, row in df.iterrows():
            category = row['Category']
            course_name = row['Course Name']
            examples = row['Examples']
            
            if pd.notna(category):
                current_category = category
                categories[current_category] = []
            
            if pd.notna(course_name) and pd.notna(examples):
                course_data = {
                    'course_name': course_name,
                    'examples': [ex.strip() for ex in examples.split(',')]
                }
                categories[current_category].append(course_data)
        
        return categories
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        return None

def get_course_examples(course_name, excel_data):
    for category, courses in excel_data.items():
        for course in courses:
            if course['course_name'] == course_name:
                return course['examples']
    
    logger.warning(f"No specific examples found for course: {course_name}")
    return []
