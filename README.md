# Government Open Data Crawler

A Streamlit web application that crawls government open data sources and provides an interactive interface for browsing, filtering, and downloading datasets.

## Features

- 🕷️ Web crawler for multiple government data sources
- 🔍 Search and filter datasets by keywords and categories
- 📊 Data preview and basic visualization
- 💾 Export data in multiple formats (CSV, JSON, Excel)
- 🌤️ **Real-time Taiwan weather dashboard**
- ⚠️ **Weather alerts and monitoring**
- 🌏 **Earthquake tracking**
- ☁️ Easy deployment to Streamlit Cloud

## Government Data Sources

- **data.gov** - 250,000+ Federal datasets
- **Census.gov** - US Census and demographic data
- **Taiwan CWA** - Real-time weather, forecasts, and earthquake data

## Quick Start

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`
4. Visit `http://localhost:8501` to access the dashboard

### Taiwan Weather API Setup
To use Taiwan weather features, the app uses the Taiwan CWA API key already configured in `config.py`. You can update it with your own key if needed.

## Deployment

This app is designed to be easily deployed to Streamlit Cloud by connecting your GitHub repository.

## Project Structure

```
gov-data-crawler/
├── app.py                 # Main Streamlit app
├── crawler/              # Web crawling modules
├── data/                 # Cached data storage
├── utils/                # Utility functions
├── requirements.txt      # Dependencies
└── README.md            # This file
```