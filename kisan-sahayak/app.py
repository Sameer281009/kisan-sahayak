import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_mic_recorder import speech_to_text
from streamlit_option_menu import option_menu
import asyncio
import edge_tts
import requests

# --- 1. CONFIG (Using full model path) ---
try:
    GEN_K = st.secrets["GENAI_KEY"]
    W_K = st.secrets["WEATHER_KEY"]
except:
    GEN_K = "AIzaSyDPR1ngpDDEotM1f8JWTgNOaFIMVfrGk5o"
    W_K = "af1ec00f9fc32d17017dc84cdc7b7613"

genai.configure(api_key=GEN_K)

# Model name fixed to full path to avoid 'NotFound' error
MODEL_NAME = 'models/gemini-1.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

# --- 2. FUNCTIONS ---
async def speak(text):
    try:
        tpl = edge_tts.Communicate(text[:250], "hi-IN-MadhurNeural")
        data = b""
        async for chk in tpl.stream():
            if chk["type"] == "audio": data += chk["data"]
        return data
    except: return None

@st.cache_data(ttl=3600)
def get_w():
    try:
        r = requests.get('http://ip-api.com/json/', timeout=5).json()
        c = r.get('city', 'Dehradun')
        u = f"http://api.openweathermap.org/data/2.5/weather?q={c}&appid={W_K}&units=metric&lang=hi"
        res = requests.get(u, timeout=5).json()
        return c, res['main']['temp'], res['weather'][0]['description']
    except: return "Dehradun", "--", "Net Slow"

# --- 3. UI ---
st.set_page_config(page_title="Kisan Sahayak", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    .header { background: #1A1C23; padding: 20px; border-radius: 15px; border-bottom: 5px solid #4CAF50; text-align: center; margin-bottom: 20px;}
    .card { background: #1A1C23; padding: 20px; border-radius: 15px; border: 1px solid #2E7D32; text-align: center; }
    .dev { background: #16191f; padding: 30px; border-radius: 20px; border: 2px solid #4CAF50; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h1>🌾 किसान सहायक AI</h1></div>", unsafe_allow_html=True)

# Main Inputs
c1, c2, c3 = st.columns([1, 2, 1])
with c1: img_file = st.camera_input("📸 Photo")
with c2: txt_input = st.text_input("🔍 Sawal:", placeholder="Yahan likhein...")
with c3: 
    st.write("🎤 Mic")
    v_in = speech_to_text(language='hi', key='mic')

# Logic
final_q = txt_input if txt_input else v_in

if final_q or img_file:
    with st.spinner("AI dhoond raha hai..."):
        try:
            if img_file:
                p_img = Image.open(img_file)
                res = model.generate_content(["Kisan ki madad karein Hindi mein:", p_img])
            else:
                res = model.generate_content(final_q)
            
            st.success(res.text)
            if st.button("🔊 Suniye"):
                aud = asyncio.run(speak(res.text))
                if aud: st.audio(aud, format="audio/mp3", autoplay=True)
        except Exception as e:
            st.error("AI service abhi busy hai, 1 min rukiye.")

# --- 4. NAV ---
sel = option_menu(None, ["Home", "Schemes", "Shop", "Dev"], 
    icons=["house", "book", "cart", "person"], orientation="horizontal",
    styles={"container": {"background-color": "#1A1C23"}})

if sel == "Home":
    city, temp, desc = get_w()
    st.info(f"📍 {city} | 🌡️ {temp}°C | {desc}")
    st.write("### Swagat hai Sameer!")

elif sel == "Schemes":
    sc1, sc2 = st.columns(2)
    with sc1:
        if st.button("PM Kisan Jankari"):
            try:
                ans = model.generate_content("PM Kisan Samman Nidhi details in Hindi short")
                st.write(ans.text)
            except: st.error("Model error")
    with sc2:
        if st.button("Fasal Bima Jankari"):
            try:
                ans = model.generate_content("Pradhan Mantri Fasal Bima Yojana Hindi")
                st.write(ans.text)
            except: st.error("Model error")

elif sel == "Dev":
    st.markdown(f"""
    <div class='dev'>
        <h2>Sameer (11th PCM)</h2>
        <p>Dehradun, Uttarakhand</p>
        <hr>
        <p>Email: sameer2810092009@gmail.com</p>
        <p>Phone: 9897979032</p>
    </div>
    """, unsafe_allow_html=True)
