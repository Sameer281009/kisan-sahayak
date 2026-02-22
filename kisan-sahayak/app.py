import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_mic_recorder import speech_to_text
from streamlit_option_menu import option_menu
import asyncio
import edge_tts
import time

# --- 1. API CONFIG ---
# Secrets mein GENAI_KEY check kar lena Sameer
GEN_K = st.secrets.get("GENAI_KEY", "AIzaSyAHYhcqdKgRTqJk6hojwMEeIJwU4ZXcSv8") 

genai.configure(api_key=GEN_K)

def get_ai_response(prompt, image=None):
    # Sabse stable model names
    stable_models = ['gemini-1.5-flash-latest', 'gemini-1.5-pro-latest']
    
    for m_name in stable_models:
        try:
            model = genai.GenerativeModel(m_name)
            if image:
                res = model.generate_content([prompt, image])
            else:
                res = model.generate_content(prompt)
            return res.text
        except Exception as e:
            error_str = str(e).lower()
            if "403" in error_str:
                return "PERMISSION_ERROR"
            if "429" in error_str:
                return "LIMIT_ERROR"
            continue
    return "UNKNOWN_ERROR"

# --- 2. UI STYLING ---
st.set_page_config(page_title="Kisan Sahayak", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    .header { background: #1A1C23; padding: 20px; border-radius: 15px; border-bottom: 5px solid #4CAF50; text-align: center; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h1>🌾 किसान सहायक AI</h1></div>", unsafe_allow_html=True)

# Main Inputs
c1, c2, c3 = st.columns([1, 2, 1])
with c1: img_file = st.camera_input("📸 Photo")
with c2: txt_in = st.text_input("🔍 Sawal likhein:", key="user_query")
with c3: 
    st.write("🎤 Mic")
    v_in = speech_to_text(language='hi', key='mic_input')

final_q = txt_in if txt_in else v_in

if final_q or img_file:
    with st.spinner("AI dhoond raha hai..."):
        p_img = Image.open(img_file) if img_file else None
        ans = get_ai_response(final_q if final_q else "Is photo ko samjhayein", p_img)
        
        if ans == "PERMISSION_ERROR":
            st.error("API Key Permission Issue (403).")
            st.info("Sameer, Google AI Studio mein jaakar check karo ki 'Gemini API' enable hai ya nahi.")
        elif ans == "LIMIT_ERROR":
            st.warning("Google abhi thoda thaka hua hai (429). 10-15 second rukiye.")
        elif ans == "UNKNOWN_ERROR":
            st.error("Model nahi mil raha (404). Nayi key try karein.")
        else:
            st.success(ans)

# --- 3. NAV ---
sel = option_menu(None, ["Home", "Dev"], icons=["house", "person"], orientation="horizontal")

if sel == "Dev":
    st.info("Sameer | 11th PCM | Dehradun | 9897979032")
