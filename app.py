import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

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

try:
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ API Key Missing")
        st.stop()
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🤖</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>HELP BRO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>Proje Mimarı v2.0</p>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📊 Mimari Araçlar")
    flow_btn = st.button("🗺️ Akış Şeması")
    folder_btn = st.button("📁 Klasör Yapısı")
    roadmap_btn = st.button("📅 Proje Planı")
    tech_btn = st.button("🛠️ Teknoloji")
    st.divider()
    st.caption("🎓 Üniversite Projesi")
    st.caption("© 2026 HELP BRO Team")

st.title("👨‍💻 Proje Planlama Merkezi")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba! Proje fikrini anlat، harika şeyler yapalım! 🚀"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Fikriniz nedir?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Hata: {e}")

def get_ai_extra(query):
    if len(st.session_state.messages) > 1:
        context = st.session_state.messages[-1]["content"]
        full_query = f"{query} \n Proje konusu: {context}"
        return model.generate_content(full_query).text
    return None

if flow_btn:
    res = get_ai_extra("Mermaid flowchart (graph TD) kodu yaz. Sadece kod.")
    if res:
        st.divider()
        clean_code = res.replace("```mermaid", "").replace("```", "").strip()
        st.code(clean_code, language="mermaid")
        encoded = urllib.parse.quote(clean_code)
        st.link_button("🖼️ Tam Ekran", f"https://mermaid.live/edit#base64:{{'code':'{encoded}'}}")

if folder_btn:
    res = get_ai_extra("Bu proje için klasör yapısını (folder tree) göster.")
    if res:
        st.info(f"### 📁 Klasör Yapısı\n\n{res}")

if roadmap_btn:
    res = get_ai_extra("Bu projeyi fazlara ayır (Phase 1, 2, 3).")
    if res:
        st.success(f"### 📅 Proje Planı\n\n{res}")

if tech_btn:
    res = get_ai_extra("Bu proje için en iyi dilleri ve kütüphaneleri öner.")
    if res:
        st.warning(f"### 🛠️ Teknoloji Önerisi\n\n{res}")
