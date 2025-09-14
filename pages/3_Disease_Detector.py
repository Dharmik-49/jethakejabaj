# pages/3_Disease_Detector.py

import streamlit as st
import requests
from language_config import LANGUAGES
from PIL import Image

# --- 1. Login Check ---
if not st.session_state.get('logged_in'):
    st.error("Please log in to access this page.")
    st.stop()

# --- 2. Language and API Configuration ---
lang = LANGUAGES[st.session_state.get('language', 'English')]
API_URL = "http://127.0.0.1:5000"

# --- 3. Page UI ---
st.title(lang["detector_title"])
st.info(lang["detector_intro"])

uploaded_file = st.file_uploader(
    lang["detector_uploader_label"],
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Leaf", use_container_width=True)
    
    if st.button(lang["detector_button"], type="primary"):
        with st.spinner("AI is analyzing the image..."):
            try:
                # Prepare the file for the API request
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                response = requests.post(f"{API_URL}/detect-disease", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    st.markdown("---")
                    st.header(lang["detector_result_header"])
                    st.markdown(result['diagnosis'])
                else:
                    st.error(f"❌ Error: {response.json()['detail']}")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Connection Error: Is the backend running?")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
