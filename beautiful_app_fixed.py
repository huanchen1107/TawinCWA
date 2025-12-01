"""
Beautiful Taiwan Weather Dashboard - Fixed for Streamlit Cloud
Simplified version without problematic components
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from crawler import TWCrawler, DataProcessor
from utils import format_file_size, format_number, TaiwanWeatherProcessor
from config import GOV_DATA_SOURCES, STREAMLIT_CONFIG, DATA_CATEGORIES

# Page configuration
st.set_page_config(
    page_title="Taiwan Weather Center",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Simplified CSS (inline to avoid file loading issues)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.main .block-container {
    font-family: 'Inter', sans-serif;
    padding-top: 1rem;
}

.hero-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    color: white;
    margin: 1rem 0;
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.metric-card {
    background: white;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
}

.weather-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.stButton > button {
    background: linear-gradient(45deg, #2196F3, #1976D2);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'taiwan_data' not in st.session_state:
    st.session_state.taiwan_data = None

def init_crawlers():
    """Initialize crawler instances."""
    try:
        taiwan_crawler = TWCrawler(GOV_DATA_SOURCES['taiwan_cwa'])
        return {'taiwan_cwa': taiwan_crawler}
    except Exception as e:
        st.error(f"Failed to initialize Taiwan crawler: {e}")
        return {}

def main():
    """Main application function."""
    
    # Hero section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🌤️ Taiwan Weather Center</h1>
        <p style="font-size: 1.1rem; opacity: 0.9;">Real-time weather data from Taiwan Central Weather Administration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["🌤️ Weather Dashboard", "🌏 Earthquake Monitor", "⚙️ Settings"])
    
    with tab1:
        show_weather_dashboard()
    
    with tab2:
        show_earthquake_monitor()
    
    with tab3:
        show_settings()

def show_weather_dashboard():
    """Weather dashboard page."""
    st.markdown("## 🌦️ Current Weather Conditions")
    
    # Initialize crawler
    crawlers = init_crawlers()
    taiwan_crawler = crawlers.get('taiwan_cwa')
    
    if not taiwan_crawler:
        st.error("❌ Taiwan CWA crawler not available")
        return
    
    # Control panel
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Weather Data", use_container_width=True):
            st.session_state.taiwan_data = None
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("🔄 Auto Refresh", value=False)
    
    # Load weather data
    if st.session_state.taiwan_data is None:
        with st.spinner("🌤️ Loading Taiwan weather data..."):
            try:
                # Get weather forecast
                weather_data = taiwan_crawler.get_dataset_data("F-A0010-001")
                
                if weather_data:
                    processor = TaiwanWeatherProcessor()
                    df = processor.process_weather_forecast(weather_data)
                    st.session_state.taiwan_data = df
                    
                    if df is not None and not df.empty:
                        st.success(f"✅ Loaded weather data for {len(df)} locations")
                    else:
                        st.warning("⚠️ Weather data processing failed")
                else:
                    st.error("❌ Failed to fetch weather data")
                    
            except Exception as e:
                st.error(f"❌ Error loading weather data: {e}")
                return
    
    # Display weather data
    if st.session_state.taiwan_data is not None and not st.session_state.taiwan_data.empty:
        display_weather_data(st.session_state.taiwan_data)
    else:
        st.info("No weather data available. Please refresh.")

def display_weather_data(df):
    """Display weather data with beautiful formatting."""
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">🌤️</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{}</div>
            <div>Locations</div>
        </div>
        """.format(len(df)), unsafe_allow_html=True)
    
    with col2:
        temp_cols = [col for col in df.columns if 'T_' in col and 'value' in col]
        if temp_cols:
            temps = pd.to_numeric(df[temp_cols[0]], errors='coerce').dropna()
            avg_temp = f"{temps.mean():.1f}°C" if not temps.empty else "N/A"
        else:
            avg_temp = "N/A"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">🌡️</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{avg_temp}</div>
            <div>Avg Temperature</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">⏰</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{datetime.now().strftime('%H:%M')}</div>
            <div>Last Update</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">🟢</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">Live</div>
            <div>Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Location selector
    if 'location' in df.columns:
        locations = sorted(df['location'].unique())
        
        # Prioritize major cities
        major_cities = ['臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市']
        priority_locations = [loc for loc in major_cities if loc in locations]
        other_locations = [loc for loc in locations if loc not in major_cities]
        ordered_locations = priority_locations + other_locations
        
        selected_location = st.selectbox("📍 Select Location:", ordered_locations)
        
        # Filter data for selected location
        location_data = df[df['location'] == selected_location]
        
        if not location_data.empty:
            row = location_data.iloc[0]
            
            st.markdown(f"### 🌤️ Weather Details - {selected_location}")
            
            # Extract weather information
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("#### Current Conditions")
                
                # Temperature
                temp_cols = [col for col in df.columns if 'T_' in col and 'value' in col]
                if temp_cols:
                    temp_value = row.get(temp_cols[0], 'N/A')
                    temp_unit = row.get(temp_cols[0].replace('value', 'unit'), '°C')
                    st.write(f"🌡️ **Temperature**: {temp_value} {temp_unit}")
                
                # Weather condition
                wx_cols = [col for col in df.columns if 'Wx_' in col and 'name' in col]
                if wx_cols:
                    weather_desc = row.get(wx_cols[0], 'N/A')
                    st.write(f"☀️ **Weather**: {weather_desc}")
                
                # Rain probability
                pop_cols = [col for col in df.columns if 'PoP_' in col and 'value' in col]
                if pop_cols:
                    rain_prob = row.get(pop_cols[0], 'N/A')
                    st.write(f"🌧️ **Rain Probability**: {rain_prob}%")
            
            with col2:
                # Temperature gauge if available
                if temp_cols:
                    try:
                        temp_val = float(row.get(temp_cols[0], 0))
                        
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=temp_val,
                            title={'text': "Temperature (°C)"},
                            gauge={
                                'axis': {'range': [0, 40]},
                                'bar': {'color': "#1976D2"},
                                'steps': [
                                    {'range': [0, 15], 'color': '#E3F2FD'},
                                    {'range': [15, 25], 'color': '#BBDEFB'},
                                    {'range': [25, 40], 'color': '#90CAF9'}
                                ],
                                'threshold': {'line': {'color': "red", 'width': 4}, 'value': 35}
                            }
                        ))
                        
                        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig, use_container_width=True)
                        
                    except:
                        st.info("🌡️ Temperature gauge unavailable")
    
    # Taiwan weather map
    st.markdown("### 🗺️ Taiwan Weather Overview")
    create_taiwan_map(df)

def create_taiwan_map(df):
    """Create Taiwan weather map."""
    # Taiwan coordinates for major cities
    taiwan_coords = {
        '臺北市': (25.0330, 121.5654),
        '新北市': (25.0173, 121.4467),
        '桃園市': (24.9936, 121.3010),
        '臺中市': (24.1477, 120.6736),
        '臺南市': (22.9999, 120.2269),
        '高雄市': (22.6273, 120.3014),
        '基隆市': (25.1276, 121.7391),
        '新竹市': (24.8138, 120.9675),
        '嘉義市': (23.4801, 120.4491)
    }
    
    # Prepare map data
    map_data = []
    for _, row in df.iterrows():
        location = row.get('location', '')
        if location in taiwan_coords:
            lat, lon = taiwan_coords[location]
            
            # Get temperature
            temp_cols = [col for col in df.columns if 'T_' in col and 'value' in col]
            temp_value = None
            if temp_cols:
                try:
                    temp_str = str(row.get(temp_cols[0], ''))
                    if temp_str.replace('.', '').replace('-', '').isdigit():
                        temp_value = float(temp_str)
                except:
                    temp_value = 20  # Default value
            
            map_data.append({
                'location': location,
                'latitude': lat,
                'longitude': lon,
                'temperature': temp_value or 20
            })
    
    if map_data:
        map_df = pd.DataFrame(map_data)
        
        # Create map
        fig = px.scatter_mapbox(
            map_df, 
            lat="latitude", 
            lon="longitude",
            hover_name="location",
            hover_data=["temperature"],
            color="temperature",
            size_max=15,
            zoom=7,
            height=400,
            color_continuous_scale="RdYlBu_r"
        )
        
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(center=dict(lat=23.8, lon=120.9)),
            margin={"r":0,"t":30,"l":0,"b":0}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("🗺️ Map data not available")

def show_earthquake_monitor():
    """Earthquake monitoring page."""
    st.markdown("## 🌏 Earthquake Monitor")
    
    crawlers = init_crawlers()
    taiwan_crawler = crawlers.get('taiwan_cwa')
    
    if not taiwan_crawler:
        st.error("❌ Taiwan CWA crawler not available")
        return
    
    if st.button("🔄 Load Earthquake Data"):
        with st.spinner("🌏 Loading earthquake data..."):
            try:
                eq_data = taiwan_crawler.get_dataset_data("E-A0015-001")
                
                if eq_data:
                    processor = TaiwanWeatherProcessor()
                    eq_df = processor.process_earthquake_data(eq_data)
                    
                    if eq_df is not None and not eq_df.empty:
                        st.success(f"✅ Loaded {len(eq_df)} earthquake records")
                        
                        # Display recent earthquakes
                        st.markdown("### 📋 Recent Earthquake Events")
                        
                        for idx, eq in eq_df.head(5).iterrows():
                            st.markdown(f"""
                            <div class="weather-card">
                                <strong>📍 {eq.get('location', 'Unknown')}</strong><br>
                                <strong>Magnitude:</strong> {eq.get('magnitude_value', 'N/A')}<br>
                                <strong>Depth:</strong> {eq.get('depth', 'N/A')} km<br>
                                <strong>Time:</strong> {eq.get('origin_time', 'N/A')}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ No earthquake data available")
                else:
                    st.error("❌ Failed to fetch earthquake data")
                    
            except Exception as e:
                st.error(f"❌ Error loading earthquake data: {e}")

def show_settings():
    """Settings page."""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### 🔑 API Configuration")
    
    api_key = GOV_DATA_SOURCES['taiwan_cwa'].get('api_key', 'Not configured')
    st.info(f"Taiwan CWA API Key: {api_key[:15]}...")
    
    st.markdown("### 📊 System Status")
    
    crawlers = init_crawlers()
    
    if 'taiwan_cwa' in crawlers:
        if st.button("🧪 Test Taiwan CWA API"):
            with st.spinner("Testing API connection..."):
                try:
                    is_healthy = crawlers['taiwan_cwa'].health_check()
                    if is_healthy:
                        st.success("✅ Taiwan CWA API is online")
                    else:
                        st.error("❌ Taiwan CWA API is not responding")
                except Exception as e:
                    st.error(f"❌ API test failed: {e}")

if __name__ == "__main__":
    main()