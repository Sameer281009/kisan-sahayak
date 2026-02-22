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

# CSS Styling (Iske triple quotes fix hain)
st.markdown("<style>.stApp { background-color: #0E1117; color: white; } .header { background: #1A1C23; padding: 20px; border-radius: 15px; border-bottom: 5px solid #4CAF50; text-align: center; margin-bottom: 20px; } .dev-box { background: #1A1C23; padding: 30px; border-radius: 20px; border: 2px solid #4CAF50; text-align: center; }</style>", unsafe_allow_html=True)

sel = option_menu(None, ["Home", "Weather", "Schemes", "Shop", "About"], 
    icons=["house", "cloud-sun", "book", "cart", "person-badge"], 
    orientation="horizontal", styles={"container": {"background-color": "#1A1C23"}})

# --- 3. PAGES ---
if sel == "Home":
    st.markdown("<div class='header'><h1>🌾 किसान सहायक AI</h1></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1: img = st.camera_input("📸 Photo")
    with c2: txt = st.text_input("🔍 Sawal:")
    with c3: 
        st.write("🎤 Mic")
        v_in = speech_to_text(language='hi', key='home_mic')
    q = txt if txt else v_in
    if q or img:
        with st.spinner("AI Jawab nikaal raha hai..."):
            ans = get_ai_response(q if q else "Is photo ko samjh
