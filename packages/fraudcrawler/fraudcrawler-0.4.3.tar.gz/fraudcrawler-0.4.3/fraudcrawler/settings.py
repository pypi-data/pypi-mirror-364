from pathlib import Path
from typing import List

# Generic settings
MAX_RETRIES = 3
RETRY_DELAY = 2
ROOT_DIR = Path(__file__).parents[1]

# Serp settings
GOOGLE_LOCATIONS_FILENAME = ROOT_DIR / "fraudcrawler" / "base" / "google-locations.json"
GOOGLE_LANGUAGES_FILENAME = ROOT_DIR / "fraudcrawler" / "base" / "google-languages.json"
SERP_DEFAULT_COUNTRY_CODES: List[str] = [
    # ".com",
]

# URL De-duplication settings
KNOWN_TRACKERS = [
    "srsltid",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "ar",
    "ps",
]

# Enrichment settings
ENRICHMENT_DEFAULT_LIMIT = 10

# Zyte settings
ZYTE_DEFALUT_PROBABILITY_THRESHOLD = 0.1

# Processor settings
PROCESSOR_DEFAULT_MODEL = "gpt-4o"
PROCESSOR_DEFAULT_IF_MISSING = -1
PROCESSOR_USER_PROMPT_TEMPLATE = "Product Details:\n{product_details}\n\nRelevance:"
PROCESSOR_PRODUCT_DETAILS_TEMPLATE = "{field_name}:\n{field_value}"

# Async settings
DEFAULT_N_SERP_WKRS = 10
DEFAULT_N_ZYTE_WKRS = 10
DEFAULT_N_PROC_WKRS = 10
