# pages/1_Home.py

import streamlit as st
import requests
from language_config import LANGUAGES # Import the dictionary we created

# Login check at the very top of the page
if not st.session_state.get('logged_in'):
    st.error("Please log in to access this page.")
    st.stop()

# Get the selected language from session state, defaulting to English
lang = LANGUAGES[st.session_state.get('language', 'English')]

# --- Page Content Starts Here ---

API_URL = "http://127.0.0.1:5000"
st.title(lang["home_title"])

# Initialize session state for this page's data
if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None
if 'crop_recommendation' not in st.session_state:
    st.session_state.crop_recommendation = None

# --- Part 1: Live Weather Fetcher ---
with st.container(border=True):
    st.header(lang["weather_header"])
    city = st.text_input(lang["city_input"], "Ahmedabad")
    if st.button(lang["get_weather_button"], type="primary"):
        with st.spinner(f"Fetching weather for {city}..."):
            try:
                response = requests.get(f"{API_URL}/live-weather", params={"city": city})
                if response.status_code == 200:
                    st.session_state.weather_data = response.json()
                    st.session_state.crop_recommendation = None
                else:
                    st.error(f"❌ Error: {response.json()['detail']}")
                    st.session_state.weather_data = None
            except requests.exceptions.ConnectionError:
                st.error("❌ Connection Error: Is the backend running?")

# Display weather widget
if st.session_state.weather_data:
    st.success(f"✅ Live weather for {st.session_state.weather_data['city']} fetched!")
    data = st.session_state.weather_data
    icon_url = f"http://openweathermap.org/img/wn/{data['icon']}@2x.png"
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(icon_url, width=100)
    with col2:
        st.metric("Temperature", f"{data['temperature_celsius']} °C", f"Feels like {data['feels_like_celsius']} °C")
        st.write(f"**{data['description']}**")
    col3, col4, col5 = st.columns(3)
    col3.metric("High / Low", f"{data['temp_max_celsius']}° / {data['temp_min_celsius']}°")
    col4.metric("Humidity", f"{data['humidity_percent']}%")
    col5.metric("Wind Speed", f"{data['wind_speed_mps']} m/s")

# --- Part 2: Get Crop Recommendation ---
with st.container(border=True):
    st.header(lang["crop_header"])
    if not st.session_state.weather_data:
        st.info("Please get live weather data first.") # This can be translated too if added to the dictionary
    data = st.session_state.weather_data or {}
    st.subheader(lang["soil_water_header"])
    col1, col2 = st.columns(2)
    with col1:
        soil_types = ['Loamy', 'Sandy', 'Clay', 'Black', 'Red']
        soil_type = st.selectbox(lang["soil_type_label"], soil_types)
        rainfall = st.number_input(lang["rainfall_label"], value=0.0)
    with col2:
        ph_value = st.slider(lang["ph_label"], 4.0, 9.0, 6.5, 0.1)
    if st.button(lang["recommend_crop_button"], type="primary"):
        if not data:
            st.error("Cannot recommend crop without weather data.")
        else:
            with st.spinner("Analyzing..."):
                payload = {"temp_high": data.get('temp_max_celsius', 0), "temp_low": data.get('temp_min_celsius', 0), "temp_avg": data.get('temperature_celsius', 0), "rainfall": rainfall, "humidity": data.get('humidity_percent', 0), "ph": ph_value, "soil_type": soil_type}
                response = requests.post(f"{API_URL}/recommend-crop", json=payload)
                if response.status_code == 200:
                    st.session_state.crop_recommendation = response.json()['recommended_crop']
                else:
                    st.error(f"❌ Error: {response.json()['detail']}")
                    st.session_state.crop_recommendation = None

# --- Part 3: Display Recommendation and Get Advice ---
if st.session_state.crop_recommendation:
    crop = st.session_state.crop_recommendation
    st.success(f"**Recommended Crop: {crop}** 🌱")
    with st.container(border=True):
        st.header(lang["advice_header"])
        # Notice the .format(crop=crop) to insert the variable into our translated string
        if st.button(lang["get_advice_button"].format(crop=crop)):
            with st.spinner("Generating advice..."):
                payload = {"crop": crop, "soil_type": soil_type, "ph": ph_value, "temp_avg": data.get('temperature_celsius', 0), "humidity": data.get('humidity_percent', 0), "description": data.get('description', 'clear sky')}
                response = requests.post(f"{API_URL}/get-suggestions", json=payload)
                if response.status_code == 200:
                    suggestions = response.json()
                    st.subheader("🔬 Soil pH Management")
                    st.info(suggestions['ph_suggestion'])
                    st.subheader("🌿 Fertilizer Suggestion")
                    st.info(suggestions['fertilizer_suggestion'])
                    st.subheader("🐛 Pesticide Suggestion")
                    st.warning(suggestions['pesticide_suggestion'])
                else:
                    st.error(f"❌ Error: {response.json()['detail']}")