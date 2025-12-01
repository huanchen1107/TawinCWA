# Beautiful Taiwan Weather Dashboard - Streamlit Cloud Entry Point
# This file is required for Streamlit Cloud deployment

import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point with error handling for Streamlit Cloud."""
    
    # Try loading the cloud-compatible app first
    try:
        from streamlit_cloud_app import main as cloud_main
        st.info("🌤️ Loading Taiwan Weather Dashboard (Cloud Version)...")
        cloud_main()
        
    except Exception as e:
        st.error(f"❌ Database app failed to load: {e}")
        st.info("🔄 Loading fallback version...")
        
        # Try the fixed beautiful app
        try:
            from beautiful_app_fixed import main as fixed_main
            st.info("🎨 Loading simplified beautiful app...")
            fixed_main()
            
        except Exception as fixed_error:
            st.error(f"❌ Fixed app also failed: {fixed_error}")
            
            # Fallback to debug version
            try:
                from streamlit_debug import main as debug_main
                st.info("🧪 Loading debug version...")
                debug_main()
            except Exception as debug_error:
                st.error(f"❌ Debug version also failed: {debug_error}")
                
                # Last resort - basic app
                st.title("🌤️ Taiwan Weather Dashboard")
                st.error("App failed to load properly. Please check the logs.")
                st.info("This might be a temporary issue. Please refresh the page.")

if __name__ == "__main__":
    main()