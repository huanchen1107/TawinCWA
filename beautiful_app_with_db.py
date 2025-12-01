"""
Beautiful Taiwan Weather Dashboard with SQLite Database Integration
Real-time data with intelligent caching and database storage
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
from crawler import TWCrawler, WeatherDataService
from utils import TaiwanWeatherProcessor
from config import GOV_DATA_SOURCES

# Page configuration
st.set_page_config(
    page_title="Taiwan Weather Center (DB)",
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

.database-status {
    background: rgba(255, 255, 255, 0.1);
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
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

.data-quality-high {
    border-left: 4px solid #4CAF50;
    background: #e8f5e8;
    padding: 1rem;
    border-radius: 5px;
}

.data-quality-medium {
    border-left: 4px solid #ff9800;
    background: #fff3e0;
    padding: 1rem;
    border-radius: 5px;
}

.data-quality-low {
    border-left: 4px solid #f44336;
    background: #ffebee;
    padding: 1rem;
    border-radius: 5px;
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
if 'data_service' not in st.session_state:
    st.session_state.data_service = None
if 'db_status' not in st.session_state:
    st.session_state.db_status = None

@st.cache_resource
def init_data_service():
    """Initialize data service with database."""
    try:
        crawlers = {
            'taiwan_cwa': TWCrawler(GOV_DATA_SOURCES['taiwan_cwa'])
        }
        return WeatherDataService(crawlers)
    except Exception as e:
        st.error(f"Failed to initialize data service: {e}")
        return None

def main():
    """Main application function."""
    
    # Initialize data service
    if st.session_state.data_service is None:
        st.session_state.data_service = init_data_service()
    
    data_service = st.session_state.data_service
    
    if not data_service:
        st.error("❌ Data service not available")
        return
    
    # Hero section with database status
    show_hero_with_db_status(data_service)
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌤️ Weather Dashboard", 
        "🌏 Earthquake Monitor", 
        "📊 Database Status",
        "⚙️ Settings"
    ])
    
    with tab1:
        show_weather_dashboard_with_db(data_service)
    
    with tab2:
        show_earthquake_monitor_with_db(data_service)
    
    with tab3:
        show_database_status(data_service)
    
    with tab4:
        show_settings_with_db(data_service)

def show_hero_with_db_status(data_service):
    """Hero section with database integration."""
    
    # Get database status
    if st.session_state.db_status is None:
        st.session_state.db_status = data_service.get_database_status()
    
    db_status = st.session_state.db_status
    health_score = db_status.get('health_score', 0)
    
    # Determine health status
    if health_score >= 80:
        health_icon = "🟢"
        health_text = "Excellent"
    elif health_score >= 60:
        health_icon = "🟡"
        health_text = "Good"
    else:
        health_icon = "🔴"
        health_text = "Needs Attention"
    
    st.markdown(f"""
    <div class="hero-section">
        <h1 class="hero-title">🌤️ Taiwan Weather Center</h1>
        <p style="font-size: 1.1rem; opacity: 0.9;">Real-time weather data with SQLite database integration</p>
        
        <div class="database-status">
            <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1rem;">
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold;">{db_status.get('database_stats', {}).get('weather_forecasts_count', 0)}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Weather Records</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold;">{db_status.get('database_stats', {}).get('earthquakes_count', 0)}</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Earthquake Records</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold;">{health_icon} {health_score:.0f}%</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">System Health</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: bold;">{db_status.get('database_stats', {}).get('db_size_mb', 0):.1f} MB</div>
                    <div style="font-size: 0.9rem; opacity: 0.8;">Database Size</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_weather_dashboard_with_db(data_service):
    """Weather dashboard with database integration."""
    st.markdown("## 🌦️ Weather Dashboard (Database-Powered)")
    
    # Control panel
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Weather Data", use_container_width=True):
            with st.spinner("Refreshing weather data..."):
                success = data_service._fetch_and_store_weather_data()
                if success:
                    st.success("✅ Weather data refreshed!")
                    st.rerun()
                else:
                    st.error("❌ Failed to refresh weather data")
    
    with col2:
        force_refresh = st.checkbox("🔧 Force API Call", help="Force API call even if data is fresh")
    
    with col3:
        show_metadata = st.checkbox("📊 Show Data Info", value=True)
    
    # Get weather data from database
    try:
        df, metadata = data_service.get_weather_forecast_data(force_refresh=force_refresh)
        
        if df.empty:
            st.warning("⚠️ No weather data available. Click 'Refresh Weather Data' to fetch from API.")
            return
        
        # Show data metadata
        if show_metadata:
            show_data_quality_info(metadata, "Weather Forecast")
        
        # Display weather data
        display_weather_data_from_db(df, metadata)
        
    except Exception as e:
        st.error(f"❌ Error loading weather data: {e}")

def show_earthquake_monitor_with_db(data_service):
    """Earthquake monitor with database integration."""
    st.markdown("## 🌏 Earthquake Monitor (Database-Powered)")
    
    # Control panel
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Earthquake Data", use_container_width=True):
            with st.spinner("Refreshing earthquake data..."):
                success = data_service._fetch_and_store_earthquake_data()
                if success:
                    st.success("✅ Earthquake data refreshed!")
                    st.rerun()
                else:
                    st.error("❌ Failed to refresh earthquake data")
    
    with col2:
        days_back = st.slider("📅 Days Back", 1, 30, 7)
    
    with col3:
        min_magnitude = st.slider("📊 Min Magnitude", 0.0, 8.0, 2.0, 0.1)
    
    # Get earthquake data from database
    try:
        df, metadata = data_service.get_earthquake_data(
            days_back=days_back, 
            min_magnitude=min_magnitude
        )
        
        if df.empty:
            st.warning(f"⚠️ No earthquakes found with magnitude ≥ {min_magnitude} in the last {days_back} days.")
            return
        
        # Show data metadata
        show_data_quality_info(metadata, "Earthquake Data")
        
        # Display earthquake data
        display_earthquake_data_from_db(df, metadata)
        
    except Exception as e:
        st.error(f"❌ Error loading earthquake data: {e}")

def show_data_quality_info(metadata, data_type):
    """Show data quality information."""
    age_hours = metadata.get('data_age_hours', 0)
    is_fresh = metadata.get('is_fresh', False)
    
    # Determine quality level
    if is_fresh and age_hours < 6:
        quality_class = "data-quality-high"
        quality_icon = "🟢"
        quality_text = "Fresh Data"
    elif age_hours < 24:
        quality_class = "data-quality-medium"
        quality_icon = "🟡"
        quality_text = "Acceptable"
    else:
        quality_class = "data-quality-low"
        quality_icon = "🔴"
        quality_text = "Stale Data"
    
    st.markdown(f"""
    <div class="{quality_class}">
        <strong>{quality_icon} {data_type} Quality: {quality_text}</strong><br>
        📊 Records: {metadata.get('record_count', 0)}<br>
        ⏰ Last Update: {metadata.get('last_update', 'Unknown')[:19] if metadata.get('last_update') else 'Unknown'}<br>
        🕒 Data Age: {age_hours:.1f} hours<br>
        📡 Source: {metadata.get('source', 'Unknown')}
    </div>
    """, unsafe_allow_html=True)

def display_weather_data_from_db(df, metadata):
    """Display weather data from database."""
    
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
        avg_temp = df['temperature'].mean() if 'temperature' in df.columns and df['temperature'].notna().any() else None
        temp_display = f"{avg_temp:.1f}°C" if avg_temp else "N/A"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">🌡️</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{temp_display}</div>
            <div>Avg Temperature</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_rain = df['rain_probability'].mean() if 'rain_probability' in df.columns and df['rain_probability'].notna().any() else None
        rain_display = f"{avg_rain:.0f}%" if avg_rain else "N/A"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">🌧️</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{rain_display}</div>
            <div>Avg Rain Probability</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        last_update = metadata.get('last_update', '')
        update_display = last_update[11:16] if len(last_update) > 16 else "N/A"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">⏰</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{update_display}</div>
            <div>Last Update</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Location selector
    if 'location' in df.columns and not df['location'].empty:
        locations = sorted(df['location'].dropna().unique())
        
        if locations:
            selected_location = st.selectbox("📍 Select Location:", locations)
            
            # Filter data for selected location
            location_data = df[df['location'] == selected_location]
            
            if not location_data.empty:
                row = location_data.iloc[0]
                
                st.markdown(f"### 🌤️ Weather Details - {selected_location}")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("#### Current Conditions (from Database)")
                    
                    # Temperature
                    if 'temperature' in row and pd.notna(row['temperature']):
                        temp_unit = row.get('temperature_unit', '°C')
                        st.write(f"🌡️ **Temperature**: {row['temperature']} {temp_unit}")
                    
                    # Weather condition
                    if 'weather_condition' in row and pd.notna(row['weather_condition']):
                        st.write(f"☀️ **Weather**: {row['weather_condition']}")
                    
                    # Rain probability
                    if 'rain_probability' in row and pd.notna(row['rain_probability']):
                        st.write(f"🌧️ **Rain Probability**: {row['rain_probability']}%")
                    
                    # Additional data
                    if 'humidity' in row and pd.notna(row['humidity']):
                        st.write(f"💧 **Humidity**: {row['humidity']}%")
                    
                    if 'wind_speed' in row and pd.notna(row['wind_speed']):
                        st.write(f"💨 **Wind Speed**: {row['wind_speed']} m/s")
                
                with col2:
                    # Temperature gauge
                    if 'temperature' in row and pd.notna(row['temperature']):
                        try:
                            temp_val = float(row['temperature'])
                            
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

def display_earthquake_data_from_db(df, metadata):
    """Display earthquake data from database."""
    
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
        max_mag = df['magnitude_value'].max() if 'magnitude_value' in df.columns and df['magnitude_value'].notna().any() else None
        mag_display = f"{max_mag:.1f}" if max_mag else "N/A"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">📊</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{mag_display}</div>
            <div>Max Magnitude</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_depth = df['depth'].mean() if 'depth' in df.columns and df['depth'].notna().any() else None
        depth_display = f"{avg_depth:.1f} km" if avg_depth else "N/A"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">⬇️</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{depth_display}</div>
            <div>Avg Depth</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        latest_time = df['origin_time'].max() if 'origin_time' in df.columns else None
        time_display = latest_time[11:16] if latest_time and len(latest_time) > 16 else "N/A"
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.5rem;">⏰</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #1976D2;">{time_display}</div>
            <div>Latest Event</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent earthquakes
    st.markdown("### 📋 Recent Earthquake Events (from Database)")
    
    # Sort by origin time
    if 'origin_time' in df.columns:
        df_sorted = df.sort_values('origin_time', ascending=False)
    else:
        df_sorted = df
    
    for idx, eq in df_sorted.head(10).iterrows():
        st.markdown(f"""
        <div class="weather-card">
            <strong>📍 {eq.get('location', 'Unknown')}</strong><br>
            <strong>Magnitude:</strong> {eq.get('magnitude_value', 'N/A')} {eq.get('magnitude_type', '')}<br>
            <strong>Depth:</strong> {eq.get('depth', 'N/A')} km<br>
            <strong>Time:</strong> {eq.get('origin_time', 'N/A')}<br>
            <strong>Earthquake No:</strong> {eq.get('earthquake_no', 'N/A')}
        </div>
        """, unsafe_allow_html=True)

def show_database_status(data_service):
    """Show comprehensive database status."""
    st.markdown("## 📊 Database Status & Management")
    
    # Refresh database status
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Database Status", use_container_width=True):
            st.session_state.db_status = data_service.get_database_status()
            st.rerun()
    
    with col2:
        if st.button("🧹 Cleanup Old Data", use_container_width=True):
            with st.spinner("Cleaning up old data..."):
                data_service.cleanup_old_data(days_to_keep=30)
                st.success("✅ Database cleanup completed!")
    
    # Get current database status
    db_status = st.session_state.db_status or data_service.get_database_status()
    
    # Database statistics
    st.markdown("### 📈 Database Statistics")
    
    db_stats = db_status.get('database_stats', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Weather Records", db_stats.get('weather_forecasts_count', 0))
    
    with col2:
        st.metric("Earthquake Records", db_stats.get('earthquakes_count', 0))
    
    with col3:
        st.metric("API Calls (24h)", db_stats.get('api_logs_count', 0))
    
    with col4:
        st.metric("Database Size", f"{db_stats.get('db_size_mb', 0):.1f} MB")
    
    # Data freshness information
    st.markdown("### 🕒 Data Freshness")
    
    freshness_info = db_status.get('data_freshness', {})
    
    for data_type, info in freshness_info.items():
        age_hours = info.get('age_hours', 0)
        record_count = info.get('record_count', 0)
        last_update = info.get('last_update', '')
        
        # Determine freshness status
        if age_hours < 3:
            status_color = "🟢"
            status_text = "Fresh"
        elif age_hours < 12:
            status_color = "🟡"
            status_text = "Acceptable"
        else:
            status_color = "🔴"
            status_text = "Stale"
        
        st.markdown(f"""
        **{data_type.replace('_', ' ').title()}**: {status_color} {status_text}
        - Records: {record_count}
        - Last Update: {last_update[:19] if last_update else 'Unknown'}
        - Age: {age_hours:.1f} hours
        """)
    
    # Health score and recommendations
    st.markdown("### 💊 System Health")
    
    health_score = db_status.get('health_score', 0)
    recommendations = db_status.get('recommendations', [])
    
    # Health score display
    if health_score >= 80:
        health_color = "#4CAF50"
        health_status = "Excellent"
    elif health_score >= 60:
        health_color = "#ff9800"
        health_status = "Good"
    else:
        health_color = "#f44336"
        health_status = "Needs Attention"
    
    st.markdown(f"""
    <div style="background: {health_color}20; padding: 1rem; border-radius: 10px; border-left: 4px solid {health_color};">
        <h4 style="color: {health_color}; margin: 0;">Health Score: {health_score:.0f}% - {health_status}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    for rec in recommendations:
        st.write(f"• {rec}")

def show_settings_with_db(data_service):
    """Settings page with database management."""
    st.markdown("## ⚙️ Settings & Database Management")
    
    # API connectivity test
    st.markdown("### 📡 API Connectivity")
    
    if st.button("🧪 Test All APIs"):
        with st.spinner("Testing API connectivity..."):
            results = data_service.test_api_connectivity()
            
            for api_name, result in results.items():
                status = result.get('status', 'unknown')
                
                if status == 'online':
                    st.success(f"✅ {api_name}: Online ({result.get('response_time', 0):.2f}s)")
                elif status == 'offline':
                    st.warning(f"⚠️ {api_name}: Offline")
                else:
                    st.error(f"❌ {api_name}: Error - {result.get('error', 'Unknown')}")
    
    # Force data refresh
    st.markdown("### 🔄 Force Data Refresh")
    
    if st.button("🚀 Force Refresh All Data"):
        with st.spinner("Force refreshing all data..."):
            results = data_service.force_refresh_all_data()
            
            for data_type, success in results.items():
                if success:
                    st.success(f"✅ {data_type}: Refreshed successfully")
                else:
                    st.error(f"❌ {data_type}: Refresh failed")
    
    # Data export
    st.markdown("### 💾 Data Export")
    
    if st.button("📤 Export All Data to CSV"):
        with st.spinner("Exporting data..."):
            exports = data_service.export_all_data()
            
            for table, result in exports.items():
                if result.endswith('.csv'):
                    st.success(f"✅ {table}: Exported to {result}")
                else:
                    st.error(f"❌ {table}: {result}")

if __name__ == "__main__":
    main()