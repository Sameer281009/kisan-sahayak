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
try:
    GENAI_API_KEY = st.secrets["GENAI_KEY"]
    WEATHER_API_KEY = st.secrets["WEATHER_KEY"]
except:
    GENAI_API_KEY = "AIzaSyBijMuhDr8AFaNvdY3DBozWTb6XRvw6eyE"
    WEATHER_API_KEY = "af1ec00f9fc32d17017dc84cdc7b7613"

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# --- 2. VOICE FUNCTION (OPTIMIZED) ---
async def generate_male_voice(text):
    try:
        communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data
    except:
        return None

# --- 3. WEATHER FUNCTION (WITH TIMEOUT) ---
def get_weather():
    try:
        # Timeout joda gaya hai taaki loading na fase
        loc_data = requests.get('http://ip-api.com/json/', timeout=5).json()
        city = loc_data.get('city', 'Delhi')
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=hi"
        res = requests.get(url, timeout=5).json()
        temp = res['main']['temp']
        desc = res['weather'][0]['description']
        return city, temp, desc.capitalize()
    except:
        return "Delhi", "--", "Net Slow Hai"

# --- 4. UI STYLING ---
st.set_page_config(page_title="Kisan Sahayak", page_icon="🌾", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3, p, span, label { color: #E0E0E0 !important; }
    .weather-card {
        background-color: #1A1C23; padding: 15px; border-radius: 15px;
        border-left: 8px solid #4CAF50; text-align: center; margin-bottom: 20px;
    }
    .stButton>button { 
        border-radius: 15px; height: 80px; font-size: 20px !important;
        background-color: #1B5E20 !important; color: white !important;
    }
    /* Loading Spinner Color */
    .stSpinner > div > div { border-top-color: #4CAF50 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. NAVIGATION (STABLE VERSION) ---
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu", 
        options=["Home", "Sarkari Schemes", "Farming Shop", "Developer"], 
        icons=["house", "bank", "cart", "person"], 
        menu_icon="cast", default_index=0,
    )

# --- 6. PAGE LOGIC ---

if selected == "Home":
    st.title("🌾 किसान सहायक")
    
    # Weather Display
    city, temp, desc = get_weather()
    st.markdown(f"<div class='weather-card'><p style='color:#AAA;'>📍 {city}</p><h2 style='color:#4CAF50; margin:0;'>🌡️ {temp}°C | {desc}</h2></div>", unsafe_allow_html=True)

    # Autoplay greeting logic (Sirf ek baar chale)
    if 'greeted' not in st.session_state:
        welcome_text = "नमस्कार किसान भाई, मैं आपकी किस तरह मदद कर सकता हूँ?"
        audio_bytes = asyncio.run(generate_male_voice(welcome_text))
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        st.session_state['greeted'] = True

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📸 फोटो")
        img_file = st.camera_input("Pehchane", label_visibility="collapsed")
        if img_file:
            img = Image.open(img_file)
            with st.spinner("AI dekh raha hai..."):
                res = model.generate_content(["Is photo ka Hindi mein jawab dein.", img])
                st.write(res.text)
                st.audio(asyncio.run(generate_male_voice(res.text[:300])), autoplay=True)

    with col2:
        st.subheader("🎤 बोलें")
        v_input = speech_to_text(language='hi', start_prompt="Yahan Dabayein", key='mic_home')
        if v_input:
            with st.spinner("Soch raha hoon..."):
                res = model.generate_content(v_input)
                st.write(res.text)
                st.audio(asyncio.run(generate_male_voice(res.text[:300])), autoplay=True)

elif selected == "Sarkari Schemes":
    st.header("📜 सरकारी योजनाएं")
    st.info("Kisan bhai, yahan sabhi nayi yojanaon ki jankari milegi.")
    
    # Simple list to avoid heavy processing
    schemes = ["PM Kisan Samman Nidhi", "Fasal Bima Yojana", "Kusum Yojana"]
    for s in schemes:
        if st.button(f"Jaane: {s}"):
            res = model.generate_content(f"{s} scheme ki jankari Hindi mein dein.")
            st.success(res.text)

elif selected == "Farming Shop":
    st.header("🛒 खेती की दुकान")
    st.write("Dawai ya khad ki photo upload karein ya naam bolein.")
    shop_input = st.text_input("Dawai ka naam likhein ya mic use karein:")
    if shop_input:
        res = model.generate_content(f"{shop_input} ke upyog aur daam batayein.")
        st.info(res.text)

elif selected == "Developer":
    st.header("👨‍💻 Developer Page")
    st.balloons()
    st.markdown("""
    ### Developed by: [Your Name]
    **Mission:** Kisanon ko AI se jodna.
    **Tech:** Python, Streamlit, Gemini AI.
    """)
