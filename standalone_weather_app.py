"""
Standalone Taiwan Weather App - No Streamlit Required
A beautiful command-line interface for Taiwan weather data
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import sys
import os

# Add current directory to path
sys.path.append('.')

from crawler.taiwan_crawler import TWCrawler
from config import GOV_DATA_SOURCES
from utils.taiwan_weather_helper import TaiwanWeatherProcessor

def print_header():
    """Print beautiful header."""
    print("=" * 60)
    print("🌤️  TAIWAN WEATHER CENTER  🌤️")
    print("Central Weather Administration Data")
    print("=" * 60)
    print()

def print_weather_summary(df):
    """Print weather summary in a beautiful format."""
    if df is None or df.empty:
        print("❌ No weather data available")
        return
    
    print("🌦️  CURRENT WEATHER CONDITIONS")
    print("-" * 40)
    
    for _, row in df.head(10).iterrows():
        location = row.get('location', 'Unknown')
        
        # Get temperature
        temp_cols = [col for col in df.columns if 'T_' in col and 'value' in col]
        temp = row.get(temp_cols[0], 'N/A') if temp_cols else 'N/A'
        temp_unit = row.get(temp_cols[0].replace('value', 'unit'), '°C') if temp_cols else ''
        
        # Get weather description
        wx_cols = [col for col in df.columns if 'Wx_' in col and 'name' in col]
        weather = row.get(wx_cols[0], 'N/A') if wx_cols else 'N/A'
        
        # Get rain probability
        pop_cols = [col for col in df.columns if 'PoP_' in col and 'value' in col]
        rain_prob = row.get(pop_cols[0], 'N/A') if pop_cols else 'N/A'
        
        print(f"📍 {location}")
        print(f"   🌡️  Temperature: {temp} {temp_unit}")
        print(f"   🌤️  Condition: {weather}")
        print(f"   🌧️  Rain Probability: {rain_prob}%")
        print()

def print_earthquake_summary(df):
    """Print earthquake summary."""
    if df is None or df.empty:
        print("❌ No earthquake data available")
        return
    
    print("🌏  RECENT EARTHQUAKE ACTIVITY")
    print("-" * 40)
    
    # Sort by time if available
    if 'origin_time' in df.columns:
        df_sorted = df.sort_values('origin_time', ascending=False)
    else:
        df_sorted = df
    
    for _, eq in df_sorted.head(5).iterrows():
        location = eq.get('location', 'Unknown')
        magnitude = eq.get('magnitude_value', 'N/A')
        depth = eq.get('depth', 'N/A')
        time_str = eq.get('origin_time', 'N/A')
        
        print(f"📍 {location}")
        print(f"   📊 Magnitude: {magnitude}")
        print(f"   ⬇️  Depth: {depth} km")
        print(f"   ⏰ Time: {time_str}")
        print()

def test_taiwan_weather():
    """Test Taiwan weather functionality."""
    print_header()
    
    try:
        # Initialize crawler
        print("🔄 Initializing Taiwan CWA crawler...")
        crawler = TWCrawler(GOV_DATA_SOURCES['taiwan_cwa'])
        processor = TaiwanWeatherProcessor()
        
        # Test connection
        print("📡 Testing API connection...")
        if crawler.health_check():
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed!")
            return
        
        print()
        
        # Get weather forecast
        print("🌤️ Fetching 36-hour weather forecast...")
        try:
            weather_data = crawler.get_dataset_data("F-A0010-001")
            if weather_data:
                df = processor.process_weather_forecast(weather_data)
                print_weather_summary(df)
            else:
                print("❌ Failed to fetch weather data")
        except Exception as e:
            print(f"❌ Weather data error: {e}")
        
        # Get earthquake data
        print("🌏 Fetching earthquake data...")
        try:
            earthquake_data = crawler.get_dataset_data("E-A0015-001")
            if earthquake_data:
                eq_df = processor.process_earthquake_data(earthquake_data)
                print_earthquake_summary(eq_df)
            else:
                print("❌ Failed to fetch earthquake data")
        except Exception as e:
            print(f"❌ Earthquake data error: {e}")
        
        # Show API info
        print("📊  API INFORMATION")
        print("-" * 40)
        print(f"🔑 API Key: {GOV_DATA_SOURCES['taiwan_cwa']['api_key'][:15]}...")
        print(f"🌐 Base URL: {GOV_DATA_SOURCES['taiwan_cwa']['base_url']}")
        print(f"⏱️  Rate Limit: {GOV_DATA_SOURCES['taiwan_cwa']['rate_limit']} sec")
        print()
        
        print("✅ Taiwan Weather App test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def interactive_weather_menu():
    """Interactive weather menu."""
    print_header()
    
    crawler = TWCrawler(GOV_DATA_SOURCES['taiwan_cwa'])
    processor = TaiwanWeatherProcessor()
    
    while True:
        print("\n🌤️  TAIWAN WEATHER MENU")
        print("-" * 30)
        print("1. 🌦️  Current Weather Forecast")
        print("2. 🌏 Recent Earthquakes") 
        print("3. 📊 API Status Check")
        print("4. 🔍 Search Datasets")
        print("5. ❌ Exit")
        print()
        
        try:
            choice = input("Select an option (1-5): ").strip()
            
            if choice == "1":
                print("\n🔄 Loading weather forecast...")
                data = crawler.get_dataset_data("F-A0010-001")
                if data:
                    df = processor.process_weather_forecast(data)
                    print_weather_summary(df)
                else:
                    print("❌ Weather data unavailable")
            
            elif choice == "2":
                print("\n🔄 Loading earthquake data...")
                data = crawler.get_dataset_data("E-A0015-001")
                if data:
                    df = processor.process_earthquake_data(data)
                    print_earthquake_summary(df)
                else:
                    print("❌ Earthquake data unavailable")
            
            elif choice == "3":
                print("\n🔄 Checking API status...")
                status = crawler.health_check()
                if status:
                    print("✅ Taiwan CWA API is online and accessible")
                else:
                    print("❌ Taiwan CWA API is not responding")
            
            elif choice == "4":
                query = input("\n🔍 Enter search term: ").strip()
                if query:
                    print(f"\n🔄 Searching for '{query}'...")
                    results = crawler.search_datasets(query, limit=5)
                    if results:
                        print(f"✅ Found {len(results)} datasets:")
                        for i, dataset in enumerate(results, 1):
                            print(f"{i}. {dataset['title']}")
                            print(f"   📝 {dataset['description'][:100]}...")
                            print()
                    else:
                        print("❌ No datasets found")
            
            elif choice == "5":
                print("\n👋 Thank you for using Taiwan Weather Center!")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check if we want interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_weather_menu()
    else:
        test_taiwan_weather()