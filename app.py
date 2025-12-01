"""
Government Open Data Crawler - Streamlit App
A web application for crawling and analyzing government open data.
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

# Page configuration
st.set_page_config(**STREAMLIT_CONFIG)

# Initialize session state
if 'datasets' not in st.session_state:
    st.session_state.datasets = []
if 'selected_dataset' not in st.session_state:
    st.session_state.selected_dataset = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

def init_crawlers():
    """Initialize crawler instances."""
    crawlers = {}
    try:
        crawlers['data.gov'] = DataGovCrawler(GOV_DATA_SOURCES['data.gov'])
        crawlers['census.gov'] = CensusCrawler(GOV_DATA_SOURCES['census.gov'])
        crawlers['taiwan_cwa'] = TWCrawler(GOV_DATA_SOURCES['taiwan_cwa'])
    except Exception as e:
        st.error(f"Failed to initialize crawlers: {e}")
    return crawlers

def main():
    """Main application function."""
    
    # Sidebar
    st.sidebar.title("🏛️ Gov Data Crawler")
    st.sidebar.markdown("Navigate through government open data sources")
    
    # Navigation
    pages = {
        "🏠 Home": show_home_page,
        "🔍 Search Data": show_search_page,
        "📊 Browse Datasets": show_browse_page,
        "📈 Data Analysis": show_analysis_page,
        "🌤️ Taiwan Weather": show_taiwan_weather_page,
        "⚙️ Settings": show_settings_page
    }
    
    selected_page = st.sidebar.selectbox("Choose a page:", list(pages.keys()))
    
    # Show selected page
    pages[selected_page]()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("Built with ❤️ using Streamlit")
    st.sidebar.markdown("[GitHub Repository](https://github.com/yourusername/gov-data-crawler)")

def show_home_page():
    """Display home page."""
    st.title("🏛️ Government Open Data Crawler")
    st.markdown("""
    Welcome to the Government Open Data Crawler! This application helps you discover, 
    download, and analyze open datasets from various government sources.
    """)
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Data Sources", "3", help="data.gov, census.gov, and Taiwan CWA")
    
    with col2:
        st.metric("Cached Datasets", len(st.session_state.datasets))
    
    with col3:
        st.metric("Categories", len(DATA_CATEGORIES))
    
    with col4:
        st.metric("Status", "🟢 Online", help="All services are operational")
    
    # Featured data sources
    st.header("📊 Featured Data Sources")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📈 Data.gov")
        st.markdown("""
        - **250,000+** datasets
        - Federal, state, and local data
        - Multiple formats (CSV, JSON, XML)
        - Real-time and historical data
        """)
        if st.button("Explore Data.gov", key="explore_datagov"):
            st.session_state.selected_source = "data.gov"
            st.experimental_rerun()
    
    with col2:
        st.subheader("🏢 Census.gov")
        st.markdown("""
        - Population and housing data
        - Economic indicators
        - Demographic statistics
        - Geographic data
        """)
        if st.button("Explore Census.gov", key="explore_census"):
            st.session_state.selected_source = "census.gov"
            st.experimental_rerun()
    
    with col3:
        st.subheader("🌤️ Taiwan CWA")
        st.markdown("""
        - **Real-time weather data**
        - Weather forecasts (36-hour)
        - Earthquake monitoring
        - Marine conditions
        - Air quality data
        """)
        if st.button("Explore Taiwan Weather", key="explore_taiwan"):
            st.session_state.selected_source = "taiwan_cwa"
            st.experimental_rerun()
    
    # Recent activity
    if st.session_state.datasets:
        st.header("📋 Recent Searches")
        for i, dataset in enumerate(st.session_state.datasets[:5]):
            with st.expander(f"📄 {truncate_text(dataset.get('title', 'Unknown'), 60)}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Source:** {dataset.get('source', 'Unknown')}")
                    st.write(f"**Description:** {truncate_text(dataset.get('description', 'No description'), 150)}")
                with col2:
                    if st.button("View", key=f"view_{i}"):
                        st.session_state.selected_dataset = dataset
                        st.experimental_rerun()

def show_search_page():
    """Display search page."""
    st.title("🔍 Search Government Data")
    
    # Initialize crawlers
    crawlers = init_crawlers()
    
    # Search form
    with st.form("search_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input(
                "Search for datasets:",
                placeholder="e.g., COVID-19, climate change, employment statistics"
            )
        
        with col2:
            data_source = st.selectbox(
                "Data Source:",
                ["All", "data.gov", "census.gov", "taiwan_cwa"]
            )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category = st.selectbox(
                "Category:",
                ["All"] + DATA_CATEGORIES
            )
        
        with col2:
            max_results = st.slider("Max Results:", 10, 100, 50)
        
        with col3:
            st.write("")  # Spacing
            search_button = st.form_submit_button("🔍 Search", use_container_width=True)
    
    # Perform search
    if search_button and search_query:
        with st.spinner("Searching government datasets..."):
            all_results = []
            
            sources_to_search = [data_source] if data_source != "All" else ["data.gov", "census.gov", "taiwan_cwa"]
            
            for source in sources_to_search:
                if source in crawlers:
                    try:
                        category_filter = None if category == "All" else category
                        results = crawlers[source].search_datasets(
                            search_query, 
                            category_filter, 
                            max_results
                        )
                        all_results.extend(results)
                    except Exception as e:
                        st.error(f"Error searching {source}: {e}")
            
            # Store results
            st.session_state.datasets = all_results
            
            # Display results
            if all_results:
                st.success(f"Found {len(all_results)} datasets")
                display_search_results(all_results)
            else:
                st.warning("No datasets found for your query. Try different keywords or check your internet connection.")

def display_search_results(datasets):
    """Display search results."""
    for i, dataset in enumerate(datasets):
        with st.expander(f"📄 {dataset.get('title', 'Unknown Dataset')}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Organization:** {dataset.get('organization', 'Unknown')}")
                st.write(f"**Source:** {dataset.get('source', 'Unknown')}")
                st.write(f"**Description:** {truncate_text(dataset.get('description', 'No description'), 200)}")
                
                # Tags
                tags = dataset.get('tags', [])
                if tags:
                    st.write(f"**Tags:** {', '.join(tags[:5])}")
                
                # Last modified
                if dataset.get('last_modified'):
                    st.write(f"**Last Modified:** {dataset.get('last_modified')}")
            
            with col2:
                st.write(f"**Resources:** {dataset.get('resources', 0)}")
                
                if st.button("📊 Analyze", key=f"analyze_{i}"):
                    st.session_state.selected_dataset = dataset
                    analyze_dataset(dataset)
                
                if st.button("🔗 View Online", key=f"view_online_{i}"):
                    if dataset.get('url'):
                        st.markdown(f"[Open Dataset]({dataset['url']})")
                        st.success("Link opened! Check the new tab.")

def show_browse_page():
    """Display browse page for cached datasets."""
    st.title("📊 Browse Datasets")
    
    if not st.session_state.datasets:
        st.info("No datasets cached yet. Go to the Search page to find datasets!")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        source_filter = st.selectbox(
            "Filter by Source:",
            ["All"] + list(set(d.get('source', 'Unknown') for d in st.session_state.datasets))
        )
    
    with col2:
        org_filter = st.selectbox(
            "Filter by Organization:",
            ["All"] + list(set(d.get('organization', 'Unknown') for d in st.session_state.datasets))
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by:",
            ["Title", "Organization", "Last Modified", "Resources"]
        )
    
    # Apply filters
    filtered_datasets = st.session_state.datasets
    
    if source_filter != "All":
        filtered_datasets = [d for d in filtered_datasets if d.get('source') == source_filter]
    
    if org_filter != "All":
        filtered_datasets = [d for d in filtered_datasets if d.get('organization') == org_filter]
    
    # Sort datasets
    sort_key_map = {
        "Title": "title",
        "Organization": "organization",
        "Last Modified": "last_modified",
        "Resources": "resources"
    }
    
    try:
        filtered_datasets.sort(
            key=lambda x: x.get(sort_key_map[sort_by], ''),
            reverse=(sort_by in ["Last Modified", "Resources"])
        )
    except:
        pass  # Keep original order if sorting fails
    
    # Display datasets
    st.write(f"**Showing {len(filtered_datasets)} of {len(st.session_state.datasets)} datasets**")
    
    for i, dataset in enumerate(filtered_datasets):
        with st.container():
            col1, col2, col3 = st.columns([6, 2, 2])
            
            with col1:
                st.subheader(truncate_text(dataset.get('title', 'Unknown'), 80))
                st.write(truncate_text(dataset.get('description', 'No description'), 150))
                
                # Metadata
                metadata_cols = st.columns(4)
                with metadata_cols[0]:
                    st.caption(f"**Source:** {dataset.get('source', 'Unknown')}")
                with metadata_cols[1]:
                    st.caption(f"**Org:** {truncate_text(dataset.get('organization', 'Unknown'), 20)}")
                with metadata_cols[2]:
                    st.caption(f"**Resources:** {dataset.get('resources', 0)}")
                with metadata_cols[3]:
                    if dataset.get('last_modified'):
                        st.caption(f"**Modified:** {dataset.get('last_modified')[:10]}")
            
            with col2:
                if st.button("📊 Analyze", key=f"browse_analyze_{i}"):
                    analyze_dataset(dataset)
            
            with col3:
                if st.button("🔗 View", key=f"browse_view_{i}"):
                    st.session_state.selected_dataset = dataset
            
            st.divider()

def show_analysis_page():
    """Display data analysis page."""
    st.title("📈 Data Analysis")
    
    if not st.session_state.selected_dataset:
        st.info("Select a dataset from the Browse or Search page to start analysis.")
        return
    
    dataset = st.session_state.selected_dataset
    st.subheader(f"Analyzing: {dataset.get('title', 'Unknown Dataset')}")
    
    # Dataset info
    with st.expander("ℹ️ Dataset Information", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Source:** {dataset.get('source', 'Unknown')}")
            st.write(f"**Organization:** {dataset.get('organization', 'Unknown')}")
            st.write(f"**Resources:** {dataset.get('resources', 0)}")
        
        with col2:
            if dataset.get('url'):
                st.markdown(f"**URL:** [{dataset.get('url')}]({dataset.get('url')})")
            if dataset.get('last_modified'):
                st.write(f"**Last Modified:** {dataset.get('last_modified')}")
    
    # Load and process data
    if st.button("📥 Load Dataset", use_container_width=True):
        load_and_analyze_dataset(dataset)
    
    # Display analysis if data is loaded
    if st.session_state.processed_data is not None:
        display_data_analysis(st.session_state.processed_data)

def load_and_analyze_dataset(dataset):
    """Load and analyze a dataset."""
    crawlers = init_crawlers()
    processor = DataProcessor()
    validator = DataValidator()
    
    with st.spinner("Loading dataset..."):
        try:
            source = dataset.get('source', '')
            
            if source in crawlers:
                # Get dataset data
                raw_data = crawlers[source].get_dataset_data(dataset['id'])
                
                if raw_data:
                    # Process data
                    df = processor.standardize_dataset(raw_data, source)
                    
                    if df is not None and not df.empty:
                        df = processor.clean_dataset(df)
                        
                        # Validate data
                        is_valid, issues = validator.validate_dataset(df)
                        quality_score = validator.get_data_quality_score(df)
                        
                        st.session_state.processed_data = {
                            'dataframe': df,
                            'summary': processor.get_dataset_summary(df),
                            'quality_score': quality_score,
                            'validation_issues': issues,
                            'is_valid': is_valid
                        }
                        
                        st.success("Dataset loaded successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to process dataset data.")
                else:
                    st.error("Failed to load dataset data.")
            else:
                st.error(f"No crawler available for source: {source}")
                
        except Exception as e:
            st.error(f"Error loading dataset: {e}")

def display_data_analysis(processed_data):
    """Display data analysis results."""
    df = processed_data['dataframe']
    summary = processed_data['summary']
    quality_score = processed_data['quality_score']
    
    # Data quality metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Quality Score", f"{quality_score:.1f}/100")
    
    with col2:
        st.metric("Total Rows", format_number(summary.get('total_rows', 0)))
    
    with col3:
        st.metric("Total Columns", summary.get('total_columns', 0))
    
    with col4:
        st.metric("Missing Values", format_number(summary.get('missing_values', 0)))
    
    # Data preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(100), use_container_width=True)
    
    # Data summary
    with st.expander("📊 Data Summary"):
        st.json(summary)
    
    # Simple visualizations
    if len(df) > 0:
        st.subheader("📈 Quick Visualizations")
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            col1, col2 = st.columns(2)
            
            with col1:
                selected_col = st.selectbox("Select column for histogram:", numeric_cols)
                if selected_col:
                    fig = px.histogram(df, x=selected_col, title=f"Distribution of {selected_col}")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if len(numeric_cols) >= 2:
                    col_x = st.selectbox("X-axis:", numeric_cols, key="scatter_x")
                    col_y = st.selectbox("Y-axis:", numeric_cols, index=1, key="scatter_y")
                    
                    if col_x and col_y:
                        fig = px.scatter(df, x=col_x, y=col_y, title=f"{col_y} vs {col_x}")
                        st.plotly_chart(fig, use_container_width=True)
    
    # Export options
    st.subheader("💾 Export Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📊 Download Excel"):
            # Note: This would need additional implementation for Excel export
            st.info("Excel export functionality coming soon!")
    
    with col3:
        if st.button("🔗 Download JSON"):
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def analyze_dataset(dataset):
    """Quick analysis trigger."""
    st.session_state.selected_dataset = dataset
    st.experimental_rerun()

def show_taiwan_weather_page():
    """Display Taiwan weather dashboard."""
    st.title("🌤️ Taiwan Weather Dashboard")
    st.markdown("Real-time weather data from Taiwan Central Weather Administration")
    
    # Initialize crawlers
    crawlers = init_crawlers()
    taiwan_crawler = crawlers.get('taiwan_cwa')
    
    if not taiwan_crawler:
        st.error("Taiwan CWA crawler not available")
        return
    
    # Weather data type selector
    col1, col2 = st.columns([2, 1])
    
    with col1:
        weather_type = st.selectbox(
            "Select Weather Data Type:",
            [
                "Weather Forecast (36-hour)",
                "Current Weather Observations", 
                "Earthquake Reports",
                "Marine Weather",
                "Air Quality"
            ]
        )
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            # Clear cache for fresh data
            st.cache_data.clear()
            st.rerun()
    
    # Map weather type to endpoint
    endpoint_map = {
        "Weather Forecast (36-hour)": "F-A0010-001",
        "Current Weather Observations": "O-A0003-001",
        "Earthquake Reports": "E-A0015-001",
        "Marine Weather": "F-A0012-001",
        "Air Quality": "F-A0086-001"
    }
    
    endpoint_id = endpoint_map.get(weather_type)
    
    if not endpoint_id:
        st.warning("Selected weather type not yet implemented")
        return
    
    # Load and display weather data
    with st.spinner(f"Loading {weather_type.lower()}..."):
        try:
            raw_data = taiwan_crawler.get_dataset_data(endpoint_id)
            
            if not raw_data:
                st.error("Failed to load weather data. Please check your connection.")
                return
            
            # Process data based on type
            taiwan_processor = TaiwanWeatherProcessor()
            
            if "Forecast" in weather_type:
                df = taiwan_processor.process_weather_forecast(raw_data)
                display_weather_forecast(df, raw_data)
                
            elif "Current" in weather_type:
                df = taiwan_processor.process_current_weather(raw_data)
                display_current_weather(df, raw_data)
                
            elif "Earthquake" in weather_type:
                df = taiwan_processor.process_earthquake_data(raw_data)
                display_earthquake_data(df, raw_data)
                
            else:
                # Generic display for other data types
                st.subheader("📊 Raw Data")
                if isinstance(raw_data, dict):
                    st.json(raw_data)
                else:
                    st.write(raw_data)
            
        except Exception as e:
            st.error(f"Error loading weather data: {e}")
            st.exception(e)

def display_weather_forecast(df: pd.DataFrame, raw_data: dict):
    """Display weather forecast data."""
    if df is None or df.empty:
        st.warning("No forecast data available")
        return
    
    st.subheader("🌦️ 36-Hour Weather Forecast")
    
    # Weather alerts
    taiwan_processor = TaiwanWeatherProcessor()
    alerts = taiwan_processor.create_weather_alerts(df)
    
    if alerts:
        st.subheader("⚠️ Weather Alerts")
        for alert in alerts[:5]:  # Show top 5 alerts
            if alert['severity'] == 'warning':
                st.warning(f"**{alert['location']}**: {alert['message']}")
            else:
                st.info(f"**{alert['location']}**: {alert['message']}")
    
    # Location selector
    if 'location' in df.columns:
        locations = df['location'].unique()
        selected_location = st.selectbox("Select Location:", locations)
        
        # Filter data for selected location
        location_data = df[df['location'] == selected_location]
        
        if not location_data.empty:
            st.subheader(f"Weather Details for {selected_location}")
            
            # Display key weather parameters
            location_row = location_data.iloc[0]
            
            # Temperature
            temp_cols = [col for col in df.columns if 'T_' in col and 'value' in col]
            wx_cols = [col for col in df.columns if 'Wx_' in col and 'name' in col]
            pop_cols = [col for col in df.columns if 'PoP_' in col and 'value' in col]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if temp_cols:
                    temp_value = location_row.get(temp_cols[0], 'N/A')
                    temp_unit = location_row.get(temp_cols[0].replace('value', 'unit'), '°C')
                    st.metric("Temperature", f"{temp_value} {temp_unit}")
            
            with col2:
                if wx_cols:
                    weather_desc = location_row.get(wx_cols[0], 'N/A')
                    st.metric("Weather", weather_desc)
            
            with col3:
                if pop_cols:
                    pop_value = location_row.get(pop_cols[0], 'N/A')
                    pop_unit = location_row.get(pop_cols[0].replace('value', 'unit'), '%')
                    st.metric("Rain Probability", f"{pop_value} {pop_unit}")
            
            # Detailed forecast table
            st.subheader("📋 Detailed Forecast")
            
            # Prepare display data
            display_data = {}
            for col in location_data.columns:
                if '_name' in col or '_value' in col:
                    clean_name = col.replace('_name', '').replace('_value', '')
                    if clean_name not in display_data:
                        display_data[clean_name] = {}
                    
                    if '_name' in col:
                        display_data[clean_name]['Description'] = location_row.get(col, '')
                    elif '_value' in col:
                        unit_col = col.replace('_value', '_unit')
                        unit = location_row.get(unit_col, '')
                        value = location_row.get(col, '')
                        display_data[clean_name]['Value'] = f"{value} {unit}".strip()
            
            # Display as table
            if display_data:
                forecast_df = pd.DataFrame(display_data).T
                st.dataframe(forecast_df, use_container_width=True)
    
    # Full data table
    with st.expander("📊 All Locations Data"):
        st.dataframe(df, use_container_width=True)

def display_current_weather(df: pd.DataFrame, raw_data: dict):
    """Display current weather observations."""
    if df is None or df.empty:
        st.warning("No current weather data available")
        return
    
    st.subheader("🌡️ Current Weather Observations")
    
    # Summary statistics
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Weather Stations", len(df))
        
        with col2:
            if 'observation_time' in df.columns:
                latest_obs = df['observation_time'].max()
                st.metric("Latest Update", latest_obs[:16] if latest_obs else "N/A")
        
        with col3:
            temp_cols = [col for col in df.columns if 'TEMP' in col or 'temp' in col]
            if temp_cols:
                temps = pd.to_numeric(df[temp_cols[0]], errors='coerce').dropna()
                if not temps.empty:
                    st.metric("Avg Temperature", f"{temps.mean():.1f}°C")
        
        with col4:
            humid_cols = [col for col in df.columns if 'HUMD' in col or 'humid' in col]
            if humid_cols:
                humidity = pd.to_numeric(df[humid_cols[0]], errors='coerce').dropna()
                if not humidity.empty:
                    st.metric("Avg Humidity", f"{humidity.mean():.1f}%")
    
    # Interactive map (if coordinates available)
    if 'latitude' in df.columns and 'longitude' in df.columns:
        st.subheader("🗺️ Weather Station Locations")
        
        map_data = df[['latitude', 'longitude']].dropna()
        if not map_data.empty:
            st.map(map_data)
    
    # Data table
    st.subheader("📊 Weather Station Data")
    st.dataframe(df, use_container_width=True)

def display_earthquake_data(df: pd.DataFrame, raw_data: dict):
    """Display earthquake reports."""
    if df is None or df.empty:
        st.warning("No earthquake data available")
        return
    
    st.subheader("🌏 Recent Earthquake Reports")
    
    # Summary
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Reports", len(df))
        
        with col2:
            magnitudes = pd.to_numeric(df['magnitude_value'], errors='coerce').dropna()
            if not magnitudes.empty:
                st.metric("Max Magnitude", f"{magnitudes.max():.1f}")
        
        with col3:
            depths = pd.to_numeric(df['depth'], errors='coerce').dropna()
            if not depths.empty:
                st.metric("Avg Depth", f"{depths.mean():.1f} km")
        
        with col4:
            if 'origin_time' in df.columns:
                latest_eq = df['origin_time'].max()
                st.metric("Latest Event", latest_eq[:16] if latest_eq else "N/A")
    
    # Recent earthquakes
    st.subheader("📋 Recent Events")
    
    # Sort by time (newest first)
    if 'origin_time' in df.columns:
        df_sorted = df.sort_values('origin_time', ascending=False)
        
        for idx, eq in df_sorted.head(5).iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**📍 {eq.get('location', 'Unknown Location')}**")
                    st.write(f"Time: {eq.get('origin_time', 'N/A')}")
                
                with col2:
                    magnitude = eq.get('magnitude_value', 'N/A')
                    st.metric("Magnitude", magnitude)
                
                with col3:
                    depth = eq.get('depth', 'N/A')
                    st.metric("Depth", f"{depth} km" if depth != 'N/A' else 'N/A')
                
                if eq.get('web_url'):
                    st.markdown(f"[📄 Detailed Report]({eq.get('web_url')})")
                
                st.divider()
    
    # Full data table
    with st.expander("📊 All Earthquake Data"):
        st.dataframe(df, use_container_width=True)

def show_settings_page():
    """Display settings page."""
    st.title("⚙️ Settings")
    
    st.subheader("🔧 Crawler Configuration")
    
    # Rate limiting settings
    with st.expander("Rate Limiting"):
        request_delay = st.slider(
            "Request delay (seconds):", 
            min_value=0.1, 
            max_value=5.0, 
            value=1.0, 
            step=0.1
        )
        
        max_retries = st.slider(
            "Max retries:", 
            min_value=1, 
            max_value=10, 
            value=3
        )
    
    # Cache settings
    with st.expander("Cache Configuration"):
        cache_expiry = st.slider(
            "Cache expiry (hours):", 
            min_value=1, 
            max_value=168, 
            value=24
        )
        
        max_cache_size = st.slider(
            "Max cache size (MB):", 
            min_value=10, 
            max_value=1000, 
            value=100
        )
    
    # Taiwan CWA API Settings
    with st.expander("Taiwan CWA API"):
        st.write("**API Key Configuration**")
        current_key = GOV_DATA_SOURCES['taiwan_cwa'].get('api_key', '')
        st.code(f"Current API Key: {current_key[:10]}...{current_key[-5:]}")
        st.info("To update the API key, modify the config.py file")
    
    # Data source status
    st.subheader("📊 Data Source Status")
    
    crawlers = init_crawlers()
    
    for source_name, crawler in crawlers.items():
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**{source_name}**")
                if source_name == 'taiwan_cwa':
                    st.caption("Taiwan Central Weather Administration")
            
            with col2:
                if st.button(f"Test {source_name}", key=f"test_{source_name}"):
                    with st.spinner(f"Testing {source_name}..."):
                        is_healthy = crawler.health_check()
                        if is_healthy:
                            st.success("✅ Online")
                        else:
                            st.error("❌ Offline")
            
            with col3:
                st.write("🟢 Ready")
    
    # Clear cache
    st.subheader("🗑️ Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Cached Datasets", type="secondary"):
            st.session_state.datasets = []
            st.session_state.selected_dataset = None
            st.session_state.processed_data = None
            st.success("Cache cleared!")
    
    with col2:
        cache_info = f"Currently cached: {len(st.session_state.datasets)} datasets"
        st.info(cache_info)

if __name__ == "__main__":
    main()