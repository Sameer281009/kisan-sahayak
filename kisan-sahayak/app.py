import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_mic_recorder import speech_to_text
from streamlit_option_menu import option_menu
import asyncio
import edge_tts
import requests

# --- 1. CONFIG ---
K1 = "AIzaSyAgSqPVmLHwa0DkrFkiu3dZV_gbLMxAHGg"
K2 = "af1ec00f9fc32d17017dc84cdc7b7613"
genai.configure(api_key=K1)

def get_ai(p, img=None):
    for m in ['gemini-1.5-flash', 'gemini-pro']:
        try:
            mdl = genai.GenerativeModel(m)
            c = [p, img] if img else p
            return mdl.generate_content(c).text
        except: continue
    return "Error: AI Busy"

def get_w():
    try:
        u = f"http://api.openweathermap.org/data/2.5/weather?q=Dehradun&appid={K2}&units=metric&lang=hi"
        r = requests.get(u, timeout=5).json()
        return r['main']['temp'], r['weather'][0]['description']
    except: return "--", "No Data"

# --- 2. STYLE ---
st.set_page_config(page_title="Kisan Sahayak", layout="wide")
st.markdown("<style>.stApp{background:#0E1117;color:white}.h{background:#1A1C23;padding:20px;border-radius:15px;border-bottom:5px solid #4CAF50;text-align:center;margin-bottom:20px}.dev{background:#1A1C23;padding:30px;border-radius:20px;border:2px solid #4CAF50;text-align:center}</style>", unsafe_allow_html=True)

menu = ["Home", "Weather", "Schemes", "Shop", "About"]
sel = option_menu(None, menu, icons=["house", "cloud", "book", "cart", "person"], orientation="horizontal")

# --- 3. LOGIC ---
if sel == "Home":
    st.markdown("<div class='h'><h1>🌾 किसान सहायक AI</h1></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: i = st.camera_input("📸")
    with c2: t = st.text_input("🔍 Sawal:")
    with c3: 
        st.write("🎤 Mic")
        v = speech_to_text(language='hi', key='hmic')
    q = t if t else v
    if q or i:
        with st.spinner("..."):
            im = Image.open(i) if i else None
            txt = q if q else "Explain photo"
            st.success(get_ai(txt, im))

elif sel == "Weather":
    st.header("🌦️ Mausam")
    tmp, des = get_w()
    st.metric("Dehradun", f"{tmp} °C")
    st.write(f"Condition: {des}")

elif sel == "Schemes":
    st.header("📜 Yojana")
    if st.button("PM Kisan"): st.write(get_ai("PM Kisan in Hindi"))

elif sel == "Shop":
    st.header("🛒 Shop")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: si = st.camera_input("📸 Item")
    with c2: stxt = st.text_input("🔍 Search:")
    with c3: sv = speech_to_text(language='hi', key='smic')
    sq = stxt if stxt else sv
    if sq or si:
        with st.spinner("Searching..."):
            p = f"Item: {sq}. Name, Work, Buy link, Local shop. Hindi."
            st.success(get_ai(p, Image.open(si) if si else None))

elif sel == "About":
    st.markdown("<div class='dev'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color:#4CAF50;'>👨‍💻 Developer</h1>", unsafe_allow_html=True)
    st.markdown("<h2>समीर (Sameer)</h2>", unsafe_allow_html=True)
    st.markdown("<p>11th PCM | Dehradun</p>", unsafe_allow_html=True)
    st.markdown("<p>📧 sameer2810092009@gmail.com</p>", unsafe_allow_html=True)
    st.markdown("<p>📞 9897979032</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
