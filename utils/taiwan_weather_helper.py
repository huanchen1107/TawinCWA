"""Helper functions specifically for Taiwan CWA weather data processing."""

import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class TaiwanWeatherProcessor:
    """Process Taiwan CWA weather data for better visualization."""
    
    def __init__(self):
        self.location_mapping = {
            # Common Taiwan location codes and names
            'taipei': ['臺北市', 'Taipei City'],
            'new_taipei': ['新北市', 'New Taipei City'],
            'taoyuan': ['桃園市', 'Taoyuan City'],
            'taichung': ['臺中市', 'Taichung City'],
            'tainan': ['臺南市', 'Tainan City'],
            'kaohsiung': ['高雄市', 'Kaohsiung City'],
            'keelung': ['基隆市', 'Keelung City'],
            'hsinchu_city': ['新竹市', 'Hsinchu City'],
            'chiayi_city': ['嘉義市', 'Chiayi City']
        }
    
    def process_weather_forecast(self, raw_data: Dict) -> Optional[pd.DataFrame]:
        """Process Taiwan weather forecast data into DataFrame."""
        try:
            if 'cwaopendata' not in raw_data:
                return None
            
            dataset = raw_data['cwaopendata']['dataset']
            locations = dataset.get('location', [])
            
            processed_data = []
            
            for location in locations:
                location_name = location.get('locationName', 'Unknown')
                
                # Process weather elements
                weather_elements = location.get('weatherElement', [])
                
                location_data = {
                    'location': location_name,
                    'location_en': self._get_english_name(location_name),
                }
                
                # Extract weather parameters
                for element in weather_elements:
                    element_name = element.get('elementName', '')
                    element_value = element.get('time', [])
                    
                    if element_value:
                        # Get the first time period
                        first_time = element_value[0]
                        start_time = first_time.get('startTime', '')
                        end_time = first_time.get('endTime', '')
                        
                        # Extract parameter value
                        parameters = first_time.get('parameter', [])
                        if parameters:
                            param = parameters[0]
                            param_name = param.get('parameterName', '')
                            param_value = param.get('parameterValue', '')
                            param_unit = param.get('parameterUnit', '')
                            
                            location_data[f"{element_name}_name"] = param_name
                            location_data[f"{element_name}_value"] = param_value
                            location_data[f"{element_name}_unit"] = param_unit
                            location_data[f"{element_name}_start"] = start_time
                            location_data[f"{element_name}_end"] = end_time
                
                processed_data.append(location_data)
            
            return pd.DataFrame(processed_data)
            
        except Exception as e:
            print(f"Error processing weather forecast: {e}")
            return None
    
    def process_current_weather(self, raw_data: Dict) -> Optional[pd.DataFrame]:
        """Process current weather observation data."""
        try:
            if 'cwaopendata' not in raw_data:
                return None
            
            dataset = raw_data['cwaopendata']['dataset']
            locations = dataset.get('location', [])
            
            processed_data = []
            
            for location in locations:
                location_name = location.get('locationName', 'Unknown')
                
                location_data = {
                    'station': location_name,
                    'station_id': location.get('stationId', ''),
                    'observation_time': location.get('time', {}).get('obsTime', ''),
                }
                
                # Process weather elements
                weather_elements = location.get('weatherElement', [])
                for element in weather_elements:
                    element_name = element.get('elementName', '')
                    element_value = element.get('elementValue', '')
                    
                    location_data[element_name] = element_value
                
                # Process location info
                lat = location.get('lat', '')
                lon = location.get('lon', '')
                if lat and lon:
                    location_data['latitude'] = float(lat) if lat else None
                    location_data['longitude'] = float(lon) if lon else None
                
                processed_data.append(location_data)
            
            return pd.DataFrame(processed_data)
            
        except Exception as e:
            print(f"Error processing current weather: {e}")
            return None
    
    def process_earthquake_data(self, raw_data: Dict) -> Optional[pd.DataFrame]:
        """Process earthquake report data."""
        try:
            if 'cwaopendata' not in raw_data:
                return None
            
            dataset = raw_data['cwaopendata']['dataset']
            earthquakes = dataset.get('earthquake', [])
            
            processed_data = []
            
            for eq in earthquakes:
                eq_info = eq.get('earthquakeInfo', {})
                
                earthquake_data = {
                    'earthquake_no': eq.get('earthquakeNo', ''),
                    'report_type': eq.get('reportType', ''),
                    'report_color': eq.get('reportColor', ''),
                    'report_content': eq.get('reportContent', ''),
                    'web_url': eq.get('web', ''),
                    'origin_time': eq_info.get('originTime', ''),
                    'magnitude_type': eq_info.get('magnitudeType', ''),
                    'magnitude_value': eq_info.get('magnitudeValue', ''),
                    'depth': eq_info.get('depth', ''),
                    'epicenter_lat': eq_info.get('epicenter', {}).get('lat', ''),
                    'epicenter_lon': eq_info.get('epicenter', {}).get('lon', ''),
                    'location': eq_info.get('epicenter', {}).get('location', ''),
                }
                
                processed_data.append(earthquake_data)
            
            return pd.DataFrame(processed_data)
            
        except Exception as e:
            print(f"Error processing earthquake data: {e}")
            return None
    
    def _get_english_name(self, chinese_name: str) -> str:
        """Convert Chinese location name to English."""
        for en_key, names in self.location_mapping.items():
            if chinese_name in names:
                return en_key.replace('_', ' ').title()
        return chinese_name
    
    def get_weather_summary(self, df: pd.DataFrame, data_type: str) -> Dict[str, Any]:
        """Generate summary statistics for weather data."""
        if df is None or df.empty:
            return {}
        
        summary = {
            'total_records': len(df),
            'data_type': data_type,
            'last_updated': datetime.now().isoformat(),
        }
        
        if data_type == 'forecast':
            # Forecast-specific summaries
            if 'location' in df.columns:
                summary['locations_count'] = df['location'].nunique()
                summary['locations'] = df['location'].unique().tolist()
        
        elif data_type == 'current':
            # Current weather summaries
            if 'station' in df.columns:
                summary['stations_count'] = df['station'].nunique()
                
            # Temperature statistics if available
            temp_columns = [col for col in df.columns if 'temp' in col.lower()]
            if temp_columns:
                for col in temp_columns:
                    numeric_values = pd.to_numeric(df[col], errors='coerce').dropna()
                    if not numeric_values.empty:
                        summary[f'{col}_avg'] = numeric_values.mean()
                        summary[f'{col}_min'] = numeric_values.min()
                        summary[f'{col}_max'] = numeric_values.max()
        
        elif data_type == 'earthquake':
            # Earthquake-specific summaries
            if 'magnitude_value' in df.columns:
                magnitudes = pd.to_numeric(df['magnitude_value'], errors='coerce').dropna()
                if not magnitudes.empty:
                    summary['magnitude_avg'] = magnitudes.mean()
                    summary['magnitude_max'] = magnitudes.max()
                    summary['magnitude_min'] = magnitudes.min()
            
            if 'depth' in df.columns:
                depths = pd.to_numeric(df['depth'], errors='coerce').dropna()
                if not depths.empty:
                    summary['depth_avg'] = depths.mean()
        
        return summary
    
    def create_weather_alerts(self, df: pd.DataFrame) -> List[Dict[str, str]]:
        """Generate weather alerts from forecast data."""
        alerts = []
        
        if df is None or df.empty:
            return alerts
        
        try:
            # Check for extreme weather conditions
            for _, row in df.iterrows():
                location = row.get('location', 'Unknown')
                
                # Temperature alerts (example thresholds)
                temp_cols = [col for col in df.columns if 'temp' in col.lower() and 'value' in col]
                for temp_col in temp_cols:
                    temp_value = row.get(temp_col, '')
                    if temp_value and temp_value.isdigit():
                        temp = int(temp_value)
                        if temp >= 35:
                            alerts.append({
                                'type': 'High Temperature',
                                'location': location,
                                'message': f'High temperature warning: {temp}°C',
                                'severity': 'warning'
                            })
                        elif temp <= 5:
                            alerts.append({
                                'type': 'Low Temperature',
                                'location': location,
                                'message': f'Cold weather alert: {temp}°C',
                                'severity': 'info'
                            })
                
                # Weather condition alerts
                weather_cols = [col for col in df.columns if 'wx' in col.lower() and 'name' in col]
                for weather_col in weather_cols:
                    weather_desc = row.get(weather_col, '')
                    if any(keyword in weather_desc for keyword in ['雨', '雷', '颱', 'rain', 'thunder', 'typhoon']):
                        alerts.append({
                            'type': 'Weather Alert',
                            'location': location,
                            'message': f'Weather condition: {weather_desc}',
                            'severity': 'info'
                        })
        
        except Exception as e:
            print(f"Error creating weather alerts: {e}")
        
        return alerts