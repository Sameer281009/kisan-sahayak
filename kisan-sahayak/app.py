import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_mic_recorder import speech_to_text
from streamlit_option_menu import option_menu
import asyncio
import edge_tts
import requests

# --- 1. CONFIGURATION ---
GEN_K = st.secrets.get("GENAI_KEY", "AIzaSyAgSqPVmLHwa0DkrFkiu3dZV_gbLMxAHGg")
W_K = st.secrets.get("WEATHER_KEY", "af1ec00f9fc32d17017dc84cdc7b7613")

genai.configure(api_key=GEN_K)

# Robust Model Loading Function
def get_ai_response(prompt, image=None):
    # Inme se jo bhi model milega, AI use utha lega
    models_to_test = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-pro']
    for m in models_to_test:
        try:
            model = genai.GenerativeModel(m)
            if image:
                res = model.generate_content([prompt, image])
            else:
                res = model.generate_content(prompt)
            return res.text
        except:
            continue
    return "Error: Model connect nahi ho raha. AI Studio mein Terms accept karein."

# Weather Function
@st.cache_data(ttl=3600)
def get_weather():
    try:
        r = requests.get('http://ip-api.com/json/', timeout=5).json()
        city = r.get('city', 'Dehradun')
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={W_K}&units=metric&lang=hi"
        res = requests.get(url).json()
        return city, res['main']['temp'], res['weather'][0]['description']
    except:
        return "Dehradun", "--", "Net Slow"

# Voice Function
async def speak(text):
    try:
        communicate = edge_tts.Communicate(text[:250], "hi-IN-MadhurNeural")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio": audio_data += chunk["data"]
        return audio_data
    except: return None

# --- 2. UI STYLING ---
st.set_page_config(page_title="Kisan Sahayak AI", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    .header-box { background: #1A1C23; padding: 20px; border-radius: 15px; border-bottom: 5px solid #4CAF50; text-align: center; margin-bottom: 20px; }
    .kisan-card { background: #1A1C23; padding: 20px; border-radius: 15px; border: 1px solid #2E7D32; text-align: center; min-height: 150px; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #1B5E20 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. TOP SECTION (Weather & Search) ---
st.markdown("<div class='header-box'><h1>🌾 किसान सहायक AI</h1></div>", unsafe_allow_html=True)

city, temp, desc = get_weather()
st.info(f"📍 {city} | 🌡️ {temp}°C | ☁️ {desc}")

c1, c2, c3 = st.columns([1, 2, 1])
with c1: img_file = st.camera_input("📸 फोटो")
with c2: txt_in = st.text_input("🔍 सवाल पूछें:", placeholder="यहाँ लिखें...")
with c3: 
    st.write("🎤 बोलकर पूछें")
    v_in = speech_to_text(language='hi', key='global_mic')

# AI Logic
final_q = txt_in if txt_in else v_in
if final_q or img_file:
    with st.spinner("AI जवाब तैयार कर रहा है..."):
        p_img = Image.open(img_file) if img_file else None
        ans = get_ai_response(final_q if final_q else "Is photo ko samjhayein", p_img)
        st.success(ans)
        if st.button("🔊 जवाब सुनें"):
            aud = asyncio.run(speak(ans))
            if aud: st.audio(aud, format="audio/mp3", autoplay=True)

# --- 4. NAVIGATION ---
selected = option_menu(
    menu_title=None, 
    options=["Home", "Sarkari Schemes", "Farming Shop", "Developer"], 
    icons=["house", "book", "cart", "person"], 
    orientation="horizontal",
    styles={"container": {"background-color": "#1A1C23"}}
)

# --- 5. PAGE CONTENT ---
if selected == "Home":
    st.write("### नमस्ते समीर! ऊपर दिए गए टूल्स का उपयोग करें।")
    st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1000&q=80", caption="उन्नत खेती, खुशहाल किसान")

elif selected == "Sarkari Schemes":
    st.subheader("📜 मुख्य सरकारी योजनाएं")
    sc1, sc2, sc3 = st.columns(3)
    schemes = [
        {"n": "PM Kisan", "d": "₹6000 सालाना सहायता"},
        {"n": "Fasal Bima", "d": "फसल नुकसान पर बीमा"},
        {"n": "Kusum Yojana", "d": "सोलर पंप सब्सिडी"}
    ]
    for i, s in enumerate(schemes):
        with [sc1, sc2, sc3][i]:
            st.markdown(f"<div class='kisan-card'><h3>{s['n']}</h3><p>{s['d']}</p></div>", unsafe_allow_html=True)
            if st.button(f"जानकारी: {s['n']}", key=f"s_{i}"):
                st.write(get_ai_response(f"{s['n']} yojana details in Hindi"))

elif selected == "Farming Shop":
    st.subheader("🛒 खेती की दुकान")
    sh1, sh2, sh3 = st.columns(3)
    products = [
        {"n": "Urea/DAP", "d": "खाद की जानकारी"},
        {"n": "कीटनाशक", "d": "दवाई की जानकारी"},
        {"n": "बीज", "d": "उन्नत किस्म के बीज"}
    ]
    for i, p in enumerate(products):
        with [sh1, sh2, sh3][i]:
            st.markdown(f"<div class='kisan-card'><h3>{p['n']}</h3><p>{p['d']}</p></div>", unsafe_allow_html=True)
            if st.button(f"विवरण: {p['n']}", key=f"p_{i}"):
                st.write(get_ai_response(f"{p['n']} farming use in Hindi"))

elif selected == "Developer":
    st.markdown(f"""
    <div style='background:#16191f; padding:30px; border-radius:20px; border:2px solid #4CAF50; text-align:center;'>
        <h1 style='color:#4CAF50;'>👨‍💻 Developer</h1>
        <h2>समीर (Sameer)</h2>
        <p>11th Class PCM Student | Dehradun</p>
        <p>📧 sameer2810092009@gmail.com | 📞 9897979032</p>
    </div>
    """, unsafe_allow_html=True)
