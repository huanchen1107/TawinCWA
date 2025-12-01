"""
Beautiful Taiwan Weather Dashboard - Inspired by CWA Design
A stunning web application for Taiwan weather data visualization.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Import our modules
from crawler import DataGovCrawler, CensusCrawler, TWCrawler, DataProcessor
from utils import DataValidator, format_file_size, format_number, truncate_text, TaiwanWeatherProcessor
from config import GOV_DATA_SOURCES, STREAMLIT_CONFIG, DATA_CATEGORIES

# Import beautiful UI components
import sys
sys.path.append('.')
from components.ui_components import *

# Page configuration with beautiful theme
st.set_page_config(
    page_title="Taiwan Weather Center",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with collapsed sidebar for cleaner look
)

# Load custom CSS
try:
    load_custom_css()
except:
    pass  # Fall back to default styling if CSS fails to load

# Initialize session state
if 'datasets' not in st.session_state:
    st.session_state.datasets = []
if 'selected_dataset' not in st.session_state:
    st.session_state.selected_dataset = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'current_weather_data' not in st.session_state:
    st.session_state.current_weather_data = None

def init_crawlers():
    """Initialize crawler instances."""
    crawlers = {}
    try:
        crawlers['taiwan_cwa'] = TWCrawler(GOV_DATA_SOURCES['taiwan_cwa'])
        crawlers['data.gov'] = DataGovCrawler(GOV_DATA_SOURCES['data.gov'])
        crawlers['census.gov'] = CensusCrawler(GOV_DATA_SOURCES['census.gov'])
    except Exception as e:
        st.error(f"Failed to initialize crawlers: {e}")
    return crawlers

def main():
    """Main application function with beautiful UI."""
    
    # Create hero section
    create_hero_section()
    
    # Navigation tabs with beautiful styling
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌤️ Weather Dashboard", 
        "🌏 Earthquake Monitor", 
        "🌊 Marine Weather", 
        "📊 Data Explorer",
        "⚙️ Settings"
    ])
    
    with tab1:
        show_weather_dashboard()
    
    with tab2:
        show_earthquake_monitor()
    
    with tab3:
        show_marine_weather()
    
    with tab4:
        show_data_explorer()
    
    with tab5:
        show_settings()

def show_weather_dashboard():
    """Beautiful weather dashboard page."""
    create_page_header("Weather Dashboard", "Real-time weather conditions across Taiwan", "🌦️")
    
    # Initialize crawlers
    crawlers = init_crawlers()
    taiwan_crawler = crawlers.get('taiwan_cwa')
    
    if not taiwan_crawler:
        st.error("❌ Taiwan CWA crawler not available")
        return
    
    # Quick weather status cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Weather Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        show_alerts = st.checkbox("⚠️ Show Weather Alerts", value=True)
    
    with col3:
        auto_refresh = st.checkbox("🔄 Auto Refresh (5min)", value=False)
    
    # Load current weather data
    with st.spinner("🌤️ Loading current weather conditions..."):
        try:
            # Get 36-hour forecast data
            forecast_data = taiwan_crawler.get_dataset_data("F-A0010-001")
            
            if forecast_data:
                taiwan_processor = TaiwanWeatherProcessor()
                df = taiwan_processor.process_weather_forecast(forecast_data)
                
                if df is not None and not df.empty:
                    display_beautiful_weather_forecast(df, taiwan_processor, show_alerts)
                else:
                    st.warning("⚠️ Unable to process weather data at this time")
            else:
                st.error("❌ Unable to fetch weather data. Please try again later.")
                
        except Exception as e:
            st.error(f"❌ Error loading weather data: {e}")

def display_beautiful_weather_forecast(df: pd.DataFrame, processor: TaiwanWeatherProcessor, show_alerts: bool):
    """Display weather forecast with beautiful UI."""
    
    # Weather alerts section
    if show_alerts:
        alerts = processor.create_weather_alerts(df)
        if alerts:
            st.markdown("### ⚠️ Active Weather Alerts")
            
            # Group alerts by severity
            high_alerts = [a for a in alerts if a['severity'] == 'warning']
            info_alerts = [a for a in alerts if a['severity'] == 'info']
            
            if high_alerts:
                for alert in high_alerts[:3]:
                    create_alert_card(
                        alert['type'], 
                        alert['message'], 
                        "high", 
                        alert['location']
                    )
            
            if info_alerts:
                with st.expander(f"📋 View {len(info_alerts)} Additional Alerts"):
                    for alert in info_alerts:
                        create_alert_card(
                            alert['type'], 
                            alert['message'], 
                            "low", 
                            alert['location']
                        )
    
    # Location selector
    if 'location' in df.columns:
        locations = sorted(df['location'].unique())
        
        # Major cities first
        major_cities = ['臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市']
        priority_locations = [loc for loc in major_cities if loc in locations]
        other_locations = [loc for loc in locations if loc not in major_cities]
        ordered_locations = priority_locations + other_locations
        
        selected_location = create_location_selector(ordered_locations, default_location='臺北市')
        
        # Filter data for selected location
        location_data = df[df['location'] == selected_location]
        
        if not location_data.empty:
            location_row = location_data.iloc[0]
            
            # Beautiful weather summary
            st.markdown(f"### 🌤️ Current Conditions - {selected_location}")
            
            # Extract key weather data
            weather_summary = extract_weather_summary(location_row)
            create_weather_summary_grid(weather_summary)
            
            # Detailed weather information
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Weather details table
                st.markdown("#### 📋 Detailed Forecast")
                display_weather_details_table(location_row, df.columns)
            
            with col2:
                # Temperature gauge if temperature data available
                temp_cols = [col for col in df.columns if 'T_' in col and 'value' in col]
                if temp_cols:
                    try:
                        temp_value = location_row.get(temp_cols[0], '')
                        if temp_value and str(temp_value).replace('.', '').isdigit():
                            create_temperature_gauge(float(temp_value))
                    except:
                        st.info("🌡️ Temperature gauge unavailable")
    
    # Taiwan weather map
    st.markdown("### 🗺️ Taiwan Weather Overview")
    create_taiwan_weather_map(df)

def extract_weather_summary(location_row: pd.Series) -> dict:
    """Extract weather summary from location data."""
    summary = {}
    
    # Temperature
    temp_cols = [col for col in location_row.index if 'T_' in col and 'value' in col]
    if temp_cols:
        temp_value = location_row.get(temp_cols[0], 'N/A')
        temp_unit = location_row.get(temp_cols[0].replace('value', 'unit'), '°C')
        summary['temperature'] = f"{temp_value} {temp_unit}"
    
    # Weather description
    wx_cols = [col for col in location_row.index if 'Wx_' in col and 'name' in col]
    if wx_cols:
        summary['condition'] = location_row.get(wx_cols[0], 'N/A')
    
    # Rain probability
    pop_cols = [col for col in location_row.index if 'PoP_' in col and 'value' in col]
    if pop_cols:
        pop_value = location_row.get(pop_cols[0], 'N/A')
        pop_unit = location_row.get(pop_cols[0].replace('value', 'unit'), '%')
        summary['rain_probability'] = f"{pop_value} {pop_unit}"
    
    # Wind
    wind_cols = [col for col in location_row.index if 'WS_' in col and 'value' in col]
    if wind_cols:
        wind_value = location_row.get(wind_cols[0], 'N/A')
        wind_unit = location_row.get(wind_cols[0].replace('value', 'unit'), 'm/s')
        summary['wind_speed'] = f"{wind_value} {wind_unit}"
    
    # Humidity
    rh_cols = [col for col in location_row.index if 'RH_' in col and 'value' in col]
    if rh_cols:
        rh_value = location_row.get(rh_cols[0], 'N/A')
        rh_unit = location_row.get(rh_cols[0].replace('value', 'unit'), '%')
        summary['humidity'] = f"{rh_value} {rh_unit}"
    
    return summary

def display_weather_details_table(location_row: pd.Series, all_columns: list):
    """Display detailed weather information in a beautiful table."""
    details = []
    
    for col in all_columns:
        if '_name' in col or '_value' in col:
            base_name = col.replace('_name', '').replace('_value', '')
            
            # Skip if we already processed this parameter
            if any(d['Parameter'] == base_name for d in details):
                continue
            
            name_col = f"{base_name}_name"
            value_col = f"{base_name}_value" 
            unit_col = f"{base_name}_unit"
            start_col = f"{base_name}_start"
            end_col = f"{base_name}_end"
            
            if name_col in location_row.index or value_col in location_row.index:
                detail = {
                    'Parameter': base_name,
                    'Description': location_row.get(name_col, ''),
                    'Value': location_row.get(value_col, ''),
                    'Unit': location_row.get(unit_col, ''),
                    'Period': f"{location_row.get(start_col, '')[:16]} - {location_row.get(end_col, '')[:16]}" if location_row.get(start_col) else ''
                }
                
                # Create display value
                if detail['Value'] and detail['Unit']:
                    detail['Display'] = f"{detail['Value']} {detail['Unit']}"
                elif detail['Description']:
                    detail['Display'] = detail['Description']
                else:
                    detail['Display'] = detail['Value'] or 'N/A'
                
                details.append(detail)
    
    if details:
        # Create a clean display DataFrame
        display_data = []
        for detail in details:
            if detail['Display'] != 'N/A' and detail['Display'].strip():
                display_data.append({
                    'Weather Parameter': detail['Parameter'],
                    'Current Value': detail['Display'],
                    'Valid Period': detail['Period'][:32] + '...' if len(detail['Period']) > 35 else detail['Period']
                })
        
        if display_data:
            df_display = pd.DataFrame(display_data)
            st.dataframe(df_display, use_container_width=True, hide_index=True)

def create_taiwan_weather_map(df: pd.DataFrame):
    """Create a beautiful Taiwan weather overview map."""
    if df is None or df.empty:
        st.info("🗺️ Weather map data not available")
        return
    
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
            
            # Get temperature for color coding
            temp_cols = [col for col in df.columns if 'T_' in col and 'value' in col]
            temp_value = None
            if temp_cols:
                try:
                    temp_str = str(row.get(temp_cols[0], ''))
                    if temp_str.replace('.', '').replace('-', '').isdigit():
                        temp_value = float(temp_str)
                except:
                    temp_value = None
            
            # Get weather condition
            wx_cols = [col for col in df.columns if 'Wx_' in col and 'name' in col]
            weather_condition = row.get(wx_cols[0], '') if wx_cols else ''
            
            map_data.append({
                'location': location,
                'latitude': lat,
                'longitude': lon,
                'temperature': temp_value,
                'weather': weather_condition
            })
    
    if map_data:
        map_df = pd.DataFrame(map_data)
        
        # Create the map
        fig = px.scatter_mapbox(
            map_df, 
            lat="latitude", 
            lon="longitude",
            hover_name="location",
            hover_data=["temperature", "weather"],
            color="temperature",
            size_max=15,
            zoom=7,
            height=500,
            color_continuous_scale="RdYlBu_r",
            title="🌤️ Taiwan Weather Overview"
        )
        
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(
                center=dict(lat=23.8, lon=120.9),
                zoom=7
            ),
            margin={"r":0,"t":30,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_earthquake_monitor():
    """Beautiful earthquake monitoring page."""
    create_page_header("Earthquake Monitor", "Real-time seismic activity monitoring", "🌏")
    
    # Initialize crawler
    crawlers = init_crawlers()
    taiwan_crawler = crawlers.get('taiwan_cwa')
    
    if not taiwan_crawler:
        st.error("❌ Taiwan CWA crawler not available")
        return
    
    # Control panel
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Earthquake Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        magnitude_filter = st.slider("Min Magnitude", 0.0, 8.0, 0.0, 0.1)
    
    with col3:
        show_map = st.checkbox("🗺️ Show Earthquake Map", value=True)
    
    # Load earthquake data
    with st.spinner("🌏 Loading earthquake data..."):
        try:
            earthquake_data = taiwan_crawler.get_dataset_data("E-A0015-001")
            
            if earthquake_data:
                taiwan_processor = TaiwanWeatherProcessor()
                df = taiwan_processor.process_earthquake_data(earthquake_data)
                
                if df is not None and not df.empty:
                    display_beautiful_earthquake_data(df, magnitude_filter, show_map)
                else:
                    st.warning("⚠️ No earthquake data available")
            else:
                st.error("❌ Unable to fetch earthquake data")
                
        except Exception as e:
            st.error(f"❌ Error loading earthquake data: {e}")

def display_beautiful_earthquake_data(df: pd.DataFrame, magnitude_filter: float, show_map: bool):
    """Display earthquake data with beautiful UI."""
    
    # Filter by magnitude
    df_filtered = df.copy()
    if 'magnitude_value' in df.columns:
        magnitudes = pd.to_numeric(df['magnitude_value'], errors='coerce')
        df_filtered = df[magnitudes >= magnitude_filter]
    
    # Summary metrics
    if not df_filtered.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card("Total Events", str(len(df_filtered)), icon="🌏")
        
        with col2:
            if 'magnitude_value' in df_filtered.columns:
                mags = pd.to_numeric(df_filtered['magnitude_value'], errors='coerce').dropna()
                max_mag = mags.max() if not mags.empty else 0
                create_metric_card("Max Magnitude", f"{max_mag:.1f}", icon="📊")
        
        with col3:
            if 'depth' in df_filtered.columns:
                depths = pd.to_numeric(df_filtered['depth'], errors='coerce').dropna()
                avg_depth = depths.mean() if not depths.empty else 0
                create_metric_card("Avg Depth", f"{avg_depth:.1f} km", icon="⬇️")
        
        with col4:
            if 'origin_time' in df_filtered.columns:
                latest = df_filtered['origin_time'].max()
                create_metric_card("Latest Event", latest[:10] if latest else "N/A", icon="⏰")
    
    # Recent earthquakes
    if not df_filtered.empty and 'origin_time' in df_filtered.columns:
        st.markdown("### 📋 Recent Earthquake Events")
        
        df_sorted = df_filtered.sort_values('origin_time', ascending=False)
        
        for idx, eq in df_sorted.head(5).iterrows():
            with st.container():
                st.markdown(f"""
                <div class="weather-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #1976D2;">📍 {eq.get('location', 'Unknown Location')}</h4>
                            <p style="margin: 0.5rem 0; color: #666;">
                                <strong>Time:</strong> {eq.get('origin_time', 'N/A')}<br>
                                <strong>Magnitude:</strong> {eq.get('magnitude_value', 'N/A')} {eq.get('magnitude_type', '')}<br>
                                <strong>Depth:</strong> {eq.get('depth', 'N/A')} km
                            </p>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; font-weight: bold; color: #1976D2;">
                                {eq.get('magnitude_value', 'N/A')}
                            </div>
                            <div style="font-size: 0.9rem; color: #666;">Magnitude</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if eq.get('web_url'):
                    st.markdown(f"[📄 View Detailed Report]({eq.get('web_url')})")

def show_marine_weather():
    """Beautiful marine weather page."""
    create_page_header("Marine Weather", "Ocean and coastal weather conditions", "🌊")
    
    st.markdown("""
    <div class="weather-card">
        <h3 style="color: #1976D2; margin-bottom: 1rem;">🚧 Marine Weather Coming Soon</h3>
        <p>This section will include:</p>
        <ul>
            <li>🌊 Ocean wave heights and periods</li>
            <li>🌬️ Marine wind conditions</li>
            <li>🌡️ Sea surface temperatures</li>
            <li>⛵ Sailing and fishing advisories</li>
            <li>🌪️ Typhoon tracking</li>
        </ul>
        <p>Marine weather data integration is in development.</p>
    </div>
    """, unsafe_allow_html=True)

def show_data_explorer():
    """Beautiful data explorer page."""
    create_page_header("Data Explorer", "Search and analyze government datasets", "📊")
    
    # Data source status
    st.markdown("### 📡 Data Source Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_data_source_card(
            "Taiwan CWA",
            "Real-time weather, earthquake, and marine data from Taiwan Central Weather Administration",
            "online",
            12
        )
    
    with col2:
        create_data_source_card(
            "Data.gov",
            "US Federal government open datasets covering various sectors and agencies",
            "online", 
            250000
        )
    
    with col3:
        create_data_source_card(
            "Census.gov",
            "US Census Bureau demographic, economic, and geographic data",
            "online",
            500
        )
    
    # Quick search
    st.markdown("### 🔍 Quick Dataset Search")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "",
            placeholder="🔍 Search for datasets (e.g., climate, population, economy)...",
            key="search_input"
        )
    
    with col2:
        if st.button("🔍 Search Datasets", use_container_width=True):
            if search_query:
                perform_beautiful_search(search_query)

def perform_beautiful_search(query: str):
    """Perform a beautiful dataset search."""
    crawlers = init_crawlers()
    
    with st.spinner(f"🔍 Searching for '{query}'..."):
        all_results = []
        
        # Search Taiwan CWA first
        if 'taiwan_cwa' in crawlers:
            try:
                results = crawlers['taiwan_cwa'].search_datasets(query, limit=20)
                all_results.extend(results)
            except Exception as e:
                st.warning(f"Taiwan CWA search error: {e}")
        
        # Search other sources
        for source in ['data.gov', 'census.gov']:
            if source in crawlers:
                try:
                    results = crawlers[source].search_datasets(query, limit=10)
                    all_results.extend(results)
                except Exception as e:
                    st.warning(f"{source} search error: {e}")
        
        if all_results:
            st.success(f"✅ Found {len(all_results)} datasets")
            
            # Display results beautifully
            for i, dataset in enumerate(all_results[:10]):
                with st.container():
                    st.markdown(f"""
                    <div class="data-source-card">
                        <div style="margin-bottom: 1rem;">
                            <h4 style="color: #1976D2; margin: 0;">{dataset.get('title', 'Unknown Dataset')}</h4>
                            <span style="background: #E3F2FD; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; color: #1976D2;">
                                {dataset.get('source', 'Unknown Source')}
                            </span>
                        </div>
                        <p style="color: #666; margin-bottom: 1rem;">
                            {truncate_text(dataset.get('description', 'No description'), 150)}
                        </p>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <small style="color: #999;">Organization: {dataset.get('organization', 'Unknown')}</small><br>
                                <small style="color: #999;">Resources: {dataset.get('resources', 0)}</small>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if dataset.get('url'):
                        st.markdown(f"[🔗 View Dataset]({dataset['url']})")
        else:
            st.warning("⚠️ No datasets found. Try different keywords.")

def show_settings():
    """Beautiful settings page."""
    create_page_header("Settings", "Configure your dashboard preferences", "⚙️")
    
    # API Configuration
    st.markdown("### 🔑 API Configuration")
    
    with st.container():
        st.markdown("""
        <div class="weather-card">
            <h4 style="color: #1976D2; margin-bottom: 1rem;">Taiwan CWA API</h4>
            <p>Current API Key: <code>CWA-1FFDDAEC-161F-46A3-BE71-93C32C52829F</code></p>
            <p style="color: #666; font-size: 0.9rem;">
                ✅ Status: Active and configured<br>
                🔄 Rate Limit: 1 request per second<br>
                📊 Daily Quota: Available
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Dashboard Preferences
    st.markdown("### 🎨 Dashboard Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="weather-card">
            <h5 style="color: #1976D2;">Display Options</h5>
        </div>
        """, unsafe_allow_html=True)
        
        auto_refresh = st.checkbox("🔄 Auto-refresh weather data", value=False)
        show_detailed_alerts = st.checkbox("⚠️ Show detailed weather alerts", value=True)
        celsius_temp = st.checkbox("🌡️ Temperature in Celsius", value=True)
    
    with col2:
        st.markdown("""
        <div class="weather-card">
            <h5 style="color: #1976D2;">Data Sources</h5>
        </div>
        """, unsafe_allow_html=True)
        
        enable_taiwan = st.checkbox("🌤️ Taiwan weather data", value=True)
        enable_earthquake = st.checkbox("🌏 Earthquake monitoring", value=True)
        enable_marine = st.checkbox("🌊 Marine weather", value=False, disabled=True)
    
    # System Status
    st.markdown("### 📊 System Status")
    
    crawlers = init_crawlers()
    
    for source_name, crawler in crawlers.items():
        status_icon = "🟢"
        status_text = "Online"
        
        try:
            is_healthy = crawler.health_check()
            if not is_healthy:
                status_icon = "🔴"
                status_text = "Offline"
        except:
            status_icon = "🟡"
            status_text = "Unknown"
        
        st.markdown(f"""
        <div class="data-source-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h5 style="margin: 0; color: #1976D2;">{source_name}</h5>
                    <small style="color: #666;">Data crawler service</small>
                </div>
                <div>
                    <span>{status_icon} {status_text}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()