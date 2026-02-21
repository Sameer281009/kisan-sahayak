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
# Key ko pehle secrets se check karo, nahi toh manual
GENAI_KEY = st.secrets.get("GENAI_KEY", "AIzaSyBijMuhDr8AFaNvdY3DBozWTb6XRvw6eyE")
WEATHER_KEY = st.secrets.get("WEATHER_KEY", "af1ec00f9fc32d17017dc84cdc7b7613")

genai.configure(api_key=GENAI_KEY)

# Error se bachne ke liye alternate model name
try:
    model = genai.GenerativeModel('gemini-1.5-flash') # 1.5-flash zyada stable hai
except:
    model = genai.GenerativeModel('gemini-pro')

# --- 2. OPTIMIZED AUDIO & WEATHER ---
async def generate_male_voice(text):
    try:
        # Limit text to 300 chars for faster response
        communicate = edge_tts.Communicate(text[:300], "hi-IN-MadhurNeural")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data
    except: return None

@st.cache_data(ttl=3600)
def get_weather():
    try:
        # Use a more stable IP service
        city_res = requests.get('https://ipapi.co/json/', timeout=5).json()
        city = city_res.get('city', 'Delhi')
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric&lang=hi"
        res = requests.get(url, timeout=5).json()
        return city, res['main']['temp'], res['weather'][0]['description']
    except: return "India", "--", "Mausam ki jankari nahi mili"

# --- 3. UI STYLING ---
st.set_page_config(page_title="Kisan Sahayak", page_icon="🌾", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stTextInput>div>div>input { background-color: #1A1C23; color: white; border: 1px solid #4CAF50; }
    .weather-card { background-color: #1A1C23; padding: 15px; border-radius: 15px; border-left: 10px solid #4CAF50; text-align: center; }
    .stButton>button { background-color: #1B5E20 !important; color: white !important; border-radius: 12px; height: 50px; width: 100%; }
    .dev-box { background-color: #1A1C23; padding: 20px; border-radius: 15px; border: 1px solid #4CAF50; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION ---
selected = option_menu(
    menu_title=None, 
    options=["Home", "सरकारी योजनाएं", "खेती Shop", "Developer"], 
    icons=["house", "list-check", "cart", "person"], 
    default_index=0, orientation="horizontal",
    styles={"container": {"background-color": "#1A1C23"}, "nav-link-selected": {"background-color": "#2E7D32"}}
)

# --- 5. SEARCHBAR (Common for all) ---
st.write("---")
user_query = st.text_input("🔍 Kuch bhi poochein (Search):", key="search_bar")
if user_query:
    with st.spinner("AI dhoond raha hai..."):
        try:
            response = model.generate_content(user_query)
            st.success(response.text)
        except Exception as e:
            st.error("API Error: Kripya 'Secrets' mein key check karein.")

# --- 6. PAGE LOGIC ---

if selected == "Home":
    st.title("🌾 किसान सहायक")
    
    city, temp, desc = get_weather()
    st.markdown(f"<div class='weather-card'><h3>📍 {city} | 🌡️ {temp}°C | {desc}</h3></div>", unsafe_allow_html=True)

    # Greeting Audio (Only once per session)
    if "greeted" not in st.session_state:
        welcome = "नमस्कार किसान भाई, मैं आपकी किस तरह मदद कर सकता हूँ?"
        audio = asyncio.run(generate_male_voice(welcome))
        if audio: st.audio(audio, autoplay=True)
        st.session_state.greeted = True

    col1, col2 = st.columns(2)
    with col1:
        st.write("### 📸 फोटो")
        img = st.camera_input("camera", label_visibility="collapsed")
        if img:
            res = model.generate_content(["Is photo ke baare mein Hindi mein batayein.", Image.open(img)])
            st.write(res.text)
    with col2:
        st.write("### 🎤 बोलें")
        v_in = speech_to_text(language='hi', key='home_mic')
        if v_in:
            res = model.generate_content(v_in)
            st.write(res.text)
            audio = asyncio.run(generate_male_voice(res.text))
            if audio: st.audio(audio, autoplay=True)

elif selected == "Developer":
    st.markdown(f"""
        <div class="dev-box">
            <h2 style='color:#4CAF50;'>नमस्ते, मैं हूँ [Aapka Naam]</h2>
            <p>Maine ye app Kisan bhaiyon ki madad ke liye banayi hai.</p>
            <p><b>Tech Stack:</b> Python, Gemini Flash, Edge-TTS</p>
            <p>Dhanyawad!</p>
        </div>
    """, unsafe_allow_html=True)

# Note: Baki pages ke liye bhi same try-except block use karein error se bachne ke liye.
