"""
SQLite Database Manager for Taiwan Weather Dashboard
Stores weather data, earthquake data, and API responses
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import os

class WeatherDBManager:
    """Manages SQLite database for weather and earthquake data."""
    
    def __init__(self, db_path: str = "data/weather_data.db"):
        """Initialize database manager."""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Weather forecast data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weather_forecasts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        location TEXT NOT NULL,
                        forecast_time TEXT NOT NULL,
                        temperature REAL,
                        temperature_unit TEXT,
                        weather_condition TEXT,
                        rain_probability REAL,
                        humidity REAL,
                        wind_speed REAL,
                        wind_direction TEXT,
                        start_time TEXT,
                        end_time TEXT,
                        raw_data TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(location, forecast_time, start_time)
                    )
                """)
                
                # Earthquake data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS earthquakes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        earthquake_no TEXT UNIQUE,
                        origin_time TEXT NOT NULL,
                        magnitude_value REAL,
                        magnitude_type TEXT,
                        depth REAL,
                        location TEXT,
                        epicenter_lat REAL,
                        epicenter_lon REAL,
                        report_type TEXT,
                        report_content TEXT,
                        web_url TEXT,
                        raw_data TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Current weather observations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weather_observations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        station_name TEXT NOT NULL,
                        station_id TEXT,
                        observation_time TEXT NOT NULL,
                        temperature REAL,
                        humidity REAL,
                        pressure REAL,
                        wind_speed REAL,
                        wind_direction TEXT,
                        visibility REAL,
                        latitude REAL,
                        longitude REAL,
                        raw_data TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(station_id, observation_time)
                    )
                """)
                
                # API call logs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        endpoint TEXT NOT NULL,
                        api_source TEXT NOT NULL,
                        success BOOLEAN NOT NULL,
                        response_size INTEGER,
                        response_time REAL,
                        error_message TEXT,
                        records_processed INTEGER,
                        called_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Data freshness tracking
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS data_freshness (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_type TEXT NOT NULL,
                        last_update TEXT NOT NULL,
                        record_count INTEGER,
                        data_quality_score REAL,
                        UNIQUE(data_type)
                    )
                """)
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def save_weather_forecast(self, forecast_data: pd.DataFrame) -> int:
        """Save weather forecast data to database."""
        if forecast_data is None or forecast_data.empty:
            return 0
        
        records_saved = 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for _, row in forecast_data.iterrows():
                    # Extract weather parameters
                    location = row.get('location', '')
                    
                    # Get temperature
                    temp_cols = [col for col in forecast_data.columns if 'T_' in col and 'value' in col]
                    temperature = None
                    temp_unit = None
                    if temp_cols:
                        temp_val = row.get(temp_cols[0])
                        if temp_val and str(temp_val).replace('.', '').isdigit():
                            temperature = float(temp_val)
                            temp_unit = row.get(temp_cols[0].replace('value', 'unit'), '°C')
                    
                    # Get weather condition
                    wx_cols = [col for col in forecast_data.columns if 'Wx_' in col and 'name' in col]
                    weather_condition = row.get(wx_cols[0], '') if wx_cols else None
                    
                    # Get rain probability
                    pop_cols = [col for col in forecast_data.columns if 'PoP_' in col and 'value' in col]
                    rain_prob = None
                    if pop_cols:
                        pop_val = row.get(pop_cols[0])
                        if pop_val and str(pop_val).replace('.', '').isdigit():
                            rain_prob = float(pop_val)
                    
                    # Get humidity
                    rh_cols = [col for col in forecast_data.columns if 'RH_' in col and 'value' in col]
                    humidity = None
                    if rh_cols:
                        rh_val = row.get(rh_cols[0])
                        if rh_val and str(rh_val).replace('.', '').isdigit():
                            humidity = float(rh_val)
                    
                    # Get wind data
                    wind_cols = [col for col in forecast_data.columns if 'WS_' in col and 'value' in col]
                    wind_speed = None
                    if wind_cols:
                        wind_val = row.get(wind_cols[0])
                        if wind_val and str(wind_val).replace('.', '').isdigit():
                            wind_speed = float(wind_val)
                    
                    # Get time information
                    start_time = None
                    end_time = None
                    for col in forecast_data.columns:
                        if col.endswith('_start'):
                            start_time = row.get(col)
                            break
                    for col in forecast_data.columns:
                        if col.endswith('_end'):
                            end_time = row.get(col)
                            break
                    
                    # Insert or update record
                    cursor.execute("""
                        INSERT OR REPLACE INTO weather_forecasts 
                        (location, forecast_time, temperature, temperature_unit, 
                         weather_condition, rain_probability, humidity, wind_speed,
                         start_time, end_time, raw_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        location,
                        datetime.now().isoformat(),
                        temperature,
                        temp_unit,
                        weather_condition,
                        rain_prob,
                        humidity,
                        wind_speed,
                        start_time,
                        end_time,
                        json.dumps(row.to_dict(), ensure_ascii=False)
                    ))
                    
                    records_saved += 1
                
                conn.commit()
                
                # Update data freshness
                self._update_data_freshness('weather_forecasts', records_saved)
                
                self.logger.info(f"Saved {records_saved} weather forecast records")
                
        except Exception as e:
            self.logger.error(f"Failed to save weather forecast data: {e}")
            
        return records_saved
    
    def save_earthquake_data(self, earthquake_data: pd.DataFrame) -> int:
        """Save earthquake data to database."""
        if earthquake_data is None or earthquake_data.empty:
            return 0
        
        records_saved = 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for _, row in earthquake_data.iterrows():
                    # Extract earthquake information
                    eq_no = row.get('earthquake_no', '')
                    origin_time = row.get('origin_time', '')
                    magnitude = row.get('magnitude_value')
                    magnitude_type = row.get('magnitude_type', '')
                    depth = row.get('depth')
                    location = row.get('location', '')
                    lat = row.get('epicenter_lat')
                    lon = row.get('epicenter_lon')
                    report_type = row.get('report_type', '')
                    report_content = row.get('report_content', '')
                    web_url = row.get('web_url', '')
                    
                    # Convert numeric values
                    try:
                        magnitude = float(magnitude) if magnitude else None
                    except:
                        magnitude = None
                    
                    try:
                        depth = float(depth) if depth else None
                    except:
                        depth = None
                    
                    try:
                        lat = float(lat) if lat else None
                    except:
                        lat = None
                    
                    try:
                        lon = float(lon) if lon else None
                    except:
                        lon = None
                    
                    # Insert or update record
                    cursor.execute("""
                        INSERT OR REPLACE INTO earthquakes 
                        (earthquake_no, origin_time, magnitude_value, magnitude_type,
                         depth, location, epicenter_lat, epicenter_lon, 
                         report_type, report_content, web_url, raw_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        eq_no,
                        origin_time,
                        magnitude,
                        magnitude_type,
                        depth,
                        location,
                        lat,
                        lon,
                        report_type,
                        report_content,
                        web_url,
                        json.dumps(row.to_dict(), ensure_ascii=False)
                    ))
                    
                    records_saved += 1
                
                conn.commit()
                
                # Update data freshness
                self._update_data_freshness('earthquakes', records_saved)
                
                self.logger.info(f"Saved {records_saved} earthquake records")
                
        except Exception as e:
            self.logger.error(f"Failed to save earthquake data: {e}")
            
        return records_saved
    
    def get_latest_weather_forecasts(self, hours_back: int = 6) -> pd.DataFrame:
        """Get latest weather forecast data from database."""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours_back)).isoformat()
            
            query = """
                SELECT location, forecast_time, temperature, temperature_unit,
                       weather_condition, rain_probability, humidity, wind_speed,
                       start_time, end_time, created_at
                FROM weather_forecasts 
                WHERE created_at > ?
                ORDER BY location, created_at DESC
            """
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=(cutoff_time,))
                
            self.logger.info(f"Retrieved {len(df)} weather forecast records")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to get weather forecasts: {e}")
            return pd.DataFrame()
    
    def get_recent_earthquakes(self, days_back: int = 7, min_magnitude: float = 0.0) -> pd.DataFrame:
        """Get recent earthquake data from database."""
        try:
            cutoff_time = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            query = """
                SELECT earthquake_no, origin_time, magnitude_value, magnitude_type,
                       depth, location, epicenter_lat, epicenter_lon,
                       report_type, web_url, created_at
                FROM earthquakes 
                WHERE created_at > ? AND magnitude_value >= ?
                ORDER BY origin_time DESC
            """
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=(cutoff_time, min_magnitude))
                
            self.logger.info(f"Retrieved {len(df)} earthquake records")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to get earthquakes: {e}")
            return pd.DataFrame()
    
    def log_api_call(self, endpoint: str, api_source: str, success: bool, 
                     response_time: float = None, records_processed: int = None,
                     error_message: str = None):
        """Log API call for monitoring."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO api_logs 
                    (endpoint, api_source, success, response_time, 
                     records_processed, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    endpoint,
                    api_source,
                    success,
                    response_time,
                    records_processed,
                    error_message
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to log API call: {e}")
    
    def _update_data_freshness(self, data_type: str, record_count: int, quality_score: float = None):
        """Update data freshness tracking."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO data_freshness 
                    (data_type, last_update, record_count, data_quality_score)
                    VALUES (?, ?, ?, ?)
                """, (
                    data_type,
                    datetime.now().isoformat(),
                    record_count,
                    quality_score
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to update data freshness: {e}")
    
    def get_data_freshness_info(self) -> Dict[str, Any]:
        """Get data freshness information."""
        try:
            query = """
                SELECT data_type, last_update, record_count, data_quality_score
                FROM data_freshness
                ORDER BY last_update DESC
            """
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                
            freshness_info = {}
            for row in rows:
                freshness_info[row[0]] = {
                    'last_update': row[1],
                    'record_count': row[2],
                    'quality_score': row[3],
                    'age_hours': self._calculate_data_age_hours(row[1])
                }
                
            return freshness_info
            
        except Exception as e:
            self.logger.error(f"Failed to get data freshness info: {e}")
            return {}
    
    def _calculate_data_age_hours(self, last_update: str) -> float:
        """Calculate age of data in hours."""
        try:
            update_time = datetime.fromisoformat(last_update)
            age = datetime.now() - update_time
            return age.total_seconds() / 3600
        except:
            return float('inf')
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Get table record counts
                tables = ['weather_forecasts', 'earthquakes', 'weather_observations', 'api_logs']
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f'{table}_count'] = cursor.fetchone()[0]
                
                # Get database size
                stats['db_size_bytes'] = os.path.getsize(self.db_path)
                stats['db_size_mb'] = stats['db_size_bytes'] / (1024 * 1024)
                
                # Get API success rate
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_calls,
                        SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_calls,
                        AVG(response_time) as avg_response_time
                    FROM api_logs 
                    WHERE called_at > datetime('now', '-24 hours')
                """)
                
                api_stats = cursor.fetchone()
                if api_stats[0] > 0:
                    stats['api_success_rate'] = (api_stats[1] / api_stats[0]) * 100
                    stats['avg_api_response_time'] = api_stats[2]
                else:
                    stats['api_success_rate'] = 0
                    stats['avg_api_response_time'] = 0
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to manage database size."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean up old weather forecasts
                cursor.execute("DELETE FROM weather_forecasts WHERE created_at < ?", (cutoff_date,))
                weather_deleted = cursor.rowcount
                
                # Clean up old API logs
                cursor.execute("DELETE FROM api_logs WHERE called_at < ?", (cutoff_date,))
                logs_deleted = cursor.rowcount
                
                # Keep earthquakes longer (they're historically important)
                earthquake_cutoff = (datetime.now() - timedelta(days=days_to_keep * 2)).isoformat()
                cursor.execute("DELETE FROM earthquakes WHERE created_at < ?", (earthquake_cutoff,))
                eq_deleted = cursor.rowcount
                
                conn.commit()
                
                # Vacuum to reclaim space
                cursor.execute("VACUUM")
                
                self.logger.info(f"Cleanup completed: {weather_deleted} weather, {logs_deleted} logs, {eq_deleted} earthquakes deleted")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
    
    def export_data_to_csv(self, table_name: str, output_path: str) -> bool:
        """Export table data to CSV."""
        try:
            query = f"SELECT * FROM {table_name}"
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn)
                df.to_csv(output_path, index=False)
                
            self.logger.info(f"Exported {len(df)} records from {table_name} to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export {table_name}: {e}")
            return False