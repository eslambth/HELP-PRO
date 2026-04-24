import streamlit as st
import google.generativeai as genai
import urllib.parse
import os
import time

# --- 1. AYARLAR VE TASARIM ---
st.set_page_config(
    page_title="HELP BRO | AI Architect",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #30363d;
        background-color: #161b22 !important;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background: linear-gradient(45deg, #238636, #2ea043);
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 15px rgba(46, 160, 67, 0.4);
    }
    [data-testid="stSidebar"] {
        background-color: #010409;
        border-right: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AKILLI MODEL YÖNETİMİ (FALLBACK LOGIC) ---
def get_working_model():
    # قائمة الموديلات مرتبة من الأحدث إلى الأكثر استقراراً
    models_to_try = [
        'models/gemini-2.0-flash',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro',
        'models/gemini-pro'
    ]
    
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ API Key Missing!")
        return None

    genai.configure(api_key=api_key)

    for model_name in models_to_try:
        try:
            m = genai.GenerativeModel(model_name)
            # تجربة بسيطة للتأكد من أن الموديل يعمل ولا يوجد ضغط (Quota)
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m
        except Exception:
            continue # إذا فشل ينتقل للموديل التالي تلقائياً
    return None

# تهيئة الموديل
model = get_working_model()

# --- 3. YAN PANEL ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🤖</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>HELP BRO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>AI Proje Mimarı v3.0</p>", unsafe_allow_html=True)
    st.divider()
    
    st.markdown("### 📊 Mimari Araçlar")
    flow_btn = st.button("🗺️ Akış Şeması")
    folder_btn = st.button("📁 Klasör Yapısı")
    roadmap_btn = st.button("📅 Proje Planı")
    tech_btn = st.button("🛠️ Teknoloji")
    
    st.divider()
    if model:
        st.success(f"⚡ Aktif Model: {model.model_name.split('/')[-1]}")
    else:
        st.error("⚠️ Bağlantı Hatası!")

# --- 4. ANA EKRAN ---
st.title("👨‍💻 Proje Planlama Merkezi")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba! Ben senin yapay zeka mimarınım. Proje fikrini anlat, her şeyi planlayalım! 🚀"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Fikriniz nedir?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if model:
            with st.spinner("Düşünüyor..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error("Şu an çok yoğunum, lütfen 10 saniye sonra tekrar dene.")
        else:
            st.error("Sistem şu an başlatılamadı. Lütfen API anahtarını kontrol et.")

# --- 5. ARAÇ FONKSİYONLARI ---
def safe_generate(query):
    if model and len(st.session_state.messages) > 1:
        context = st.session_state.messages[-1]["content"]
        try:
            res = model.generate_content(f"{query} \n Bağlam: {context}")
            return res.text
        except:
            return "Şu an bu işlemi yapamıyorum, lütfen biraz bekleyin."
    return None

if flow_btn:
    res = safe_generate("Mermaid flowchart (graph TD) kodu yaz. Sadece kod ver.")
    if res:
        st.divider()
        clean_code = res.replace("```mermaid", "").replace("```", "").strip()
        st.code(clean_code, language="mermaid")
        encoded = urllib.parse.quote(clean_code)
        st.link_button("🖼️ Şemayı Aç", f"https://mermaid.live/edit#base64:{{'code':'{encoded}'}}")

if folder_btn:
    res = safe_generate("Bu proje için klasör yapısını (tree structure) göster.")
    if res: st.info(f"### 📁 Klasör Yapısı\n\n{res}")

if roadmap_btn:
    res = safe_generate("Bu projeyi fazlara ayır (Phase 1, 2, 3).")
    if res: st.success(f"### 📅 Proje Planı\n\n{res}")

if tech_btn:
    res = safe_generate("Bu proje için en iyi dilleri ve kütüphaneleri öner.")
    if res: st.warning(f"### 🛠️ Teknoloji Önerisi\n\n{res}")
