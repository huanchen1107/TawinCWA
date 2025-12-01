import streamlit as st
import pandas as pd

st.title("🌤️ Streamlit Test - Taiwan Weather Ready!")

st.write("✅ Streamlit is working!")

# Test basic components
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Temperature", "25°C", "2°C")

with col2:
    st.metric("Humidity", "70%", "-5%")

with col3:
    st.metric("Status", "✅ Ready")

# Test data display
df = pd.DataFrame({
    'City': ['Taipei', 'Taichung', 'Kaohsiung'],
    'Temperature': [25, 28, 30],
    'Weather': ['Sunny', 'Cloudy', 'Partly Cloudy']
})

st.dataframe(df)

st.success("🎉 Streamlit is working perfectly! Ready for your Taiwan Weather App!")
