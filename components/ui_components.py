"""Beautiful UI components for the Taiwan Weather Dashboard."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

def load_custom_css():
    """Load custom CSS styling."""
    with open('styles/custom_styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def create_hero_section():
    """Create a beautiful hero section."""
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🌤️ Taiwan Weather Center</h1>
        <p class="hero-subtitle">Real-time weather data from Central Weather Administration</p>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 2rem;">
            <div style="text-align: center; color: white;">
                <div style="font-size: 1.5rem; font-weight: bold;">400+</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Weather Stations</div>
            </div>
            <div style="text-align: center; color: white;">
                <div style="font-size: 1.5rem; font-weight: bold;">24/7</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Monitoring</div>
            </div>
            <div style="text-align: center; color: white;">
                <div style="font-size: 1.5rem; font-weight: bold;">Real-time</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">Updates</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_weather_status_card(title: str, value: str, status: str = "good", icon: str = "🌤️"):
    """Create a beautiful weather status card."""
    status_class = f"status-{status}"
    
    st.markdown(f"""
    <div class="weather-card">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <span style="font-size: 2rem; margin-right: 1rem;">{icon}</span>
            <h3 style="margin: 0; color: #333;">{title}</h3>
        </div>
        <div class="temperature-display">{value}</div>
        <div class="{status_class}" style="display: inline-block; margin-top: 1rem;">
            {status.upper()}
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(label: str, value: str, delta: str = None, icon: str = "📊"):
    """Create a metric card with beautiful styling."""
    delta_html = ""
    if delta:
        delta_color = "green" if "+" in delta else "red" if "-" in delta else "gray"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.9rem; margin-top: 0.5rem;">{delta}</div>'
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def create_alert_card(title: str, message: str, severity: str = "medium", location: str = ""):
    """Create an alert card."""
    icons = {
        "high": "🚨",
        "medium": "⚠️", 
        "low": "ℹ️"
    }
    
    st.markdown(f"""
    <div class="alert-card alert-{severity}">
        <div style="display: flex; align-items: center;">
            <span style="font-size: 1.5rem; margin-right: 1rem;">{icons.get(severity, "ℹ️")}</span>
            <div>
                <strong>{title}</strong>
                {f" - {location}" if location else ""}
                <br>
                <span style="color: #666;">{message}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_data_source_card(title: str, description: str, status: str = "online", count: int = 0):
    """Create a data source card."""
    status_icon = "🟢" if status == "online" else "🔴"
    
    st.markdown(f"""
    <div class="data-source-card">
        <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 1rem;">
            <h4 style="margin: 0; color: #1976D2;">{title}</h4>
            <span>{status_icon} {status.title()}</span>
        </div>
        <p style="color: #666; margin-bottom: 1rem;">{description}</p>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.9rem; color: #999;">Datasets: {count}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_weather_map(df: pd.DataFrame, lat_col: str = "latitude", lon_col: str = "longitude"):
    """Create an interactive weather map."""
    if df is None or df.empty or lat_col not in df.columns or lon_col not in df.columns:
        st.info("📍 Map data not available")
        return
    
    # Filter out invalid coordinates
    map_data = df.dropna(subset=[lat_col, lon_col])
    
    if map_data.empty:
        st.info("📍 No location data available for mapping")
        return
    
    # Create the map
    fig = go.Figure()
    
    fig.add_trace(go.Scattermapbox(
        lat=map_data[lat_col],
        lon=map_data[lon_col],
        mode='markers',
        marker=dict(
            size=10,
            color='blue',
            opacity=0.7
        ),
        text=map_data.get('station', map_data.index),
        hovertemplate="<b>%{text}</b><br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>"
    ))
    
    # Calculate map center
    center_lat = map_data[lat_col].mean()
    center_lon = map_data[lon_col].mean()
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=7
        ),
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_temperature_gauge(temperature: float, min_temp: float = -10, max_temp: float = 40):
    """Create a beautiful temperature gauge."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=temperature,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Temperature (°C)", 'font': {'size': 20}},
        delta={'reference': 25},
        gauge={
            'axis': {'range': [min_temp, max_temp], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#1976D2"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [min_temp, 0], 'color': '#E3F2FD'},
                {'range': [0, 25], 'color': '#BBDEFB'},
                {'range': [25, max_temp], 'color': '#90CAF9'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 35
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#1976D2", 'family': "Inter"}
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_weather_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str):
    """Create a beautiful weather chart."""
    if df is None or df.empty or x_col not in df.columns or y_col not in df.columns:
        st.info(f"📊 {title} data not available")
        return
    
    fig = px.line(
        df, 
        x=x_col, 
        y=y_col,
        title=title,
        template="plotly_white"
    )
    
    fig.update_traces(
        line=dict(color='#1976D2', width=3),
        mode='lines+markers',
        marker=dict(size=6, color='#1976D2')
    )
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        title_font_size=16,
        title_font_color='#1976D2',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='white',
        font_family="Inter"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_location_selector(locations: list, default_location: str = None):
    """Create a beautiful location selector."""
    st.markdown("""
    <div class="location-selector">
        <h4 style="margin-bottom: 1rem; color: #1976D2;">📍 Select Location</h4>
    </div>
    """, unsafe_allow_html=True)
    
    default_index = 0
    if default_location and default_location in locations:
        default_index = locations.index(default_location)
    
    return st.selectbox(
        "",
        locations,
        index=default_index,
        key="location_selector"
    )

def create_weather_summary_grid(weather_data: dict):
    """Create a grid of weather summary cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        temp = weather_data.get('temperature', 'N/A')
        create_metric_card("Temperature", temp, icon="🌡️")
    
    with col2:
        humidity = weather_data.get('humidity', 'N/A')
        create_metric_card("Humidity", humidity, icon="💧")
    
    with col3:
        wind = weather_data.get('wind_speed', 'N/A')
        create_metric_card("Wind Speed", wind, icon="💨")
    
    with col4:
        pressure = weather_data.get('pressure', 'N/A')
        create_metric_card("Pressure", pressure, icon="📊")

def create_page_header(title: str, subtitle: str = "", icon: str = "🌤️"):
    """Create a beautiful page header."""
    st.markdown(f"""
    <div class="weather-header">
        <div style="text-align: center; padding: 1rem;">
            <h1 style="color: white; margin-bottom: 0.5rem; font-size: 2.5rem;">
                {icon} {title}
            </h1>
            {f'<p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0;">{subtitle}</p>' if subtitle else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)