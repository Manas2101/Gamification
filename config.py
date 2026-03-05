"""
Configuration file for API credentials and settings
Loads from .env file for security
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration - Separate tokens for TeamBook and DataSight
TEAMBOOK_BEARER_TOKEN = os.getenv('TEAMBOOK_BEARER_TOKEN', '')
DATASIGHT_BEARER_TOKEN = os.getenv('DATASIGHT_BEARER_TOKEN', '')

# Backward compatibility - if old BEARER_TOKEN exists, use it for both
BEARER_TOKEN = os.getenv('BEARER_TOKEN', '')
if BEARER_TOKEN and not TEAMBOOK_BEARER_TOKEN:
    TEAMBOOK_BEARER_TOKEN = BEARER_TOKEN
if BEARER_TOKEN and not DATASIGHT_BEARER_TOKEN:
    DATASIGHT_BEARER_TOKEN = BEARER_TOKEN

# Database Configuration
DB_PATH = os.getenv('DB_PATH', 'metrics.db')

# Service Line Configuration
SERVICE_LINE_ID = int(os.getenv('SERVICE_LINE_ID', '449'))

# Data Retention - Keep only last 5 weeks
MAX_WEEKS_TO_KEEP = int(os.getenv('MAX_WEEKS_TO_KEEP', '5'))

# Data Refresh Settings
AUTO_REFRESH_ENABLED = os.getenv('AUTO_REFRESH_ENABLED', 'false').lower() == 'true'
REFRESH_INTERVAL_HOURS = int(os.getenv('REFRESH_INTERVAL_HOURS', '168'))  # Weekly by default

# Default values
DEFAULT_WEEKS_HISTORY = 12
