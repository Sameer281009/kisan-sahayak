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

try:
    genai.configure(api_key=GENAI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("API Key ki dikkat hai, Secrets check karein.")

# --- 2. OPTIMIZED FUNCTIONS ---
async def generate_male_voice(text):
    try:
        communicate = edge_tts.Communicate(text[:300], "hi-IN-MadhurNeural")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data
    except: return None

@st.cache_data(ttl=600)
def get_weather():
    try:
        loc = requests.get('http://ip-api.com/json/', timeout=5).json()
        city = loc.get('city', 'Dehradun')
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric&lang=hi"
        res = requests.get(url, timeout=5).json()
        return city, res['main']['temp'], res['weather'][0]['description']
    except: return "Dehradun", "--", "Net Slow Hai"

# --- 3. UI DESIGN ---
st.set_page_config(page_title="Kisan Sahayak", page_icon="🌾", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .weather-card { background-color: #1A1C23; padding: 15px; border-radius: 15px; border-left: 10px solid #4CAF50; text-align: center; margin-bottom: 20px;}
    .stButton>button { background-color: #1B5E20 !important; color: white !important; border-radius: 10px; width: 100%; height: 50px; }
    .dev-box { background: linear-gradient(145deg, #1e2129, #16191f); padding: 30px; border-radius: 20px; border: 1px solid #4CAF50; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION ---
with st.sidebar:
    selected = option_menu("Main Menu", ["Home", "Sarkari Schemes", "Farming Shop", "Developer"], 
                           icons=["house", "list-check", "cart", "person-circle"], default_index=0)

# --- 5. SEARCHBAR ---
st.write("### 🔍 Sawal Poochein")
search_q = st.text_input("", placeholder="Kuch bhi search karein...", key="main_search")
if search_q:
    try:
        with st.spinner("AI dhoond raha hai..."):
            res = model.generate_content(search_q)
            st.success(res.text)
    except: st.error("AI abhi respond nahi kar raha, kripya thodi der baad koshish karein.")

# --- 6. PAGE LOGIC ---
if selected == "Home":
    st.title("🌾 किसान सहायक")
    city, temp, desc = get_weather()
    st.markdown(f"<div class='weather-card'><h3>📍 {city} | 🌡️ {temp}°C | {desc}</h3></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        img = st.camera_input("📸 Photo", label_visibility="collapsed")
        if img:
            try:
                res = model.generate_content(["Is kheti ki photo ko samjhayein.", Image.open(img)])
                st.info(res.text)
            except: st.error("AI photo nahi dekh pa raha.")
    with col2:
        v_in = speech_to_text(language='hi', key='home_mic')
        if v_in:
            try:
                res = model.generate_content(v_in)
                st.success(res.text)
                audio = asyncio.run(generate_male_voice(res.text))
                if audio: st.audio(audio, autoplay=True)
            except: st.error("Mic error.")

elif selected == "Developer":
    st.markdown(f"""
        <div class="dev-box">
            <h1 style='color:#4CAF50;'>👨‍💻 Developer Profile</h1>
            <h2 style='margin-bottom:0;'>Sameer</h2>
            <p style='color:#AAA;'>11th Class (PCM) Student | Dehradun</p>
            <hr style='border-color:#2E7D32;'>
            <div style='text-align:left; background:#0E1117; padding:20px; border-radius:15px;'>
                <p><b>📍 Location:</b> Dehradun, Uttarakhand</p>
                <p><b>📧 Email:</b> sameer2810092009@gmail.com</p>
                <p><b>📞 Contact:</b> +91 9897979032</p>
                <p><b>🚀 Mission:</b> AI ki madad se kisanon ki zindagi asaan banana.</p>
            </div>
            <br>
            <p style='font-style:italic;'>Aapka apna Kisan Sahayak App Developer.</p>
        </div>
    """, unsafe_allow_html=True)
