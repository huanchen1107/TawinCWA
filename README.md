# 🌤️ Taiwan Weather Dashboard

A beautiful Streamlit web application that provides real-time Taiwan weather data, earthquake monitoring, and government open data exploration with a professional CWA-inspired design.

## 🌐 **Live Demo**
### **[https://taiwancwa.streamlit.app/](https://taiwancwa.streamlit.app/)**

Experience the beautiful Taiwan Weather Dashboard live! Features real-time weather data from Taiwan Central Weather Administration.

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

## 🚀 Quick Start

### **Option 1: Try the Live Demo**
Visit **[https://taiwancwa.streamlit.app/](https://taiwancwa.streamlit.app/)** to experience the full Taiwan Weather Dashboard immediately!

### **Option 2: Run Locally**
1. Clone this repository
   ```bash
   git clone https://github.com/huanchen1107/TawinCWA.git
   cd TawinCWA
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app
   ```bash
   streamlit run streamlit_app.py
   ```
4. Visit `http://localhost:8501` to access the dashboard

### 🔑 Taiwan Weather API Setup
The app includes Taiwan CWA API integration already configured in `config.py`. For your own deployment, you can update it with your Taiwan CWA API key.

## 🌐 Live Deployment

### **🎉 Currently Deployed!**
The Taiwan Weather Dashboard is live at: **[https://taiwancwa.streamlit.app/](https://taiwancwa.streamlit.app/)**

### **📱 Mobile Ready**
The app is fully responsive and works beautifully on:
- 🖥️ Desktop computers
- 📱 Mobile phones  
- 📟 Tablets
- 💻 Laptops

### **🚀 Deploy Your Own**
This app is designed to be easily deployed to Streamlit Cloud:
1. Fork this repository
2. Connect to [share.streamlit.io](https://share.streamlit.io)
3. Deploy with `streamlit_app.py` as the main file

## 🎨 **Features Showcase**

### **🌤️ Beautiful Weather Dashboard**
- Real-time Taiwan weather forecasts from CWA API
- Interactive weather maps with Taiwan cities
- Professional CWA-inspired design with gradients
- Temperature, humidity, wind speed metrics
- Weather alerts and notifications

### **🌏 Earthquake Monitoring**
- Live earthquake data from Taiwan CWA
- Magnitude and depth visualization
- Recent seismic activity timeline
- Interactive earthquake maps

### **📊 Government Data Explorer**
- Integration with data.gov (250,000+ datasets)
- US Census Bureau demographic data
- Search and filter capabilities
- Data export in multiple formats

### **🎯 Technical Highlights**
- Beautiful responsive UI with CSS animations
- Real-time API data integration
- Professional error handling and caching
- Mobile-optimized design
- Production-ready code architecture

---
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