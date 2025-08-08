"""
Configuration file for Hugo Speaker Generator.

Contains field mappings, constants, and configuration settings.
"""

# Field mappings from Excel columns to output fields
SPEAKER_FIELD_MAPPING = {
    "title": "Speaker Name",
    "headline": "Speaker Headline",
    "linkedin": "Link to your LinkedIn profile",
    "bio": "Bio",
}

SESSION_FIELD_MAPPING = {
    "id": "Session_ID",
    "title": "Title of Session",
    "abstract": "Abstract of Session",
    "speakers": "Speaker Name",
    "duration": "Session Duration",
    "room": "Room",
    "agenda": "Agenda",
}

# Event date for session datetime generation
EVENT_DATE = "2025-09-25"

# Session level extraction mapping
LEVEL_EXTRACTION = {
    "100 (Beginner)": 1,
    "200 (Intermediate)": 2,
    "300 (Advanced)": 3,
    "400 (Expert)": 4,
    "500 (Principal)": 5,
}

# Duration mapping patterns
DURATION_PATTERNS = {"20": "30", "30": "30", "40": "60", "50": "60", "60": "60"}

# File paths and constants
DEFAULT_SPEAKER_IMAGE = "samples/unknown.jpg"
EXCEL_FILE_PATH = "data/responses+votes.xlsx"
OUTPUT_DIR = "generated_files"
MISSING_PHOTOS_CSV = "missing_photos.csv"
SESSION_ID_MAPPING_FILE = "data/session_id_mapping.json"

# Image processing settings
IMAGE_SIZE = (400, 400)  # Square image dimensions
IMAGE_QUALITY = 85
REQUEST_TIMEOUT = 10  # seconds

# LinkedIn Selenium Configuration
SELENIUM_USER_DATA_DIR = ".selenium"  # Directory for browser session data
LINKEDIN_REQUEST_DELAY = 2.5  # Delay between LinkedIn requests (seconds)

# Console output emojis
EMOJIS = {
    "rocket": "🚀",
    "chart": "📊",
    "people": "👥",
    "document": "📝",
    "image": "🖼️",
    "clipboard": "📋",
    "check": "✅",
    "warning": "⚠️",
    "folder": "📁",
    "bar_chart": "📈",
    "trash": "🗑️",
    "update": "🔄",
    "computer": "🖥️",
    "key": "🔐",
    "cross": "❌",
    "bulb": "💡",
    "globe": "🌐",
    "wrench": "🔧",
    "magnifier": "🔍",
    "party": "🎉",
    "hourglass": "⏳",
    "smile": "😊",
    "test": "🧪",
    "pencil": "✏️",
}
