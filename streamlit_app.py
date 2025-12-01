# Beautiful Taiwan Weather Dashboard - Streamlit Cloud Entry Point
# This file is required for Streamlit Cloud deployment

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the beautiful app
try:
    from beautiful_app import main
    print("🌤️ Loading Beautiful Taiwan Weather Dashboard...")
    main()
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback to original app
    from app import main
    main()