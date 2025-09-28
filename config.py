import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'calorie_tracker_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

# App configuration
APP_CONFIG = {
    'title': 'Calorie Tracker Pro',
    'version': '2.0.0',
    'window_width': 1200,
    'window_height': 800,
    'min_width': 800,
    'min_height': 600
}

# UI Theme configuration
THEME_CONFIG = {
    'primary_color': '#2E86AB',
    'secondary_color': '#A23B72',
    'accent_color': '#F18F01',
    'background_color': '#F5F5F5',
    'text_color': '#2C3E50',
    'success_color': '#27AE60',
    'warning_color': '#F39C12',
    'error_color': '#E74C3C'
}
