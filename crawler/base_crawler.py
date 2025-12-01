"""Base crawler class for government data sources."""

import time
import requests
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os

from config import CrawlerConfig

class BaseCrawler(ABC):
    """Abstract base class for all data crawlers."""
    
    def __init__(self, source_name: str, config: Dict[str, Any]):
        self.source_name = source_name
        self.config = config
        self.crawler_config = CrawlerConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.crawler_config.USER_AGENT
        })
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"crawler.{source_name}")
        
        # Ensure data directories exist
        os.makedirs(self.crawler_config.RAW_DATA_DIR, exist_ok=True)
        os.makedirs(self.crawler_config.PROCESSED_DATA_DIR, exist_ok=True)
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make a rate-limited request with error handling."""
        
        # Rate limiting
        time.sleep(self.config.get('rate_limit', self.crawler_config.REQUEST_DELAY))
        
        for attempt in range(self.crawler_config.MAX_RETRIES):
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.crawler_config.TIMEOUT
                )
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.crawler_config.MAX_RETRIES - 1:
                    self.logger.error(f"Max retries exceeded for {url}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def _cache_data(self, data: Any, cache_key: str) -> None:
        """Cache data to local storage."""
        cache_file = os.path.join(
            self.crawler_config.RAW_DATA_DIR, 
            f"{self.source_name}_{cache_key}.json"
        )
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            self.logger.info(f"Cached data to {cache_file}")
        except Exception as e:
            self.logger.error(f"Failed to cache data: {e}")
    
    def _load_cached_data(self, cache_key: str) -> Optional[Any]:
        """Load data from cache if it exists and is not expired."""
        cache_file = os.path.join(
            self.crawler_config.RAW_DATA_DIR, 
            f"{self.source_name}_{cache_key}.json"
        )
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            expiry_time = cache_time + timedelta(hours=self.crawler_config.CACHE_EXPIRY_HOURS)
            
            if datetime.now() > expiry_time:
                self.logger.info(f"Cache expired for {cache_key}")
                return None
            
            self.logger.info(f"Loaded data from cache: {cache_key}")
            return cache_data['data']
            
        except Exception as e:
            self.logger.error(f"Failed to load cached data: {e}")
            return None
    
    @abstractmethod
    def search_datasets(self, query: str, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Search for datasets based on query and category."""
        pass
    
    @abstractmethod
    def get_dataset_metadata(self, dataset_id: str) -> Optional[Dict]:
        """Get detailed metadata for a specific dataset."""
        pass
    
    @abstractmethod
    def get_dataset_data(self, dataset_id: str, format: str = 'json') -> Optional[Any]:
        """Download the actual dataset data."""
        pass
    
    def get_available_categories(self) -> List[str]:
        """Get list of available data categories."""
        return []
    
    def health_check(self) -> bool:
        """Check if the data source is accessible."""
        try:
            response = self._make_request(self.config['base_url'])
            return response is not None and response.status_code == 200
        except:
            return False