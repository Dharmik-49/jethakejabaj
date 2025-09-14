# pages/1_Home.py

import streamlit as st
import requests
from language_config import LANGUAGES
import json

# --- 1. Login Check ---
# This must be the first Streamlit command on the page
if not st.session_state.get('logged_in'):
    st.error("Please log in to access this page.")
    st.stop()

# --- 2. Language and API Configuration ---
lang = LANGUAGES[st.session_state.get('language', 'English')]
API_URL = "http://127.0.0.1:5000"

# --- 3. Page Title ---
st.title(lang["home_title"])

# --- 4. Initialize Session State ---
if 'weather_data' not in st.session_state: st.session_state.weather_data = None
if 'crop_recommendation' not in st.session_state: st.session_state.crop_recommendation = None
if 'prediction_history' not in st.session_state: st.session_state.prediction_history = None

# --- 5. Helper Function to Fetch Prediction History ---
def fetch_history():
    try:
        email = st.session_state.get('user_email')
        if email:
            response = requests.get(f"{API_URL}/prediction-history/{email}")
            if response.status_code == 200:
                st.session_state.prediction_history = response.json()
            else:
                # Clear history on error to prevent showing stale data
                st.session_state.prediction_history = []
    except requests.exceptions.ConnectionError:
        st.session_state.prediction_history = []

# Fetch history only once when the page loads
if st.session_state.prediction_history is None:
    fetch_history()

# --- 6. UI Part 1: Live Weather Fetcher ---
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

if st.session_state.weather_data:
    st.success(f"✅ Live weather for {st.session_state.weather_data['city']} fetched!")
    data = st.session_state.weather_data
    icon_url = f"http://openweathermap.org/img/wn/{data['icon']}@2x.png"
    col1, col2 = st.columns([1, 2])
    with col1: st.image(icon_url, width=100)
    with col2:
        st.metric("Temperature", f"{data['temperature_celsius']} °C", f"Feels like {data['feels_like_celsius']} °C")
        st.write(f"**{data['description']}**")
    col3, col4, col5 = st.columns(3)
    col3.metric("High / Low", f"{data['temp_max_celsius']}° / {data['temp_min_celsius']}°")
    col4.metric("Humidity", f"{data['humidity_percent']}%")
    col5.metric("Wind Speed", f"{data['wind_speed_mps']} m/s")

# --- 7. UI Part 2: Get Crop Recommendation ---
with st.container(border=True):
    st.header(lang["crop_header"])
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
        if not data: st.error("Please get live weather data first.")
        else:
            with st.spinner("Analyzing..."):
                payload = {"user_email": st.session_state['user_email'], "temp_high": data.get('temp_max_celsius', 0), "temp_low": data.get('temp_min_celsius', 0), "temp_avg": data.get('temperature_celsius', 0), "rainfall": rainfall, "humidity": data.get('humidity_percent', 0), "ph": ph_value, "soil_type": soil_type}
                response = requests.post(f"{API_URL}/recommend-crop", json=payload)
                if response.status_code == 200:
                    st.session_state.crop_recommendation = response.json()['recommended_crop']
                    fetch_history() # Refresh history after a new prediction is made
                else:
                    st.error(f"❌ Error: {response.json()['detail']}")
                    st.session_state.crop_recommendation = None

# --- 8. UI Part 3: Display Recommendation and Get Advice ---
if st.session_state.crop_recommendation:
    crop = st.session_state.crop_recommendation
    st.success(f"**Recommended Crop: {crop}** 🌱")
    with st.expander(lang["get_advice_button"].format(crop=crop)):
        with st.spinner("Generating advice..."):
            data = st.session_state.weather_data or {}
            payload = {"crop": crop, "soil_type": soil_type, "ph": ph_value, "temp_avg": data.get('temperature_celsius', 0), "humidity": data.get('humidity_percent', 0), "description": data.get('description', 'clear sky')}
            response = requests.post(f"{API_URL}/get-suggestions", json=payload)
            if response.status_code == 200:
                suggestions = response.json()
                st.subheader("🔬 Soil pH Management"); st.info(suggestions['ph_suggestion'])
                st.subheader("🌿 Fertilizer Suggestion"); st.info(suggestions['fertilizer_suggestion'])
                st.subheader("🐛 Pesticide Suggestion"); st.warning(suggestions['pesticide_suggestion'])
            else:
                st.error(f"❌ Error: {response.json()['detail']}")

# --- 9. UI Part 4: Display Prediction History with Professional UI ---
st.markdown("---")
st.header(lang["history_header"])

if st.session_state.prediction_history:
    for prediction in st.session_state.prediction_history:
        # Format the timestamp for a cleaner display (YYYY-MM-DD HH:MM:SS)
        ts = prediction['timestamp'].split('.')[0].replace("T", " ")
        expander_title = f"**{prediction['recommended_crop']}** (Predicted on: {ts})"
        
        with st.expander(expander_title):
            inputs = prediction['inputs']
            
            st.markdown(f"**{lang['history_inputs_label']}**")
            
            # Use columns and metrics for a clean, professional layout
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Avg Temp", value=f"{inputs.get('temp_avg', 'N/A')} °C")
                st.metric(label="Rainfall", value=f"{inputs.get('rainfall', 'N/A')} mm")
            with col2:
                st.metric(label="High Temp", value=f"{inputs.get('temp_high', 'N/A')} °C")
                st.metric(label="Humidity", value=f"{inputs.get('humidity', 'N/A')} %")
            with col3:
                st.metric(label="Low Temp", value=f"{inputs.get('temp_low', 'N/A')} °C")
                st.metric(label="Soil pH", value=f"{inputs.get('ph', 'N/A')}")

            st.markdown(f"**Soil Type:** `{inputs.get('soil_type', 'N/A')}`")

else:
    st.info(lang["history_no_predictions"])

