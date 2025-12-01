"""
Streamlit Cloud Compatible Taiwan Weather Dashboard
Handles database initialization and cloud-specific issues
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
import tempfile

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="Taiwan Weather Center",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Beautiful CSS
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

.status-card {
    background: rgba(255, 255, 255, 0.1);
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
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
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'earthquake_data' not in st.session_state:
    st.session_state.earthquake_data = None
if 'api_status' not in st.session_state:
    st.session_state.api_status = None

@st.cache_resource
def init_crawlers():
    """Initialize crawlers for cloud deployment."""
    try:
        from crawler import TWCrawler
        from config import GOV_DATA_SOURCES
        
        taiwan_crawler = TWCrawler(GOV_DATA_SOURCES['taiwan_cwa'])
        return {'taiwan_cwa': taiwan_crawler}
    except Exception as e:
        st.error(f"Failed to initialize crawlers: {e}")
        return {}

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_weather_data():
    """Fetch weather data with caching."""
    crawlers = init_crawlers()
    
    if 'taiwan_cwa' not in crawlers:
        return None, "No Taiwan CWA crawler available"
    
    try:
        from utils import TaiwanWeatherProcessor
        
        crawler = crawlers['taiwan_cwa']
        processor = TaiwanWeatherProcessor()
        
        # Fetch raw data
        raw_data = crawler.get_dataset_data("F-A0010-001")
        
        if not raw_data:
            return None, "No weather data returned from API"
        
        # Process data
        df = processor.process_weather_forecast(raw_data)
        
        if df is None or df.empty:
            return None, "Weather data processing failed"
        
        return df, "Success"
        
    except Exception as e:
        return None, f"Error fetching weather data: {e}"

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_earthquake_data():
    """Fetch earthquake data with caching."""
    crawlers = init_crawlers()
    
    if 'taiwan_cwa' not in crawlers:
        return None, "No Taiwan CWA crawler available"
    
    try:
        from utils import TaiwanWeatherProcessor
        
        crawler = crawlers['taiwan_cwa']
        processor = TaiwanWeatherProcessor()
        
        # Fetch raw data
        raw_data = crawler.get_dataset_data("E-A0015-001")
        
        if not raw_data:
            return None, "No earthquake data returned from API"
        
        # Process data
        df = processor.process_earthquake_data(raw_data)
        
        if df is None or df.empty:
            return None, "Earthquake data processing failed"
        
        return df, "Success"
        
    except Exception as e:
        return None, f"Error fetching earthquake data: {e}"

def main():
    """Main application function for cloud deployment."""
    
    # Hero section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🌤️ Taiwan Weather Center</h1>
        <p style="font-size: 1.1rem; opacity: 0.9;">Real-time weather data from Taiwan Central Weather Administration</p>
        
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;">
            <div class="status-card">
                <div style="font-size: 1.5rem; font-weight: bold;">Live</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Taiwan CWA API</div>
            </div>
            <div class="status-card">
                <div style="font-size: 1.5rem; font-weight: bold;">Cloud</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Streamlit Hosted</div>
            </div>
            <div class="status-card">
                <div style="font-size: 1.5rem; font-weight: bold;">Real-time</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Updates</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["🌤️ Weather Dashboard", "🌏 Earthquake Monitor", "⚙️ Status"])
    
    with tab1:
        show_weather_dashboard()
    
    with tab2:
        show_earthquake_monitor()
    
    with tab3:
        show_system_status()

def show_weather_dashboard():
    """Weather dashboard for cloud deployment."""
    st.markdown("## 🌦️ Taiwan Weather Dashboard")
    
    # Control panel
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Weather Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        show_raw_data = st.checkbox("🔍 Show Raw Data", value=False)
    
    # Load weather data
    with st.spinner("🌤️ Loading Taiwan weather data..."):
        df, status = fetch_weather_data()
    
    if df is None:
        st.error(f"❌ {status}")
        st.info("💡 Try refreshing the data or check the Status tab for more information")
        return
    
    st.success(f"✅ Loaded weather data for {len(df)} locations")
    
    # Display weather data
    display_weather_data(df, show_raw_data)

def show_earthquake_monitor():
    """Earthquake monitor for cloud deployment."""
    st.markdown("## 🌏 Taiwan Earthquake Monitor")
    
    # Control panel
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Earthquake Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        show_details = st.checkbox("📋 Show Details", value=True)
    
    # Load earthquake data
    with st.spinner("🌏 Loading earthquake data..."):
        df, status = fetch_earthquake_data()
    
    if df is None:
        st.error(f"❌ {status}")
        st.info("💡 Try refreshing the data or check the Status tab for more information")
        return
    
    st.success(f"✅ Loaded {len(df)} earthquake records")
    
    # Display earthquake data
    display_earthquake_data(df, show_details)

def display_weather_data(df, show_raw_data):
    """Display weather data with beautiful formatting."""
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">🌤️</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{len(df)}</div>
            <div>Locations</div>
        </div>
        """, unsafe_allow_html=True)
    
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
        pop_cols = [col for col in df.columns if 'PoP_' in col and 'value' in col]
        if pop_cols:
            rain_probs = pd.to_numeric(df[pop_cols[0]], errors='coerce').dropna()
            avg_rain = f"{rain_probs.mean():.0f}%" if not rain_probs.empty else "N/A"
        else:
            avg_rain = "N/A"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">🌧️</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{avg_rain}</div>
            <div>Avg Rain Chance</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">⏰</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{datetime.now().strftime('%H:%M')}</div>
            <div>Current Time</div>
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
            display_location_weather(location_data.iloc[0], df.columns)
    
    # Taiwan weather map
    st.markdown("### 🗺️ Taiwan Weather Overview")
    create_taiwan_weather_map(df)
    
    # Raw data display
    if show_raw_data:
        st.markdown("### 📊 Raw Weather Data")
        st.dataframe(df, use_container_width=True)

def display_location_weather(row, all_columns):
    """Display weather for selected location."""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🌤️ Current Conditions")
        
        # Temperature
        temp_cols = [col for col in all_columns if 'T_' in col and 'value' in col]
        if temp_cols:
            temp_value = row.get(temp_cols[0], 'N/A')
            temp_unit = row.get(temp_cols[0].replace('value', 'unit'), '°C')
            st.write(f"🌡️ **Temperature**: {temp_value} {temp_unit}")
        
        # Weather condition
        wx_cols = [col for col in all_columns if 'Wx_' in col and 'name' in col]
        if wx_cols:
            weather_desc = row.get(wx_cols[0], 'N/A')
            st.write(f"☀️ **Weather**: {weather_desc}")
        
        # Rain probability
        pop_cols = [col for col in all_columns if 'PoP_' in col and 'value' in col]
        if pop_cols:
            rain_prob = row.get(pop_cols[0], 'N/A')
            st.write(f"🌧️ **Rain Probability**: {rain_prob}%")
        
        # Humidity
        rh_cols = [col for col in all_columns if 'RH_' in col and 'value' in col]
        if rh_cols:
            humidity = row.get(rh_cols[0], 'N/A')
            st.write(f"💧 **Humidity**: {humidity}%")
    
    with col2:
        # Temperature gauge
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
                        ]
                    }
                ))
                
                fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
                
            except:
                st.info("🌡️ Temperature gauge unavailable")

def create_taiwan_weather_map(df):
    """Create Taiwan weather map."""
    # Taiwan coordinates
    taiwan_coords = {
        '臺北市': (25.0330, 121.5654),
        '新北市': (25.0173, 121.4467),
        '桃園市': (24.9936, 121.3010),
        '臺中市': (24.1477, 120.6736),
        '臺南市': (22.9999, 120.2269),
        '高雄市': (22.6273, 120.3014)
    }
    
    # Prepare map data
    map_data = []
    for _, row in df.iterrows():
        location = row.get('location', '')
        if location in taiwan_coords:
            lat, lon = taiwan_coords[location]
            
            # Get temperature
            temp_cols = [col for col in df.columns if 'T_' in col and 'value' in col]
            temp_value = 25  # Default
            if temp_cols:
                try:
                    temp_str = str(row.get(temp_cols[0], ''))
                    if temp_str.replace('.', '').replace('-', '').isdigit():
                        temp_value = float(temp_str)
                except:
                    temp_value = 25
            
            map_data.append({
                'location': location,
                'latitude': lat,
                'longitude': lon,
                'temperature': temp_value
            })
    
    if map_data:
        map_df = pd.DataFrame(map_data)
        
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

def display_earthquake_data(df, show_details):
    """Display earthquake data."""
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">🌏</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{len(df)}</div>
            <div>Total Events</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if 'magnitude_value' in df.columns:
            magnitudes = pd.to_numeric(df['magnitude_value'], errors='coerce').dropna()
            max_mag = f"{magnitudes.max():.1f}" if not magnitudes.empty else "N/A"
        else:
            max_mag = "N/A"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">📊</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{max_mag}</div>
            <div>Max Magnitude</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if 'depth' in df.columns:
            depths = pd.to_numeric(df['depth'], errors='coerce').dropna()
            avg_depth = f"{depths.mean():.0f} km" if not depths.empty else "N/A"
        else:
            avg_depth = "N/A"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">⬇️</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{avg_depth}</div>
            <div>Avg Depth</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if 'origin_time' in df.columns:
            latest = df['origin_time'].max()
            time_display = latest[11:16] if latest and len(latest) > 16 else "N/A"
        else:
            time_display = "N/A"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">⏰</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{time_display}</div>
            <div>Latest Event</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent earthquakes
    if show_details:
        st.markdown("### 📋 Recent Earthquake Events")
        
        # Sort by time
        if 'origin_time' in df.columns:
            df_sorted = df.sort_values('origin_time', ascending=False)
        else:
            df_sorted = df
        
        for idx, eq in df_sorted.head(5).iterrows():
            st.markdown(f"""
            <div class="weather-card">
                <strong>📍 {eq.get('location', 'Unknown')}</strong><br>
                <strong>Magnitude:</strong> {eq.get('magnitude_value', 'N/A')}<br>
                <strong>Depth:</strong> {eq.get('depth', 'N/A')} km<br>
                <strong>Time:</strong> {eq.get('origin_time', 'N/A')}
            </div>
            """, unsafe_allow_html=True)

def show_system_status():
    """Show system status for troubleshooting."""
    st.markdown("## ⚙️ System Status")
    
    # Test API connectivity
    if st.button("🧪 Test Taiwan CWA API"):
        with st.spinner("Testing API connectivity..."):
            crawlers = init_crawlers()
            
            if 'taiwan_cwa' in crawlers:
                try:
                    is_healthy = crawlers['taiwan_cwa'].health_check()
                    if is_healthy:
                        st.success("✅ Taiwan CWA API is accessible")
                    else:
                        st.error("❌ Taiwan CWA API is not responding")
                except Exception as e:
                    st.error(f"❌ API test failed: {e}")
            else:
                st.error("❌ Taiwan CWA crawler not initialized")
    
    # System information
    st.markdown("### 💻 System Information")
    
    import platform
    st.write(f"**Python Version**: {platform.python_version()}")
    st.write(f"**Platform**: {platform.platform()}")
    st.write(f"**Current Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cache information
    st.markdown("### 💾 Cache Information")
    st.write("Weather data cache: 1 hour")
    st.write("Earthquake data cache: 30 minutes")
    
    if st.button("🗑️ Clear Cache"):
        st.cache_data.clear()
        st.success("✅ Cache cleared")
    
    # Debug information
    st.markdown("### 🔍 Debug Information")
    st.write("This is the Streamlit Cloud compatible version")
    st.write("Database features are disabled for cloud compatibility")
    st.write("All data is cached in memory during the session")

if __name__ == "__main__":
    main()