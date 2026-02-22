import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_mic_recorder import speech_to_text
from streamlit_option_menu import option_menu
import asyncio
import edge_tts
import requests

# --- 1. CONFIG ---
# Sameer, tumhari nayi key yahan hai
API_KEY = "AIzaSyAgSqPVmLHwa0DkrFkiu3dZV_gbLMxAHGg"
W_KEY = "af1ec00f9fc32d17017dc84cdc7b7613"

genai.configure(api_key=API_KEY)

def get_ai_response(prompt, image=None):
    models = ['gemini-1.5-flash', 'gemini-pro']
    for m in models:
        try:
            model = genai.GenerativeModel(m)
            if image:
                res = model.generate_content([prompt, image])
            else:
                res = model.generate_content(prompt)
            return res.text
        except:
            continue
    return "AI Busy hai. Nayi Key ya Net check karein."

def get_weather():
    try:
        u = f"http://api.openweathermap.org/data/2.5/weather?q=Dehradun&appid={W_KEY}&units=metric&lang=hi"
        r = requests.get(u, timeout=5).json()
        temp = r['main']['temp']
        desc = r['weather'][0]['description']
        return "Dehradun", temp, desc
    except:
        return "Dehradun", "--", "No Data"

async def speak(text):
    try:
        tpl = edge_tts.Communicate(text[:250], "hi-IN-MadhurNeural")
        data = b""
        async for chk in tpl.stream():
            if chk["type"] == "audio": data += chk["data"]
        return data
    except: return None

# --- 2. UI STYLE ---
st.set_page_config(page_title="Kisan Sahayak", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    .header { background: #1A1C23; padding: 20px; border-radius: 15px; border-bottom: 5px solid #4CAF50; text-align: center; margin-bottom: 20px; }
    .card { background: #1A1C23; padding: 20px; border-radius: 15px; border: 1px solid #4CAF50; text-align: center; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# Navigation
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
        v_in = speech_to_text(language='hi', key='mic')
    
    q = txt if txt else v_in
    if q or img:
        with st.spinner("Wait..."):
            p_img = Image.open(img) if img else None
            ans = get_ai_response(q if q else "Explain photo", p_img)
            st.success(ans)
            if st.button("🔊 Suniye"):
                aud = asyncio.run(speak(ans))
                if aud: st.audio(aud, format="audio/mp3", autoplay=True)

elif sel == "Weather":
    st.header("🌦️ Mausam")
    city, temp, desc = get_weather()
    st.metric(city, f"{temp} °C")
    st.write(f"Condition: {desc}")

elif sel == "Schemes":
    st.header("📜 Yojana")
    if st.button("PM Kisan Details"):
        st.write(get_ai_response("PM Kisan details in Hindi"))

elif sel == "Shop":
    st.header("🛒 Shop")
    p = st.text_input("Product Name:")
    if p: st.write(get_ai_response(f"{p} price and use in Hindi"))

elif sel == "About":
    st.markdown(f"""
    <div style='background: #1A1C23; padding: 40px; border-radius: 20px; border: 2px solid #4CAF50; text-align: center;'>
        <h1 style='color:#4CAF50;'>👨‍💻 Developer</h1>
        <hr>
        <h2>समीर (Sameer)</h2>
        <p>11th PCM Student | Dehradun</p>
        <p>📧 sameer2810092009@gmail.com</p>
        <p>📞 9897979032</p>
    </div>
    """, unsafe_allow_html=True)
