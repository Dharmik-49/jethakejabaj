# Login.py

import streamlit as st
import db_utils
from language_config import LANGUAGES

# --- Page Configuration ---
st.set_page_config(
    page_title="Login - Farming Assistant",
    page_icon="🧑‍🌾",
    layout="centered"
)


# --- Custom CSS for a more user-friendly, mobile-first look ---
def load_css():
    st.markdown("""
        <style>
            .stButton > button {
                font-size: 18px;
                padding: 10px 24px;
                border-radius: 8px;
                width: 100%;
            }
            .main .block-container {
                font-size: 1.1rem;
            }
            div[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > div[data-testid="stExpander"] {
                 border-radius: 0.5rem;
            }
        </style>
    """, unsafe_allow_html=True)

load_css()


# --- Language Selection in Sidebar ---
if 'language' not in st.session_state:
    st.session_state['language'] = "English"

st.session_state['language'] = st.sidebar.selectbox(
    "Language / ભાષા",
    options=list(LANGUAGES.keys())
)
lang = LANGUAGES[st.session_state['language']]


# --- Page Functions ---

def login_page():
    st.title(lang["login_title"])
    with st.form("login_form"):
        email = st.text_input(lang["login_email"])
        password = st.text_input(lang["login_password"], type="password")
        submitted = st.form_submit_button(lang["login_button"])

        if submitted:
            if db_utils.check_user(email, password):
                st.session_state['logged_in'] = True
                st.session_state['user_email'] = email
                # Redirect to the home page upon successful login
                st.switch_page("pages/1_Home.py")
            else:
                st.error(lang["login_error"])

def signup_page():
    st.title(lang["signup_title"])
    with st.form("signup_form"):
        name = st.text_input(lang["signup_name"])
        email = st.text_input(lang["login_email"])
        password = st.text_input(lang["login_password"], type="password")
        submitted = st.form_submit_button(lang["signup_button"])

        if submitted:
            if db_utils.add_user(name, email, password):
                st.success(lang["signup_success"])
            else:
                st.error(lang["signup_error"])

def main_app_view():
    """ This is the view shown after a user logs in (on the Login.py page). """
    st.sidebar.success(f"Logged in as {st.session_state['user_email']}")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            if key not in ['language']:
                del st.session_state[key]
        st.session_state['logged_in'] = False
        st.rerun()
    
    st.title(lang["main_welcome"])
    st.write(lang["main_navigate"])
    st.info("Your chat history will now be saved automatically to your account.")


# --- Main App Logic ---

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_app_view()
else:
    page = st.sidebar.radio(lang["choose_action"], ["Login", "Sign Up"])
    if page == "Login":
        login_page()
    elif page == "Sign Up":
        signup_page()