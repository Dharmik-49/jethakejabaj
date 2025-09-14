🧑‍🌾 Smart AI Farming Assistant (Krishi Mitra)
A comprehensive, multilingual web application designed to empower Indian farmers with data-driven insights and AI-powered assistance. This platform helps farmers make informed decisions about crop selection, resource management, and pest control by leveraging live weather data, machine learning, and a conversational AI.

This project was developed to address the challenges outlined in the "Smart AI Farming Assistant" problem statement, focusing on creating a user-friendly, accessible, and intelligent tool for the modern agricultural sector.

✨ Key Features
🌦️ Live Weather Reports: Fetches real-time, location-based weather data using the OpenWeatherMap API, including temperature, humidity, and weather conditions.

🤖 AI-Powered Crop Recommendation: Utilizes a custom-trained Machine Learning model (Random Forest) to recommend the most suitable crops based on soil type, pH, rainfall, temperature, and humidity. The model is trained on a diverse dataset of over 25,000 samples covering 10 different crops.

💡 Personalized Farming Advice: Provides actionable advice on:

Fertilizer Usage: Recommends appropriate fertilizers for the selected crop.

Pesticide Control: Suggests common pests to watch for and control methods.

Soil pH Management: Gives specific instructions on how to raise or lower soil pH.

🗣️ Multilingual AI Chatbot ("Krishi Mitra"): A conversational assistant powered by Google's Gemini API that can answer farming-related questions in English, Hindi, and Gujarati. The chatbot is instructed to stay on the topic of agriculture.

🔒 Secure User Accounts: Features a full login and sign-up system. User data (name, email) and passwords (securely hashed) are stored in a local SQLite database.

📝 Personalized Chat History: The chatbot automatically saves and loads conversation history for each logged-in user, providing a continuous experience.

🌐 Multi-Language UI: The entire user interface can be dynamically switched between English, Hindi, and Gujarati.

📱 Mobile-Responsive Design: The UI is built with Streamlit and enhanced with custom CSS to be fully functional and user-friendly on both desktop and mobile devices.

🛠️ Technology Stack
Frontend: Streamlit

Backend & API: FastAPI, Python

Machine Learning: Scikit-learn, Pandas, NumPy

AI / LLM: Google Gemini API

Database: SQLite

External APIs: OpenWeatherMap API

Password Security: Passlib, Bcrypt

🚀 Setup and Installation Guide
Follow these steps to set up and run the project on your local machine.

1. Prerequisites
Python 3.8 or higher installed on your system.

A code editor like Visual Studio Code.

Access to a terminal or PowerShell.

2. Clone the Repository
Clone this project to your local machine.

git clone <your-repository-url>
cd <project-folder-name>

3. Create and Activate a Virtual Environment
It is highly recommended to use a virtual environment to keep project dependencies isolated.

On Windows (PowerShell):

python -m venv venv
.\venv\Scripts\activate

4. Install Dependencies
Install all the required Python libraries using the provided requirements.txt file.

pip install streamlit fastapi uvicorn scikit-learn pandas requests google-generativeai passlib[bcrypt]

5. API Key Configuration (Crucial Step)
You need to get two free API keys for the weather and chatbot features.

OpenWeatherMap Key:

Sign up at https://openweathermap.org/.

Go to your account's "API keys" tab and copy your key.

Google Gemini Key:

Go to https://ai.google.dev/.

Click "Get API key in Google AI Studio" and create your key.

Now, open the 2_main_api.py file and paste your keys into the designated variables:

# In 2_main_api.py
OPENWEATHER_API_KEY = "PASTE_YOUR_OPENWEATHER_KEY_HERE"
GEMINI_API_KEY = "PASTE_YOUR_GEMINI_KEY_HERE"

6. Set Up the Database
Run the database setup script once to create the user_data.db file and the necessary tables.

python db_setup.py

7. Train the Machine Learning Model
Run the model creation script once to generate the training dataset and save the trained model as .pkl files.

python 1_create_models.py

▶️ How to Run the Application
The application consists of two parts: the backend API and the frontend UI. You need to run them in two separate terminals.

Terminal 1: Start the Backend API
In your first terminal (with the virtual environment activated), run the Uvicorn server:

uvicorn 2_main_api:app --reload --port 5000

The API will be running at http://127.0.0.1:5000.

Terminal 2: Start the Frontend UI
Open a new terminal, activate the virtual environment again, and run the Streamlit app:

streamlit run Login.py

Your web browser will automatically open a new tab with the application's login page.

📖 User Guide
1. Account Creation and Login
Use the sidebar to switch between the Login and Sign Up pages.

New users can create an account by providing a name, email, and password.

Existing users can log in with their credentials.

2. Language Selection
The sidebar contains a dropdown menu to switch the display language between English, हिंदी (Hindi), and ગુજરાતી (Gujarati) at any time.

3. Home Page: Weather and Crop Advice
This page is a three-step dashboard:

Get Live Weather: Enter a city name and click "Get Weather" to fetch real-time data.

Get Crop Recommendation: Input your soil type, expected rainfall, and soil pH. Click "Recommend Crop" to get an AI-powered suggestion.

Get Farming Advice: After a crop is recommended, an expandable section will appear. Click on it to view detailed advice on fertilizers, pesticides, and soil pH management for that specific crop.

4. Chatbot Page: Krishi Mitra
Navigate to the "Chatbot" page using the sidebar.

Ask any farming-related question in English, Hindi, or Gujarati.

The chatbot will respond in the same language and remember your conversation history, which is saved to your account.