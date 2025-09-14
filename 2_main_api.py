# 2_main_api.py

import pickle
import uvicorn
import pandas as pd
import requests
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
import db_utils

# For Chatbot and Image Analysis
import google.generativeai as genai

# --- Main App Initialization ---
app = FastAPI(
    title="Farming Assistant API",
    description="API for Live Weather, Crop Recommendations, Farming Advice, and AI-powered Analysis."
)

# --- API Key Configuration ---
# IMPORTANT: Paste your secret keys here before running the server.
OPENWEATHER_API_KEY = "4a26316df0392e19d8cf8b49fba8ed8b"
GEMINI_API_KEY = "AIzaSyAheQfS5BucQ-Nr2I45LnckaMhkwT8QoGw"


# --- Pydantic Models for Data Validation ---
class CropInput(BaseModel):
    user_email: str
    temp_high: float
    temp_low: float
    temp_avg: float
    rainfall: float
    humidity: float
    ph: float
    soil_type: str

class SuggestionInput(BaseModel):
    crop: str
    soil_type: str
    ph: float
    temp_avg: float
    humidity: float
    description: str

class ChatMessage(BaseModel):
    role: str
    parts: List[str]

class ChatInput(BaseModel):
    history: List[ChatMessage]
    message: str


# --- Load Machine Learning Models on Startup ---
try:
    with open('crop_model.pkl', 'rb') as f:
        crop_model = pickle.load(f)
    with open('crop_model_columns.pkl', 'rb') as f:
        crop_model_columns = pickle.load(f)
    print("Crop model loaded successfully.")
except FileNotFoundError:
    crop_model = None
    print("Warning: Crop model files not found. The crop recommender will not work.")


# --- Configure Gemini Model on Startup ---
try:
    if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        genai.configure(api_key=GEMINI_API_KEY)
        system_instruction = (
            "You are 'Krishi Mitra', a friendly and expert AI assistant for Indian farmers. "
            "Your knowledge is strictly limited to agriculture, including crops, soil science, fertilizers, "
            "pesticides, weather patterns for farming, plant diseases, and Indian government agricultural schemes. "
            "You must communicate in the same language as the user's query (English, Hindi, or Gujarati). "
            "If a user asks a question outside of the agriculture domain, "
            "politely decline to answer and guide the conversation back to farming topics."
        )
        gemini_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        print("Gemini model configured successfully.")
    else:
        gemini_model = None
        print("Warning: Gemini API key not set. Chatbot and Disease Detector will be disabled.")
except Exception as e:
    gemini_model = None
    print(f"Error configuring Gemini model: {e}")


# --- Helper Function for Simulated Expert Advice ---
def get_llm_suggestions_mock(data: SuggestionInput):
    crop = data.crop.lower()
    ph_level = data.ph

    if ph_level < 6.0: ph_suggestion = f"Your soil pH of {ph_level} is acidic. To raise it, apply agricultural lime or wood ash."
    elif ph_level > 7.5: ph_suggestion = f"Your soil pH of {ph_level} is alkaline. To lower it, add organic matter like peat moss or compost."
    else: ph_suggestion = f"Your soil pH of {ph_level} is in an optimal range. To maintain it, continue to enrich your soil with organic compost."
    
    fertilizer_suggestion = "For general growth, an NPK fertilizer is a good start. Test your soil for specific nutrient deficiencies."
    pesticide_suggestion = "Regularly inspect for common pests like aphids and mites. Use neem oil as a first-line organic pesticide."
    
    if "rice" in crop: fertilizer_suggestion = "For Rice, use Urea as a nitrogen source after transplanting. A balanced NPK like 10-26-26 is crucial."
    if "wheat" in crop: pesticide_suggestion = "Aphids can be a problem. Monitor for yellow rust disease."
    
    return {
        "fertilizer_suggestion": fertilizer_suggestion,
        "pesticide_suggestion": pesticide_suggestion,
        "ph_suggestion": ph_suggestion
    }


# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Farming Assistant API is running!"}

@app.get("/live-weather")
def get_live_weather(city: str):
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY_HERE":
        raise HTTPException(status_code=500, detail="OpenWeatherMap API key is not set in the backend.")
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        return {
            "city": data["name"], "description": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"], "temperature_celsius": data["main"]["temp"],
            "feels_like_celsius": data["main"]["feels_like"], "temp_min_celsius": data["main"]["temp_min"],
            "temp_max_celsius": data["main"]["temp_max"], "humidity_percent": data["main"]["humidity"],
            "wind_speed_mps": data["wind"]["speed"]
        }
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404: raise HTTPException(status_code=404, detail=f"City '{city}' not found.")
        else: raise HTTPException(status_code=response.status_code, detail=f"Weather API error: {http_err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.post("/recommend-crop")
def recommend_crop(data: CropInput):
    if not crop_model:
        raise HTTPException(status_code=503, detail="Crop recommendation model is not loaded.")
    
    user_id = db_utils.get_user_id(data.user_email)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found.")

    model_input_data = data.dict(exclude={"user_email"})
    input_df = pd.DataFrame([model_input_data])
    input_encoded = pd.get_dummies(input_df, columns=['soil_type'])
    input_aligned = input_encoded.reindex(columns=crop_model_columns, fill_value=0)
    
    prediction = crop_model.predict(input_aligned)[0]
    
    db_utils.save_prediction(user_id, model_input_data, prediction)
    
    return {"recommended_crop": prediction}

@app.get("/prediction-history/{user_email}")
def get_prediction_history(user_email: str):
    user_id = db_utils.get_user_id(user_email)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found.")
    
    history = db_utils.load_prediction_history(user_id)
    return history

@app.post("/get-suggestions")
def get_suggestions(data: SuggestionInput):
    try:
        return get_llm_suggestions_mock(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
def chat_handler(chat_input: ChatInput):
    if not gemini_model:
        raise HTTPException(status_code=503, detail="Gemini model is not configured. Please check the API key.")
    try:
        history_gemini_format = [{"role": msg.role, "parts": msg.parts} for msg in chat_input.history]
        chat_session = gemini_model.start_chat(history=history_gemini_format)
        response = chat_session.send_message(chat_input.message)
        return {"role": "model", "parts": [response.text]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred with the Gemini API: {e}")

@app.post("/detect-disease")
async def detect_disease(
    file: UploadFile = File(...),
    prompt: str = Form("Please identify the disease in this plant leaf image. Describe the disease and suggest organic and chemical treatments.")
):
    if not gemini_model:
        raise HTTPException(status_code=503, detail="Gemini model is not configured. Please check the API key.")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")

    try:
        image_contents = await file.read()
        image_part = {"mime_type": file.content_type, "data": image_contents}
        response = gemini_model.generate_content([prompt, image_part])
        return {"diagnosis": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during disease detection: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)

