"""Configuration settings for the government data crawler."""

import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class CrawlerConfig:
    """Configuration for web crawler behavior."""
    
    # Rate limiting
    REQUEST_DELAY: float = 1.0  # Seconds between requests
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    # User agent for requests
    USER_AGENT: str = "GovDataCrawler/1.0 (+https://github.com/yourusername/gov-data-crawler)"
    
    # Data storage
    DATA_DIR: str = "data"
    RAW_DATA_DIR: str = os.path.join(DATA_DIR, "raw")
    PROCESSED_DATA_DIR: str = os.path.join(DATA_DIR, "processed")
    
    # Cache settings
    CACHE_EXPIRY_HOURS: int = 24
    MAX_CACHE_SIZE_MB: int = 100

# Government data source configurations
GOV_DATA_SOURCES = {
    "data.gov": {
        "base_url": "https://catalog.data.gov",
        "api_url": "https://catalog.data.gov/api/3",
        "search_endpoint": "/action/package_search",
        "rate_limit": 1.0,  # seconds
        "max_results": 1000
    },
    "census.gov": {
        "base_url": "https://api.census.gov/data",
        "api_url": "https://api.census.gov/data",
        "rate_limit": 0.5,
        "max_results": 500
    },
    "taiwan_cwa": {
        "base_url": "https://opendata.cwa.gov.tw",
        "api_url": "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi",
        "api_key": "CWA-1FFDDAEC-161F-46A3-BE71-93C32C52829F",
        "rate_limit": 1.0,
        "max_results": 50
    }
}

# Streamlit app configuration
STREAMLIT_CONFIG = {
    "page_title": "Government Open Data Crawler",
    "page_icon": "🏛️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Data categories for filtering
DATA_CATEGORIES = [
    "Agriculture",
    "Climate",
    "Economics",
    "Education",
    "Energy",
    "Finance",
    "Health",
    "Housing",
    "Labor",
    "Law Enforcement",
    "Transportation",
    "Weather",
    "Weather Forecast",
    "Current Weather",
    "Marine Weather",
    "Air Quality",
    "Earthquake",
    "Other"
]