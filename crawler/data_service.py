"""
Data Service Layer - Integrates crawlers with database
Provides cached data access and intelligent data refresh
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import time

from database.db_manager import WeatherDBManager
from .taiwan_crawler import TWCrawler
from utils.taiwan_weather_helper import TaiwanWeatherProcessor

class WeatherDataService:
    """Service layer for weather data with database integration."""
    
    def __init__(self, crawlers: Dict, db_path: str = "data/weather_data.db"):
        """Initialize data service."""
        self.crawlers = crawlers
        self.db = WeatherDBManager(db_path)
        self.processor = TaiwanWeatherProcessor()
        self.logger = logging.getLogger(__name__)
        
        # Data refresh thresholds (in hours)
        self.refresh_thresholds = {
            'weather_forecasts': 3,    # Refresh every 3 hours
            'earthquakes': 1,          # Refresh every hour
            'weather_observations': 0.5 # Refresh every 30 minutes
        }
    
    def get_weather_forecast_data(self, force_refresh: bool = False) -> Tuple[pd.DataFrame, Dict]:
        """Get weather forecast data with smart caching."""
        
        # Check if we need to refresh data
        needs_refresh = self._needs_data_refresh('weather_forecasts', force_refresh)
        
        if needs_refresh:
            success = self._fetch_and_store_weather_data()
            if not success:
                self.logger.warning("Failed to fetch new weather data, using cached data")
        
        # Get data from database
        df = self.db.get_latest_weather_forecasts(hours_back=24)
        
        # Get metadata
        metadata = {
            'record_count': len(df),
            'last_update': self._get_last_update('weather_forecasts'),
            'data_age_hours': self._get_data_age('weather_forecasts'),
            'is_fresh': not needs_refresh,
            'source': 'Taiwan CWA API'
        }
        
        return df, metadata
    
    def get_earthquake_data(self, force_refresh: bool = False, 
                           days_back: int = 7, min_magnitude: float = 0.0) -> Tuple[pd.DataFrame, Dict]:
        """Get earthquake data with smart caching."""
        
        # Check if we need to refresh data
        needs_refresh = self._needs_data_refresh('earthquakes', force_refresh)
        
        if needs_refresh:
            success = self._fetch_and_store_earthquake_data()
            if not success:
                self.logger.warning("Failed to fetch new earthquake data, using cached data")
        
        # Get data from database
        df = self.db.get_recent_earthquakes(days_back=days_back, min_magnitude=min_magnitude)
        
        # Get metadata
        metadata = {
            'record_count': len(df),
            'last_update': self._get_last_update('earthquakes'),
            'data_age_hours': self._get_data_age('earthquakes'),
            'is_fresh': not needs_refresh,
            'source': 'Taiwan CWA API',
            'filters': {
                'days_back': days_back,
                'min_magnitude': min_magnitude
            }
        }
        
        return df, metadata
    
    def _needs_data_refresh(self, data_type: str, force_refresh: bool = False) -> bool:
        """Check if data needs to be refreshed."""
        if force_refresh:
            return True
        
        freshness_info = self.db.get_data_freshness_info()
        
        if data_type not in freshness_info:
            return True  # No data exists
        
        data_info = freshness_info[data_type]
        age_hours = data_info['age_hours']
        threshold = self.refresh_thresholds.get(data_type, 6)  # Default 6 hours
        
        return age_hours > threshold
    
    def _fetch_and_store_weather_data(self) -> bool:
        """Fetch weather data from API and store in database."""
        if 'taiwan_cwa' not in self.crawlers:
            self.logger.error("Taiwan CWA crawler not available")
            return False
        
        crawler = self.crawlers['taiwan_cwa']
        start_time = time.time()
        
        try:
            self.logger.info("Fetching weather forecast data from Taiwan CWA API...")
            
            # Fetch raw data
            raw_data = crawler.get_dataset_data("F-A0010-001")
            response_time = time.time() - start_time
            
            if not raw_data:
                self.db.log_api_call("F-A0010-001", "taiwan_cwa", False, response_time, 0, "No data returned")
                return False
            
            # Process data
            df = self.processor.process_weather_forecast(raw_data)
            
            if df is None or df.empty:
                self.db.log_api_call("F-A0010-001", "taiwan_cwa", False, response_time, 0, "Data processing failed")
                return False
            
            # Store in database
            records_saved = self.db.save_weather_forecast(df)
            
            # Log successful API call
            self.db.log_api_call("F-A0010-001", "taiwan_cwa", True, response_time, records_saved)
            
            self.logger.info(f"Successfully stored {records_saved} weather forecast records")
            return True
            
        except Exception as e:
            response_time = time.time() - start_time
            self.db.log_api_call("F-A0010-001", "taiwan_cwa", False, response_time, 0, str(e))
            self.logger.error(f"Failed to fetch weather data: {e}")
            return False
    
    def _fetch_and_store_earthquake_data(self) -> bool:
        """Fetch earthquake data from API and store in database."""
        if 'taiwan_cwa' not in self.crawlers:
            self.logger.error("Taiwan CWA crawler not available")
            return False
        
        crawler = self.crawlers['taiwan_cwa']
        start_time = time.time()
        
        try:
            self.logger.info("Fetching earthquake data from Taiwan CWA API...")
            
            # Fetch raw data
            raw_data = crawler.get_dataset_data("E-A0015-001")
            response_time = time.time() - start_time
            
            if not raw_data:
                self.db.log_api_call("E-A0015-001", "taiwan_cwa", False, response_time, 0, "No data returned")
                return False
            
            # Process data
            df = self.processor.process_earthquake_data(raw_data)
            
            if df is None or df.empty:
                self.db.log_api_call("E-A0015-001", "taiwan_cwa", False, response_time, 0, "Data processing failed")
                return False
            
            # Store in database
            records_saved = self.db.save_earthquake_data(df)
            
            # Log successful API call
            self.db.log_api_call("E-A0015-001", "taiwan_cwa", True, response_time, records_saved)
            
            self.logger.info(f"Successfully stored {records_saved} earthquake records")
            return True
            
        except Exception as e:
            response_time = time.time() - start_time
            self.db.log_api_call("E-A0015-001", "taiwan_cwa", False, response_time, 0, str(e))
            self.logger.error(f"Failed to fetch earthquake data: {e}")
            return False
    
    def _get_last_update(self, data_type: str) -> Optional[str]:
        """Get last update time for data type."""
        freshness_info = self.db.get_data_freshness_info()
        return freshness_info.get(data_type, {}).get('last_update')
    
    def _get_data_age(self, data_type: str) -> float:
        """Get data age in hours."""
        freshness_info = self.db.get_data_freshness_info()
        return freshness_info.get(data_type, {}).get('age_hours', float('inf'))
    
    def get_database_status(self) -> Dict:
        """Get comprehensive database status information."""
        try:
            # Get basic database stats
            db_stats = self.db.get_database_stats()
            
            # Get data freshness info
            freshness_info = self.db.get_data_freshness_info()
            
            # Calculate overall health score
            health_score = self._calculate_health_score(freshness_info, db_stats)
            
            status = {
                'database_stats': db_stats,
                'data_freshness': freshness_info,
                'health_score': health_score,
                'recommendations': self._get_recommendations(freshness_info),
                'last_checked': datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get database status: {e}")
            return {
                'error': str(e),
                'last_checked': datetime.now().isoformat()
            }
    
    def _calculate_health_score(self, freshness_info: Dict, db_stats: Dict) -> float:
        """Calculate overall system health score (0-100)."""
        score = 100.0
        
        # Deduct points for old data
        for data_type, info in freshness_info.items():
            age_hours = info.get('age_hours', 0)
            threshold = self.refresh_thresholds.get(data_type, 6)
            
            if age_hours > threshold * 2:  # Very old data
                score -= 20
            elif age_hours > threshold:     # Somewhat old data
                score -= 10
        
        # Deduct points for API failures
        api_success_rate = db_stats.get('api_success_rate', 100)
        if api_success_rate < 80:
            score -= (100 - api_success_rate) / 2
        
        # Deduct points for large database size (performance impact)
        db_size_mb = db_stats.get('db_size_mb', 0)
        if db_size_mb > 100:  # > 100MB
            score -= min(20, (db_size_mb - 100) / 10)
        
        return max(0.0, min(100.0, score))
    
    def _get_recommendations(self, freshness_info: Dict) -> List[str]:
        """Get recommendations for improving data quality."""
        recommendations = []
        
        for data_type, info in freshness_info.items():
            age_hours = info.get('age_hours', 0)
            threshold = self.refresh_thresholds.get(data_type, 6)
            
            if age_hours > threshold * 3:
                recommendations.append(f"⚠️ {data_type} data is very old ({age_hours:.1f}h), consider refreshing")
            elif age_hours > threshold * 2:
                recommendations.append(f"📋 {data_type} data should be refreshed soon ({age_hours:.1f}h)")
        
        if not recommendations:
            recommendations.append("✅ All data is fresh and up to date")
        
        return recommendations
    
    def force_refresh_all_data(self) -> Dict[str, bool]:
        """Force refresh all data types."""
        results = {}
        
        self.logger.info("Force refreshing all data...")
        
        # Refresh weather data
        results['weather_forecasts'] = self._fetch_and_store_weather_data()
        
        # Refresh earthquake data
        results['earthquakes'] = self._fetch_and_store_earthquake_data()
        
        return results
    
    def export_all_data(self, export_dir: str = "data/exports") -> Dict[str, str]:
        """Export all data to CSV files."""
        import os
        
        os.makedirs(export_dir, exist_ok=True)
        
        exports = {}
        tables = ['weather_forecasts', 'earthquakes', 'weather_observations', 'api_logs']
        
        for table in tables:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{table}_{timestamp}.csv"
            filepath = os.path.join(export_dir, filename)
            
            if self.db.export_data_to_csv(table, filepath):
                exports[table] = filepath
            else:
                exports[table] = f"Failed to export {table}"
        
        return exports
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to manage database size."""
        self.logger.info(f"Cleaning up data older than {days_to_keep} days...")
        self.db.cleanup_old_data(days_to_keep)
    
    def test_api_connectivity(self) -> Dict[str, Any]:
        """Test API connectivity for all crawlers."""
        results = {}
        
        for name, crawler in self.crawlers.items():
            try:
                start_time = time.time()
                is_healthy = crawler.health_check()
                response_time = time.time() - start_time
                
                results[name] = {
                    'status': 'online' if is_healthy else 'offline',
                    'response_time': response_time,
                    'last_tested': datetime.now().isoformat()
                }
                
            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'error': str(e),
                    'last_tested': datetime.now().isoformat()
                }
        
        return results