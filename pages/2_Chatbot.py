# pages/2_Chatbot.py

import streamlit as st
import requests
from language_config import LANGUAGES # Import the dictionary
import db_utils

# 1. Login check at the very top of the page
if not st.session_state.get('logged_in'):
    st.error("Please log in to access this page.")
    st.stop()

# 2. Get the selected language from session state
lang = LANGUAGES[st.session_state.get('language', 'English')]

# 3. Define constants and set the page title using the language dictionary
API_URL = "http://127.0.0.1:5000"
st.title(lang["chatbot_title"])
st.write(lang["chatbot_intro"])

# 4. The rest of the chatbot logic
# Load chat history from DB when the page loads for a logged-in user
if "messages" not in st.session_state:
    user_id = db_utils.get_user_id(st.session_state['user_email'])
    st.session_state.messages = db_utils.load_chat_history(user_id) if user_id else []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])

# Accept user input, using the placeholder from the language dictionary
if prompt := st.chat_input(lang["chat_input_placeholder"]):
    user_id = db_utils.get_user_id(st.session_state['user_email'])
    if not user_id:
        st.error("Could not find user. Please log in again.")
        st.stop()
        
    # Add user message to session state and DB
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    db_utils.save_chat_message(user_id, "user", prompt)
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                chat_payload = {"history": st.session_state.messages[:-1], "message": prompt}
                response = requests.post(f"{API_URL}/chat", json=chat_payload)
                if response.status_code == 200:
                    assistant_response = response.json()
                    response_text = assistant_response["parts"][0]
                    st.markdown(response_text)
                    # Add model response to session state and DB
                    st.session_state.messages.append(assistant_response)
                    db_utils.save_chat_message(user_id, "model", response_text)
                else:
                    st.error(f"❌ Error: {response.json()['detail']}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Connection Error: Is the backend running?")