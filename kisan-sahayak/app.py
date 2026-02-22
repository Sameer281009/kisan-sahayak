import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_mic_recorder import speech_to_text
from streamlit_option_menu import option_menu
import asyncio
import edge_tts
import requests

# --- 1. CONFIGURATION ---
API_KEY = "AIzaSyAgSqPVmLHwa0DkrFkiu3dZV_gbLMxAHGg"
WEATHER_KEY = "af1ec00f9fc32d17017dc84cdc7b7613"

genai.configure(api_key=API_KEY)

# AI Response Logic
def get_ai_response(prompt, image=None):
    models = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-pro']
    for m in models:
        try:
            model = genai.GenerativeModel(m)
            if image:
                res = model.generate_content([prompt, image])
            else:
                res = model.generate_content(prompt)
            return res.text
        except:
            continue
    return "AI abhi offline hai. Nayi API Key ya Internet check karein."

# Fixed Weather Logic (Line 35 fixed)
def get_weather_data():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Dehradun&appid={WEATHER_KEY}&units=metric&lang=hi"
        res = requests.get(url, timeout=5).json()
        return "Dehradun", res['main']['temp'], res['weather'][0]['description']
    except:
        return "De
