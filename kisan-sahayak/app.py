import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_mic_recorder import speech_to_text
from streamlit_option_menu import option_menu
import asyncio
import edge_tts
import io
import requests

# --- 1. API CONFIGURATION ---
GENAI_KEY = st.secrets.get("GENAI_KEY", "AIzaSyBijMuhDr8AFaNvdY3DBozWTb6XRvw6eyE")
WEATHER_KEY = st.secrets.get("WEATHER_KEY", "af1ec00f9fc32d17017dc84cdc7b7613")

# Model try-except block to handle model name issues
try:
    genai.configure(api_key=GENAI_KEY)
    
    # Hum pehle 'gemini-1.5-flash' try karenge
    # Agar ye fail ho toh 'gemini-pro' backup rahega
    model_name = 'gemini-1.5-flash' 
    model = genai.GenerativeModel(model_name)
    
    # Test call to check if model name is accepted
    # Agar error aana hoga toh yahi aa jayega
except Exception as e:
    model = genai.GenerativeModel('gemini-pro')

# --- 2. OPTIMIZED AUDIO & WEATHER ---
async def generate_male_voice(text):
    try:
        communicate = edge_tts.Communicate(text[:250], "hi-IN-MadhurNeural")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data
    except: return None

@st.cache_data(ttl=3600)
def get_weather():
    try:
        # Stable IP detection
        loc = requests.get('http://ip-api.com/json/', timeout=8).json()
        city = loc.get('city', 'Dehradun')
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric&lang=hi"
        res = requests.get(url, timeout=8).json()
        return city, res['main']['temp'], res['weather'][0]['description']
    except: return "Dehradun", "--", "Mausam check karein"

# --- 3. UI DESIGN ---
st.set_page_config(page_title="Kisan Sahayak", page_icon="🌾", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .weather-card { background-color: #1A1C23; padding: 15px; border-radius: 15px; border-left: 10px solid #4CAF50; text-align: center; margin-bottom: 20px;}
    .stButton>button { background-color: #1B5E20 !important; color: white !important; border-radius: 12px; height: 50px; font-weight: bold; }
    .dev-box { background: #1A1C23; padding: 25px; border-radius: 20px; border: 1px solid #4CAF50; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION ---
with st.sidebar:
    selected = option_menu("Main Menu", ["Home", "Sarkari Schemes", "Farming Shop", "Developer"], 
                           icons=["house", "list-check", "cart", "person-badge"], default_index=0)

# --- 5. SEARCHBAR ---
st.write("---")
search_q = st.text_input("🔍 Sawal Poochein:", placeholder="Yahan likhein...")

if search_q:
    with st.spinner("AI Jawab taiyar kar raha hai..."):
        try:
            # Try with primary model
            res = model.generate_content(search_q)
            st.success(res.text)
        except:
            try:
                # Backup: try with 'gemini-pro' if flash fails
                backup_model = genai.GenerativeModel('gemini-pro')
                res = backup_model.generate_content(search_q)
                st.success(res.text)
            except:
                st.error("Google API Limit: Kripya 1 minute baad koshish karein ya naya API Key generate karein.")

# --- 6. PAGE LOGIC ---
if selected == "Home":
    st.title("🌾 किसान सहायक")
    city, temp, desc = get_weather()
    st.markdown(f"<div class='weather-card'><h3>📍 {city} | 🌡️ {temp}°C | {desc}</h3></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        img = st.camera_input("📸 Photo")
        if img:
            try:
                res = model.generate_content(["Is photo ko kisan ke liye Hindi mein samjhayein.", Image.open(img)])
                st.info(res.text)
            except: st.warning("Photo AI process nahi ho payi. Text search use karein.")
    with col2:
        v_in = speech_to_text(language='hi', key='home_mic')
        if v_in:
            try:
                res = model.generate_content(v_in)
                st.success(res.text)
                audio = asyncio.run(generate_male_voice(res.text))
                if audio: st.audio(audio, autoplay=True)
            except: st.error("Awaz samajhne mein dikkat hui.")

elif selected == "Developer":
    st.markdown(f"""
        <div class="dev-box">
            <h1 style='color:#4CAF50;'>Developer Details</h1>
            <h2 style='margin:0;'>Sameer</h2>
            <p style='color:#AAA;'>11th Class PCM Student | Dehradun</p>
            <hr style='border-color:#2E7D32;'>
            <div style='text-align:left; background:#0E1117; padding:20px; border-radius:15px;'>
                <p>📧 <b>Gmail:</b> sameer2810092009@gmail.com</p>
                <p>📞 <b>Phone:</b> 9897979032</p>
                <p>📍 <b>City:</b> Dehradun, Uttarakhand</p>
            </div>
            <p style='margin-top:15px;'><i>"Technology ka upyog kisanon ki unnati ke liye."</i></p>
        </div>
    """, unsafe_allow_html=True)
