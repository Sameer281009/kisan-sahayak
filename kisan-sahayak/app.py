import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_mic_recorder import speech_to_text
from streamlit_option_menu import option_menu
import asyncio
import edge_tts
import requests

# --- 1. API CONFIGURATION ---
GENAI_KEY = st.secrets.get("GENAI_KEY", "AIzaSyDPR1ngpDDEotM1f8JWTgNOaFIMVfrGk5o")
WEATHER_KEY = st.secrets.get("WEATHER_KEY", "af1ec00f9fc32d17017dc84cdc7b7613")

try:
    genai.configure(api_key=GENAI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("API Error: Nayi Key Secrets mein daalein.")

# --- 2. VOICE & WEATHER ---
async def generate_voice(text):
    try:
        communicate = edge_tts.Communicate(text[:250], "hi-IN-MadhurNeural")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio": audio_data += chunk["data"]
        return audio_data
    except: return None

@st.cache_data(ttl=3600)
def get_weather():
    try:
        res = requests.get('http://ip-api.com/json/', timeout=5).json()
        city = res.get('city', 'Dehradun')
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric&lang=hi"
        w_res = requests.get(url, timeout=5).json()
        return city, w_res['main']['temp'], w_res['weather'][0]['description']
    except: return "Dehradun", "--", "Net Slow"

# --- 3. UI DESIGN ---
st.set_page_config(page_title="Kisan Sahayak", page_icon="🌾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .header-box { background: #1A1C23; padding: 15px; border-radius: 15px; border-bottom: 4px solid #4CAF50; margin-bottom: 20px; text-align: center; }
    .kisan-card { background: #1A1C23; padding: 20px; border-radius: 15px; border: 1px solid #2E7D32; text-align: center; height: 100%; transition: 0.3s; }
    .kisan-card:hover { border-color: #4CAF50; background: #252932; }
    .stButton>button { border-radius: 10px; background-color: #1B5E20 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. GLOBAL HEADER (Camera + Mic) ---
with st.container():
    st.markdown("<div class='header-box'><h1>🌾 किसान सहायक</h1></div>", unsafe_allow_html=True)
    h_col1, h_col2, h_col3 = st.columns([1, 2, 1])
    
    with h_col1:
        img_file
