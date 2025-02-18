import logging
from datetime import datetime

# Selenium configuration
SELENIUM_CONFIG = {
    'page_load_timeout': 30,  # seconds
    'implicit_wait': 10,  # seconds
}

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# URL patterns for partner program detection
PARTNER_KEYWORDS = [
    'partner', 'partners', 'partnership', 'affiliate', 'affiliates',
    'reseller', 'resellers', 'channel-partners', 'solution-partners',
    'technology-partners', 'strategic-partners'
]

# Patterns to identify partner names in text
PARTNER_NAME_PATTERNS = [
    'partner:', 'partners:', 'including', 'such as', 'featured',
    'spotlight', 'certified', 'premier', 'preferred', 'gold',
    'silver', 'platinum', 'trusted'
]

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = f'scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

# Output configuration
OUTPUT_FILE = f'partner_programs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
CSV_HEADERS = [
    'domain',
    'partner_program_url',
    'url_path',
    'program_types',
    'partner_names',
    'page_structure',
    'status',
    'timestamp',
    'subpages'
]
