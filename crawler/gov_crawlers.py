"""Specific crawler implementations for government data sources."""

from typing import Dict, List, Optional, Any
import json
from urllib.parse import urljoin

from .base_crawler import BaseCrawler

class DataGovCrawler(BaseCrawler):
    """Crawler for data.gov datasets."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("data_gov", config)
    
    def search_datasets(self, query: str, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Search for datasets on data.gov."""
        cache_key = f"search_{hash(query + str(category) + str(limit))}"
        
        # Try to load from cache first
        cached_data = self._load_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        search_url = urljoin(self.config['api_url'], self.config['search_endpoint'])
        params = {
            'q': query,
            'rows': min(limit, self.config.get('max_results', 1000)),
            'sort': 'score desc, metadata_modified desc'
        }
        
        if category:
            params['fq'] = f'groups:{category.lower()}'
        
        response = self._make_request(search_url, params)
        if not response:
            return []
        
        try:
            data = response.json()
            results = []
            
            for item in data.get('result', {}).get('results', []):
                dataset = {
                    'id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'description': item.get('notes', ''),
                    'organization': item.get('organization', {}).get('title', ''),
                    'tags': [tag.get('name', '') for tag in item.get('tags', [])],
                    'last_modified': item.get('metadata_modified', ''),
                    'resources': len(item.get('resources', [])),
                    'url': f"https://catalog.data.gov/dataset/{item.get('name', '')}",
                    'source': 'data.gov'
                }
                results.append(dataset)
            
            # Cache the results
            self._cache_data(results, cache_key)
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to parse search results: {e}")
            return []
    
    def get_dataset_metadata(self, dataset_id: str) -> Optional[Dict]:
        """Get detailed metadata for a specific dataset."""
        cache_key = f"metadata_{dataset_id}"
        
        # Try to load from cache first
        cached_data = self._load_cached_data(cache_key)
        if cached_data:
            return cached_data
        
        metadata_url = f"{self.config['api_url']}/action/package_show"
        params = {'id': dataset_id}
        
        response = self._make_request(metadata_url, params)
        if not response:
            return None
        
        try:
            data = response.json()
            if data.get('success'):
                result = data['result']
                metadata = {
                    'id': result.get('id'),
                    'title': result.get('title'),
                    'description': result.get('notes'),
                    'organization': result.get('organization', {}).get('title'),
                    'tags': [tag.get('name') for tag in result.get('tags', [])],
                    'license': result.get('license_title'),
                    'created': result.get('metadata_created'),
                    'modified': result.get('metadata_modified'),
                    'resources': []
                }
                
                # Process resources (downloadable files)
                for resource in result.get('resources', []):
                    metadata['resources'].append({
                        'id': resource.get('id'),
                        'name': resource.get('name'),
                        'format': resource.get('format'),
                        'url': resource.get('url'),
                        'size': resource.get('size'),
                        'description': resource.get('description')
                    })
                
                # Cache the metadata
                self._cache_data(metadata, cache_key)
                return metadata
                
        except Exception as e:
            self.logger.error(f"Failed to get dataset metadata: {e}")
            
        return None
    
    def get_dataset_data(self, dataset_id: str, format: str = 'json') -> Optional[Any]:
        """Download dataset data."""
        metadata = self.get_dataset_metadata(dataset_id)
        if not metadata:
            return None
        
        # Find resource with requested format
        resource_url = None
        for resource in metadata.get('resources', []):
            if resource.get('format', '').lower() == format.lower():
                resource_url = resource.get('url')
                break
        
        if not resource_url:
            # If exact format not found, try to get the first available resource
            if metadata.get('resources'):
                resource_url = metadata['resources'][0].get('url')
        
        if not resource_url:
            return None
        
        response = self._make_request(resource_url)
        if not response:
            return None
        
        try:
            if format.lower() == 'json':
                return response.json()
            else:
                return response.text
        except:
            return response.content
    
    def get_available_categories(self) -> List[str]:
        """Get available categories from data.gov."""
        categories_url = f"{self.config['api_url']}/action/group_list"
        
        response = self._make_request(categories_url)
        if not response:
            return []
        
        try:
            data = response.json()
            if data.get('success'):
                return data.get('result', [])
        except Exception as e:
            self.logger.error(f"Failed to get categories: {e}")
        
        return []

class CensusCrawler(BaseCrawler):
    """Crawler for US Census data."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("census", config)
    
    def search_datasets(self, query: str, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Search for Census datasets."""
        cache_key = f"census_search_{hash(query + str(category))}"
        
        # Try to load from cache first
        cached_data = self._load_cached_data(cache_key)
        if cached_data:
            return cached_data[:limit]
        
        # Get available datasets
        datasets_url = f"{self.config['api_url']}.json"
        response = self._make_request(datasets_url)
        
        if not response:
            return []
        
        try:
            data = response.json()
            results = []
            
            for year, datasets in data.get('dataset', {}).items():
                for dataset_name, dataset_info in datasets.items():
                    if query.lower() in dataset_name.lower() or query.lower() in str(dataset_info).lower():
                        dataset = {
                            'id': f"{year}_{dataset_name}",
                            'title': dataset_info.get('title', dataset_name),
                            'description': dataset_info.get('description', ''),
                            'organization': 'U.S. Census Bureau',
                            'tags': [year, 'census'],
                            'last_modified': '',
                            'resources': 1,
                            'url': f"https://api.census.gov/data/{year}/{dataset_name}",
                            'source': 'census.gov'
                        }
                        results.append(dataset)
            
            # Cache the results
            self._cache_data(results, cache_key)
            return results[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to search Census datasets: {e}")
            return []
    
    def get_dataset_metadata(self, dataset_id: str) -> Optional[Dict]:
        """Get Census dataset metadata."""
        try:
            year, dataset_name = dataset_id.split('_', 1)
            metadata_url = f"{self.config['api_url']}/{year}/{dataset_name}.json"
            
            response = self._make_request(metadata_url)
            if not response:
                return None
            
            data = response.json()
            return {
                'id': dataset_id,
                'title': data.get('title', dataset_name),
                'description': data.get('description', ''),
                'organization': 'U.S. Census Bureau',
                'variables': len(data.get('variables', {})),
                'geography': data.get('geography', {}),
                'url': f"https://api.census.gov/data/{year}/{dataset_name}"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get Census metadata: {e}")
            return None
    
    def get_dataset_data(self, dataset_id: str, format: str = 'json') -> Optional[Any]:
        """Get sample Census data."""
        # For Census API, we'll get a small sample of data
        try:
            year, dataset_name = dataset_id.split('_', 1)
            data_url = f"{self.config['api_url']}/{year}/{dataset_name}"
            
            # Get basic population data as example
            params = {
                'get': 'NAME,POP',
                'for': 'state:*',
                'key': 'YOUR_API_KEY'  # Users would need to add their own key
            }
            
            response = self._make_request(data_url, params)
            if response:
                return response.json()
            
        except Exception as e:
            self.logger.error(f"Failed to get Census data: {e}")
        
        return None
    
    def get_available_categories(self) -> List[str]:
        """Get available Census data categories."""
        return [
            "Population", "Housing", "Economics", "Demographics", 
            "Employment", "Income", "Education", "Health"
        ]