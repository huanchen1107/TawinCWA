#!/usr/bin/env python3
"""
Quick Taiwan Weather Test - Your API is working!
"""

import sys
sys.path.append('.')

from crawler.taiwan_crawler import TWCrawler
from config import GOV_DATA_SOURCES
from utils.taiwan_weather_helper import TaiwanWeatherProcessor

def main():
    print("🌤️ QUICK TAIWAN WEATHER TEST")
    print("=" * 40)
    
    try:
        # Test your API
        crawler = TWCrawler(GOV_DATA_SOURCES['taiwan_cwa'])
        print(f"🔑 API Key: {GOV_DATA_SOURCES['taiwan_cwa']['api_key'][:15]}...")
        
        # Test connection
        print("📡 Testing connection...")
        if crawler.health_check():
            print("✅ Your Taiwan CWA API is WORKING!")
        else:
            print("❌ Connection failed")
            return
            
        # Get weather data
        print("🌦️ Getting weather forecast...")
        data = crawler.get_dataset_data("F-A0010-001")
        
        if data and 'cwaopendata' in data:
            print("✅ Weather data received!")
            
            # Process the data
            processor = TaiwanWeatherProcessor()
            df = processor.process_weather_forecast(data)
            
            if df is not None and not df.empty:
                print(f"📊 Processed {len(df)} location forecasts")
                
                # Show sample cities
                cities = df['location'].tolist()[:5]
                print(f"📍 Sample cities: {', '.join(cities)}")
                
                # Show Taipei weather if available
                taipei_data = df[df['location'].str.contains('臺北', na=False)]
                if not taipei_data.empty:
                    print("\n🌤️ TAIPEI WEATHER:")
                    row = taipei_data.iloc[0]
                    
                    # Get temperature
                    temp_cols = [col for col in df.columns if 'T_' in col and 'value' in col]
                    if temp_cols:
                        temp = row.get(temp_cols[0], 'N/A')
                        print(f"   🌡️ Temperature: {temp}°C")
                    
                    # Get weather description  
                    wx_cols = [col for col in df.columns if 'Wx_' in col and 'name' in col]
                    if wx_cols:
                        weather = row.get(wx_cols[0], 'N/A')
                        print(f"   ☀️ Condition: {weather}")
            else:
                print("⚠️ Data processing issue")
        else:
            print("⚠️ Weather data format unexpected")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✨ Test completed!")
    print("\n🚀 NEXT STEPS:")
    print("1. Use: python standalone_weather_app.py --interactive")
    print("2. Deploy to Streamlit Cloud (even if local Streamlit has issues)")
    print("3. Your Taiwan weather data is ready! 🌤️")

if __name__ == "__main__":
    main()