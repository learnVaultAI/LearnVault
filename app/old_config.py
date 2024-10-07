# app\config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class to manage application settings."""
    
    # API keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # MongoDB settings
    MONGODB_URI = os.getenv('MONGODB_URI')
    
    # Other settings
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
    
    @staticmethod
    def get(key, default=None):
        """Fetch configuration value with optional default."""
        return os.getenv(key, default)
