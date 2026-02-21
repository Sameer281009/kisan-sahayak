import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_mic_recorder import speech_to_text
from streamlit_option_menu import option_menu
import asyncio
import edge_tts
import requests

# --- 1. API CONFIGURATION (Using your new key) ---
try:
    GENAI_KEY = st.secrets["GENAI_KEY"]
    WEATHER_KEY = st.secrets["WEATHER_KEY"]
except:
    # Local testing ke liye tumhari nayi key
    GENAI_KEY = "AIzaSyDPR1ngpDDEotM1f8JWTgNOaFIMVfrGk5o"
    WEATHER_KEY = "af1ec00f9fc32d17017dc84cdc7b7613"

genai.configure(api_key=GENAI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. HELPER FUNCTIONS ---
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

# --- 3. UI STYLING ---
st.set_page_config(page_title="Kisan Sahayak AI", page_icon="🌾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .header-box { background: #1A1C23; padding: 20px; border-radius: 15px; border-bottom: 5px solid #4CAF50; text-align: center; margin-bottom: 25px; }
    .kisan-card { background: #1A1C23; padding: 20px; border-radius: 15px; border: 1px solid #2E7D32; text-align: center; min-height: 200px; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #1B5E20 !important; color: white !important; font-weight: bold; }
    .dev-card { background: linear-gradient(145deg, #1e2129, #16191f); padding: 30px; border-radius: 20px; border: 2px solid #4CAF50; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 4. GLOBAL HEADER (Always Visible) ---
st.markdown("<div class='header-box'><h1>🌾 किसान सहायक AI</h1><p>Samajhdar Kheti, Khushal Kisan</p></div>", unsafe_allow_html=True)

# NameError se bachne ke liye variables initialize karein
img_file = None
v_in = None
prompt = None

h_col1, h_col2, h_col3 = st.columns([1, 2, 1])

with h_col1:
    img_file = st.camera_input("📸 फोटो लें", key="global_cam")

with h_col2:
    global_q = st.text_input("🔍 सवाल पूछें या फोटो का इस्तेमाल करें:", placeholder="यहाँ लिखें... जैसे: ग
