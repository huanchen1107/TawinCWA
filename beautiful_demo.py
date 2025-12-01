"""
Demo script to test the beautiful Taiwan Weather Dashboard
Run with: streamlit run beautiful_demo.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Taiwan Weather Demo",
    page_icon="🌤️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

.main .block-container {
    font-family: 'Inter', sans-serif;
}

.hero-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 3rem 2rem;
    border-radius: 20px;
    margin: 1rem 0;
    text-align: center;
    box-shadow: 0 15px 35px rgba(0,0,0,0.1);
}

.hero-title {
    color: white;
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.hero-subtitle {
    color: rgba(255,255,255,0.9);
    font-size: 1.2rem;
    margin-bottom: 2rem;
    font-weight: 300;
}

.weather-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.weather-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.2);
}

.metric-card {
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
}

.metric-value {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1976D2;
    margin-bottom: 0.5rem;
}

.metric-label {
    color: #666;
    font-size: 1rem;
    font-weight: 500;
}

.alert-card {
    border-left: 4px solid #ff5722;
    background: #fff3e0;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}

.alert-high {
    border-left-color: #f44336;
    background: #ffebee;
}

.data-source-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 0.5rem;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    border-left: 4px solid #2196F3;
    transition: all 0.3s ease;
}

.data-source-card:hover {
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}

.stButton > button {
    background: linear-gradient(45deg, #2196F3, #1976D2);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: linear-gradient(45deg, #1976D2, #1565C0);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(33, 150, 243, 0.4);
}
</style>
""", unsafe_allow_html=True)

def main():
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🌤️ Taiwan Weather Center</h1>
        <p class="hero-subtitle">Beautiful Real-time Weather Dashboard</p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 2rem;">
            <div style="text-align: center; color: white;">
                <div style="font-size: 1.5rem; font-weight: bold;">400+</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Weather Stations</div>
            </div>
            <div style="text-align: center; color: white;">
                <div style="font-size: 1.5rem; font-weight: bold;">24/7</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Real-time Updates</div>
            </div>
            <div style="text-align: center; color: white;">
                <div style="font-size: 1.5rem; font-weight: bold;">Live</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Earthquake Monitor</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Tabs
    tab1, tab2, tab3 = st.tabs(["🌤️ Weather Dashboard", "🌏 Earthquake Monitor", "📊 Demo Features"])
    
    with tab1:
        show_weather_demo()
    
    with tab2:
        show_earthquake_demo()
    
    with tab3:
        show_features_demo()

def show_weather_demo():
    st.markdown("### 🌦️ Current Weather Conditions")
    
    # Sample weather data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌡️</div>
            <div class="metric-value">25°C</div>
            <div class="metric-label">Temperature</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💧</div>
            <div class="metric-value">68%</div>
            <div class="metric-label">Humidity</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💨</div>
            <div class="metric-value">12 km/h</div>
            <div class="metric-label">Wind Speed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌧️</div>
            <div class="metric-value">30%</div>
            <div class="metric-label">Rain Chance</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Weather Alerts
    st.markdown("### ⚠️ Weather Alerts")
    
    st.markdown("""
    <div class="alert-card alert-high">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 1.5rem; margin-right: 1rem;">🌡️</span>
            <div>
                <strong>High Temperature Warning</strong> - Taipei City
                <br>
                <span style="color: #666;">Temperature expected to reach 35°C today</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Weather Map
    st.markdown("### 🗺️ Taiwan Weather Map")
    
    # Create a sample map
    taiwan_cities = pd.DataFrame({
        'City': ['Taipei', 'Taichung', 'Kaohsiung', 'Tainan', 'Taoyuan'],
        'lat': [25.0330, 24.1477, 22.6273, 22.9999, 24.9936],
        'lon': [121.5654, 120.6736, 120.3014, 120.2269, 121.3010],
        'temp': [25, 28, 30, 29, 26]
    })
    
    fig = px.scatter_mapbox(
        taiwan_cities, 
        lat="lat", 
        lon="lon",
        hover_name="City",
        hover_data=["temp"],
        color="temp",
        size_max=15,
        zoom=7,
        height=500,
        color_continuous_scale="RdYlBu_r",
        title="🌤️ Taiwan Temperature Map"
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=23.8, lon=120.9),
        ),
        margin={"r":0,"t":30,"l":0,"b":0}
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_earthquake_demo():
    st.markdown("### 🌏 Recent Earthquake Activity")
    
    # Sample earthquake data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌏</div>
            <div class="metric-value">3</div>
            <div class="metric-label">Recent Events</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <div class="metric-value">4.2</div>
            <div class="metric-label">Max Magnitude</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⬇️</div>
            <div class="metric-value">15 km</div>
            <div class="metric-label">Avg Depth</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⏰</div>
            <div class="metric-value">2 hrs</div>
            <div class="metric-label">Last Event</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent Earthquakes
    st.markdown("### 📋 Recent Earthquake Events")
    
    earthquakes = [
        {"location": "Hualien County", "magnitude": "4.2", "depth": "15", "time": "2024-01-15 14:30"},
        {"location": "Taitung County", "magnitude": "3.8", "depth": "22", "time": "2024-01-15 09:45"},
        {"location": "Yilan County", "magnitude": "3.2", "depth": "8", "time": "2024-01-14 22:15"}
    ]
    
    for eq in earthquakes:
        st.markdown(f"""
        <div class="weather-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: #1976D2;">📍 {eq['location']}</h4>
                    <p style="margin: 0.5rem 0; color: #666;">
                        <strong>Time:</strong> {eq['time']}<br>
                        <strong>Depth:</strong> {eq['depth']} km
                    </p>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2rem; font-weight: bold; color: #1976D2;">
                        {eq['magnitude']}
                    </div>
                    <div style="font-size: 0.9rem; color: #666;">Magnitude</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_features_demo():
    st.markdown("### 🎨 Beautiful UI Features")
    
    # Data Source Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="data-source-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #1976D2;">Taiwan CWA</h4>
                <span>🟢 Online</span>
            </div>
            <p style="color: #666; margin-bottom: 1rem;">Real-time weather, earthquake, and marine data</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.9rem; color: #999;">12 Active Endpoints</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="data-source-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #1976D2;">Data.gov</h4>
                <span>🟢 Online</span>
            </div>
            <p style="color: #666; margin-bottom: 1rem;">US Federal government open datasets</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.9rem; color: #999;">250,000+ Datasets</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="data-source-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #1976D2;">Census.gov</h4>
                <span>🟢 Online</span>
            </div>
            <p style="color: #666; margin-bottom: 1rem;">US Census demographic and economic data</p>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.9rem; color: #999;">500+ Datasets</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Interactive Controls
    st.markdown("### 🎛️ Interactive Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🌤️ Load Weather Data", use_container_width=True):
            st.success("✅ Weather data loaded successfully!")
        
        if st.button("🌏 Load Earthquake Data", use_container_width=True):
            st.success("✅ Earthquake data loaded successfully!")
    
    with col2:
        if st.button("🔄 Refresh All Data", use_container_width=True):
            st.info("🔄 Refreshing all data sources...")
        
        if st.button("📊 Export Data", use_container_width=True):
            st.success("✅ Data exported successfully!")
    
    # Feature List
    st.markdown("### ✨ Available Features")
    
    features = [
        "🌤️ Real-time Taiwan weather forecasts",
        "🌡️ Interactive temperature gauges", 
        "🗺️ Beautiful weather maps with Taiwan coordinates",
        "🌏 Live earthquake monitoring and alerts",
        "📊 Data quality scoring and validation",
        "💾 Multiple export formats (CSV, JSON, Excel)",
        "⚠️ Smart weather alerts with custom thresholds",
        "🎨 Modern UI inspired by Taiwan CWA design",
        "📱 Responsive design for mobile devices",
        "🔄 Auto-refresh capabilities"
    ]
    
    for feature in features:
        st.markdown(f"- {feature}")

if __name__ == "__main__":
    main()