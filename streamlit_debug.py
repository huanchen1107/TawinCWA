"""
Streamlit Cloud Debug Version - Simplified for testing
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page config
st.set_page_config(
    page_title="Taiwan Weather Debug",
    page_icon="🌤️",
    layout="wide"
)

def main():
    """Debug version with minimal dependencies."""
    
    st.title("🌤️ Taiwan Weather Dashboard")
    st.write("Debug version for Streamlit Cloud")
    
    # Test basic functionality
    st.success("✅ Streamlit is working!")
    
    # Test imports
    try:
        from config import GOV_DATA_SOURCES
        st.success("✅ Config imported successfully")
        
        # Show Taiwan API key (first 10 chars only)
        api_key = GOV_DATA_SOURCES.get('taiwan_cwa', {}).get('api_key', 'Not found')
        st.info(f"🔑 API Key: {api_key[:10]}...")
        
    except Exception as e:
        st.error(f"❌ Config import error: {e}")
    
    # Test Taiwan crawler
    try:
        from crawler.taiwan_crawler import TWCrawler
        st.success("✅ Taiwan crawler imported successfully")
        
        # Test API connection
        if st.button("🧪 Test Taiwan CWA API"):
            with st.spinner("Testing API connection..."):
                try:
                    crawler = TWCrawler(GOV_DATA_SOURCES['taiwan_cwa'])
                    
                    # Simple health check
                    if crawler.health_check():
                        st.success("✅ Taiwan CWA API is accessible!")
                    else:
                        st.warning("⚠️ API health check failed")
                        
                except Exception as api_error:
                    st.error(f"❌ API test error: {api_error}")
                    
    except Exception as e:
        st.error(f"❌ Crawler import error: {e}")
        st.write("Full error:", str(e))
    
    # Test basic UI components
    st.markdown("### 📊 Basic UI Test")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Temperature", "25°C", "2°C")
    
    with col2:
        st.metric("Humidity", "70%", "-5%")
    
    with col3:
        st.metric("Status", "✅ Working")
    
    # Test map functionality
    st.markdown("### 🗺️ Map Test")
    
    # Sample Taiwan data
    taiwan_data = pd.DataFrame({
        'City': ['Taipei', 'Taichung', 'Kaohsiung'],
        'lat': [25.0330, 24.1477, 22.6273],
        'lon': [121.5654, 120.6736, 120.3014],
        'temp': [25, 28, 30]
    })
    
    st.map(taiwan_data)
    
    # Debug info
    st.markdown("### 🔍 Debug Information")
    st.write("Python version:", sys.version)
    st.write("Current working directory:", os.getcwd())
    st.write("Available files:", os.listdir('.'))
    
    # Show requirements
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        st.text("Requirements.txt content:")
        st.code(requirements)
    
    st.markdown("---")
    st.markdown("**🎯 If you see this page, Streamlit Cloud is working!**")
    st.markdown("**Issue might be in specific components or CSS loading.**")

if __name__ == "__main__":
    main()