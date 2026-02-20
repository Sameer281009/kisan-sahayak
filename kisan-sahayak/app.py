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
GENAI_API_KEY = "AIzaSyBijMuhDr8AFaNvdY3DBozWTb6XRvw6eyE"
WEATHER_API_KEY = "af1ec00f9fc32d17017dc84cdc7b7613"

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-flash-latest')

# --- 2. HELPER FUNCTIONS ---

async def generate_male_voice(text):
    """Natural Male Hindustani awaaz (Madhur)"""
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

def get_weather():
    """Behtar Location Detection ke saath Weather"""
    try:
        # IP se location nikalne ka sabse bharosemand tareeka
        loc_data = requests.get('http://ip-api.com/json/').json()
        city = loc_data.get('city', 'Delhi')
        
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=hi"
        res = requests.get(url).json()
        
        if res.get("cod") != 200: # Agar city nahi mili
            return "Khet", "--", "Mausam ki jaankari nahi mili"
            
        temp = res['main']['temp']
        desc = res['weather'][0]['description']
        return city, temp, desc.capitalize()
    except Exception as e:
        return "Delhi", "--", "Internet check karein"

# --- 3. DARK MODE UI STYLING ---
st.set_page_config(page_title="Kisan Sahayak AI", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3, p, span, label { color: #E0E0E0 !important; }
    
    /* Weather Card Design */
    .weather-card {
        background-color: #1A1C23;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        border-left: 10px solid #4CAF50;
        margin-bottom: 25px;
        text-align: center;
    }
    .weather-text { color: #4CAF50 !important; font-weight: bold; font-size: 32px; margin: 0; }
    .city-text { color: #AAAAAA !important; font-size: 20px; margin-bottom: 5px; }

    /* Action Buttons (Camera & Mic) */
    .stButton>button { 
        border-radius: 20px; height: 120px; font-size: 24px !important;
        background-color: #1B5E20 !important; color: #FFFFFF !important;
        border: 2px solid #2E7D32; font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2E7D32 !important;
        border: 2px solid #FFFFFF;
    }

    /* Tabs Styling */
    .nav-link { font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVIGATION (FOOTER) ---
selected = option_menu(
    menu_title=None, 
    options=["Home", "सरकारी योजनाएं", "खेती Shop"], 
    icons=["house-fill", "bank2", "cart-fill"], 
    default_index=0, 
    orientation="horizontal",
    styles={
        "container": {"background-color": "#1A1C23", "padding": "0!important"},
        "icon": {"color": "#4CAF50", "font-size": "20px"}, 
        "nav-link": {"color": "white", "font-size": "16px", "text-align": "center"},
        "nav-link-selected": {"background-color": "#2E7D32"},
    }
)

# --- 5. MAIN LOGIC ---

if selected == "Home":
    st.title("🌾 किसान सहायक")
    
    # Weather Display (Dynamic Location)
    city, temp, desc = get_weather()
    st.markdown(f"""
        <div class="weather-card">
            <p class="city-text">📍 आपके यहाँ का मौसम ({city}):</p>
            <p class="weather-text">🌡️ {temp}°C | {desc}</p>
        </div>
    """, unsafe_allow_html=True)

    # Greeting (Male Voice)
    welcome_text = "नमस्कार किसान भाई, मैं आपकी किस तरह मदद कर सकता हूँ?"
    audio_bytes = asyncio.run(generate_male_voice(welcome_text))
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    
    st.subheader(welcome_text)

    # Action Buttons
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 📸 फोटो खींचें")
        img_file = st.camera_input("camera", label_visibility="collapsed")
        if img_file:
            img = Image.open(img_file)
            with st.spinner("AI जाँच कर रहा है..."):
                response = model.generate_content(["Is photo mein jo kheti ki cheez hai, use Hindi mein samjhayein.", img])
                st.success(response.text)
                ans_audio = asyncio.run(generate_male_voice(response.text[:300]))
                st.audio(ans_audio, autoplay=True)

    with col2:
        st.write("### 🎤 बोलकर पूछें")
        v_input = speech_to_text(language='hi', start_prompt="यहाँ दबाएं", key='mic_home')
        if v_input:
            with st.spinner("सोच रहा हूँ..."):
                response = model.generate_content(f"Kisan ki samasya: {v_input}. Jawab saral hindi mein dein.")
                st.success(response.text)
                ans_audio = asyncio.run(generate_male_voice(response.text[:300]))
                st.audio(ans_audio, autoplay=True)

# Footer Pages (Sarkari Schemes & Shop)
elif selected == "सरकारी योजनाएं":
    st.header("📜 सरकारी योजनाएं")
    st.write("यहाँ आप योजनाओं के बारे में जान सकते हैं...")
    # (Aap purana schemes wala code yahan paste kar sakte hain)

elif selected == "खेती Shop":
    st.header("🛒 खेती Shop")
    st.write("दवाई, खाद और औजारों की जानकारी...")
    # (Aap purana shop wala code yahan paste kar sakte hain)