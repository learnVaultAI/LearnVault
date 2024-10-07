import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CourseMonitor:
    def __init__(self, file_path='course_progress.json'):
        self.file_path = file_path
        self.progress = self.load_progress()

    def load_progress(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    content = f.read()
                    if content.strip():  # Check if file is not empty
                        return json.loads(content)
                    else:
                        logger.warning(f"Empty progress file: {self.file_path}")
                        return {}
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from {self.file_path}: {str(e)}")
                logger.info("Creating a new progress file")
                return {}
        else:
            logger.info(f"Progress file not found: {self.file_path}")
            return {}

    def save_progress(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.progress, f)

    def mark_stage_complete(self, course_name, stage):
        if course_name not in self.progress:
            self.progress[course_name] = {}
        self.progress[course_name][stage] = {
            'status': 'complete',
            'timestamp': datetime.now().isoformat(),
            'version': self.progress[course_name].get(stage, {}).get('version', 0) + 1
        }
        self.save_progress()

    def mark_stage_partial(self, course_name, stage, completion_percentage):
        if course_name not in self.progress:
            self.progress[course_name] = {}
        self.progress[course_name][stage] = {
            'status': 'partial',
            'completion_percentage': completion_percentage,
            'timestamp': datetime.now().isoformat(),
            'version': self.progress[course_name].get(stage, {}).get('version', 0) + 1
        }
        self.save_progress()

    def is_stage_complete(self, course_name, stage):
        return self.progress.get(course_name, {}).get(stage, {}).get('status') == 'complete'

    def get_stage_completion(self, course_name, stage):
        stage_info = self.progress.get(course_name, {}).get(stage, {})
        if stage_info.get('status') == 'complete':
            return 100
        return stage_info.get('completion_percentage', 0)

    def is_course_complete(self, course_name):
        return all(stage.get('status') == 'complete' for stage in self.progress.get(course_name, {}).values())

    def remove_course(self, course_name):
        if course_name in self.progress:
            del self.progress[course_name]
            self.save_progress()

    def log_error(self, course_name, stage, error_message):
        if course_name not in self.progress:
            self.progress[course_name] = {}
        if 'errors' not in self.progress[course_name]:
            self.progress[course_name]['errors'] = []
        self.progress[course_name]['errors'].append({
            'stage': stage,
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        })
        self.save_progress()

    def get_stage_version(self, course_name, stage):
        return self.progress.get(course_name, {}).get(stage, {}).get('version', 0)

    def get_course_completion_status(self, course_name):
        course_progress = self.progress.get(course_name, {})
        
        if isinstance(course_progress, list):
            logger.warning(f"Course progress for {course_name} is a list instead of a dictionary. Returning incomplete status.")
            return {
                'is_complete': False,
                'completed_stages': [],
                'incomplete_stages': ['unknown']
            }

        completed_stages = [stage for stage, data in course_progress.items() if isinstance(data, dict) and data.get('status') == 'complete']
        incomplete_stages = [stage for stage, data in course_progress.items() if isinstance(data, dict) and data.get('status') != 'complete']
        is_complete = len(incomplete_stages) == 0 and len(completed_stages) > 0

        return {
            'is_complete': is_complete,
            'completed_stages': completed_stages,
            'incomplete_stages': incomplete_stages
        }

course_monitor = CourseMonitor()
