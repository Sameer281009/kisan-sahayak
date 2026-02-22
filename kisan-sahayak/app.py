import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_mic_recorder import speech_to_text
from streamlit_option_menu import option_menu
import asyncio
import edge_tts
import requests

# --- 1. CONFIG ---
API_KEY = "AIzaSyAgSqPVmLHwa0DkrFkiu3dZV_gbLMxAHGg"
W_KEY = "af1ec00f9fc32d17017dc84cdc7b7613"
genai.configure(api_key=API_KEY)

def get_ai_response(prompt, image=None):
    models = ['gemini-1.5-flash', 'gemini-pro']
    for m in models:
        try:
            model = genai.GenerativeModel(m)
            content = [prompt, image] if image else prompt
            res = model.generate_content(content)
            return res.text
        except: continue
    return "AI Busy hai. Nayi Key ya Net check karein."

def get_weather():
    try:
        u = f"http://api.openweathermap.org/data/2.5/weather?q=Dehradun&appid={W_KEY}&units=metric&lang=hi"
        r = requests.get(u, timeout=5).json()
        return "Dehradun", r['main']['temp'], r['weather'][0]['description']
    except: return "Dehradun", "--", "No Data"

# --- 2. UI STYLE ---
st.set_page_config(page_title="Kisan Sahayak", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    .header { background: #1A1C23; padding: 20px; border-radius: 15px; border-bottom: 5px solid #4CAF50;
