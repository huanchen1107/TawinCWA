# Beautiful Taiwan Weather Dashboard - Streamlit Cloud Entry Point
# This file is required for Streamlit Cloud deployment

import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point with error handling for Streamlit Cloud."""
    
    # Try loading the beautiful app first
    try:
        from beautiful_app import main as beautiful_main
        st.success("🌤️ Loading Beautiful Taiwan Weather Dashboard...")
        beautiful_main()
        
    except Exception as e:
        st.error(f"❌ Beautiful app failed to load: {e}")
        st.info("🔄 Loading debug version...")
        
        # Fallback to debug version
        try:
            from streamlit_debug import main as debug_main
            debug_main()
        except Exception as debug_error:
            st.error(f"❌ Debug version also failed: {debug_error}")
            
            # Last resort - basic app
            st.title("🌤️ Taiwan Weather Dashboard")
            st.error("App failed to load properly. Please check the logs.")
            st.info("This might be a temporary issue. Please refresh the page.")

if __name__ == "__main__":
    main()