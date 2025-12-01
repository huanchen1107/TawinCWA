"""Taiwan Central Weather Administration (CWA) data crawler."""

from typing import Dict, List, Optional, Any
import json
from urllib.parse import urljoin
from datetime import datetime

from .base_crawler import BaseCrawler

class TWCrawler(BaseCrawler):
    """Crawler for Taiwan Central Weather Administration open data."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("taiwan_cwa", config)
        self.api_key = config.get('api_key', '')
        self.base_endpoints = {
            # Weather forecasts
            'F-A0010-001': 'Weather forecast for Taiwan 36 hours',
            'F-C0032-001': 'General weather forecast',
            'F-D0047-089': 'Weather forecast for all townships',
            
            # Current conditions
            'O-A0003-001': 'Automatic weather station data',
            'O-A0001-001': 'Current weather observation',
            
            # Marine data
            'F-A0012-001': 'Marine weather forecast',
            'O-A0018-001': 'Ocean buoy data',
            
            # Air quality (if available)
            'F-A0086-001': 'Air quality forecast',
            
            # Earthquake
            'E-A0015-001': 'Earthquake report',
            'E-A0016-001': 'Small earthquake report'
        }
    
    def search_datasets(self, query: str, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Search for Taiwan CWA datasets."""
        cache_key = f"tw_search_{hash(query + str(category))}"
        
        # Try to load from cache first
        cached_data = self._load_cached_data(cache_key)
        if cached_data:
            return cached_data[:limit]
        
        results = []
        query_lower = query.lower()
        
        # Filter endpoints based on query
        for endpoint_id, description in self.base_endpoints.items():
            if (query_lower in description.lower() or 
                query_lower in endpoint_id.lower()):
                
                dataset = {
                    'id': endpoint_id,
                    'title': description,
                    'description': f'Taiwan CWA data: {description}',
                    'organization': 'Central Weather Administration, Taiwan',
                    'tags': self._get_tags_for_endpoint(endpoint_id),
                    'last_modified': datetime.now().isoformat(),
                    'resources': 1,
                    'url': f"https://opendata.cwa.gov.tw/dataset/{endpoint_id.lower()}",
                    'source': 'taiwan_cwa',
                    'api_endpoint': endpoint_id,
                    'category': self._get_category_for_endpoint(endpoint_id)
                }
                
                if category is None or dataset['category'].lower() == category.lower():
                    results.append(dataset)
        
        # Cache the results
        self._cache_data(results, cache_key)
        return results[:limit]
    
    def get_dataset_metadata(self, dataset_id: str) -> Optional[Dict]:
        """Get detailed metadata for a specific Taiwan CWA dataset."""
        cache_key = f"tw_metadata_{dataset_id}"
        
        # Try to load from cache first
        cached_data = self._load_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        if dataset_id not in self.base_endpoints:
            return None
        
        # Test API endpoint to get structure
        sample_data = self._fetch_cwa_data(dataset_id, sample_only=True)
        
        metadata = {
            'id': dataset_id,
            'title': self.base_endpoints[dataset_id],
            'description': f'Taiwan Central Weather Administration data: {self.base_endpoints[dataset_id]}',
            'organization': 'Central Weather Administration, Taiwan',
            'license': 'Open Government Data License',
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'category': self._get_category_for_endpoint(dataset_id),
            'tags': self._get_tags_for_endpoint(dataset_id),
            'api_endpoint': dataset_id,
            'data_format': 'JSON',
            'update_frequency': self._get_update_frequency(dataset_id),
            'coverage': 'Taiwan',
            'resources': [{
                'id': f"{dataset_id}_json",
                'name': f"{dataset_id} JSON Data",
                'format': 'JSON',
                'url': self._build_api_url(dataset_id),
                'description': f'Real-time {self.base_endpoints[dataset_id]} data in JSON format'
            }]
        }
        
        # Add sample data structure if available
        if sample_data:
            metadata['sample_structure'] = self._analyze_data_structure(sample_data)
        
        # Cache the metadata
        self._cache_data(metadata, cache_key)
        return metadata
    
    def get_dataset_data(self, dataset_id: str, format: str = 'json') -> Optional[Any]:
        """Download Taiwan CWA dataset data."""
        return self._fetch_cwa_data(dataset_id)
    
    def _fetch_cwa_data(self, endpoint_id: str, sample_only: bool = False) -> Optional[Dict]:
        """Fetch data from Taiwan CWA API."""
        url = self._build_api_url(endpoint_id)
        
        try:
            response = self._make_request(url)
            if not response:
                return None
            
            data = response.json()
            
            if sample_only:
                # Return only a small sample for metadata analysis
                if isinstance(data, dict):
                    sample = {}
                    for key, value in list(data.items())[:5]:
                        if isinstance(value, list) and len(value) > 0:
                            sample[key] = value[:2]  # First 2 items
                        else:
                            sample[key] = value
                    return sample
                elif isinstance(data, list):
                    return data[:5]  # First 5 items
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to fetch CWA data for {endpoint_id}: {e}")
            return None
    
    def _build_api_url(self, endpoint_id: str) -> str:
        """Build API URL for given endpoint."""
        base_url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi"
        return f"{base_url}/{endpoint_id}?Authorization={self.api_key}&downloadType=WEB&format=JSON"
    
    def _get_category_for_endpoint(self, endpoint_id: str) -> str:
        """Get category based on endpoint ID."""
        if endpoint_id.startswith('F-A') or endpoint_id.startswith('F-C') or endpoint_id.startswith('F-D'):
            return 'Weather Forecast'
        elif endpoint_id.startswith('O-A'):
            return 'Current Weather'
        elif endpoint_id.startswith('E-A'):
            return 'Earthquake'
        elif 'marine' in endpoint_id.lower() or endpoint_id.startswith('F-A0012'):
            return 'Marine Weather'
        elif 'air' in endpoint_id.lower():
            return 'Air Quality'
        else:
            return 'Weather'
    
    def _get_tags_for_endpoint(self, endpoint_id: str) -> List[str]:
        """Get relevant tags for endpoint."""
        tags = ['taiwan', 'weather', 'cwa']
        
        if 'forecast' in self.base_endpoints.get(endpoint_id, '').lower():
            tags.append('forecast')
        if 'current' in self.base_endpoints.get(endpoint_id, '').lower():
            tags.append('real-time')
        if 'marine' in self.base_endpoints.get(endpoint_id, '').lower():
            tags.extend(['marine', 'ocean'])
        if 'earthquake' in self.base_endpoints.get(endpoint_id, '').lower():
            tags.append('earthquake')
        if 'air' in self.base_endpoints.get(endpoint_id, '').lower():
            tags.extend(['air-quality', 'pollution'])
        
        return tags
    
    def _get_update_frequency(self, endpoint_id: str) -> str:
        """Get update frequency for endpoint."""
        if endpoint_id.startswith('F-'):  # Forecasts
            return 'Every 6 hours'
        elif endpoint_id.startswith('O-'):  # Observations
            return 'Every 10 minutes'
        elif endpoint_id.startswith('E-'):  # Earthquakes
            return 'As needed'
        else:
            return 'Varies'
    
    def _analyze_data_structure(self, data: Dict) -> Dict[str, Any]:
        """Analyze the structure of sample data."""
        def analyze_value(value, max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return str(type(value).__name__)
            
            if isinstance(value, dict):
                return {k: analyze_value(v, max_depth, current_depth + 1) 
                       for k, v in list(value.items())[:5]}
            elif isinstance(value, list) and len(value) > 0:
                return [analyze_value(value[0], max_depth, current_depth + 1)]
            else:
                return str(type(value).__name__)
        
        return analyze_value(data)
    
    def get_available_categories(self) -> List[str]:
        """Get available categories from Taiwan CWA."""
        categories = set()
        for endpoint_id in self.base_endpoints.keys():
            categories.add(self._get_category_for_endpoint(endpoint_id))
        return list(categories)
    
    def health_check(self) -> bool:
        """Check if the Taiwan CWA API is accessible."""
        try:
            # Test with a simple endpoint
            test_endpoint = 'F-A0010-001'  # Weather forecast
            url = self._build_api_url(test_endpoint)
            response = self._make_request(url)
            
            if response and response.status_code == 200:
                # Try to parse JSON
                data = response.json()
                return isinstance(data, (dict, list))
            
            return False
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False