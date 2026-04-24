import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

st.set_page_config(page_title="HELP BRO | AI Architect", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stChatMessage { border-radius: 15px; padding: 15px; margin-bottom: 15px; border: 1px solid #30363d; background-color: #161b22 !important; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #238636, #2ea043); color: white; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 4px 15px rgba(46, 160, 67, 0.4); }
    [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_ai():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key: return None
    genai.configure(api_key=api_key)
    
    working_models = ['models/gemini-2.5-flash', 'models/gemma-3-12b-it', 'models/gemini-pro']
    
    for m_name in working_models:
        try:
            m = genai.GenerativeModel(m_name)
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m
        except:
            continue
    return None

model = load_ai()

with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🤖</h1><h2 style='text-align: center;'>HELP BRO</h2>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📊 Mimari Araçlar")
    flow_btn = st.button("🗺️ Akış Şeması")
    folder_btn = st.button("📁 Klasör Yapısı")
    roadmap_btn = st.button("📅 Proje Planı")
    tech_btn = st.button("🛠️ Teknoloji")
    st.divider()
    if model:
        st.success(f"✅ Aktif: {model.model_name.split('/')[-1]}")
    else:
        st.error("❌ API Bağlantı Hatası")

st.title("👨‍💻 Proje Mimarı")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Merhaba! Harika bir proje tasarlamaya hazır ميسين؟ 🚀"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Fikriniz nedir?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            res = model.generate_content(prompt)
            st.markdown(res.text)
            st.session_state.messages.append({"role": "assistant", "content": res.text})
        except:
            st.error("Şu an yoğunluk var، lütfen saniyeler sonra tekrar deneyin.")

def run_tool(query):
    if model and len(st.session_state.messages) > 1:
        last_context = st.session_state.messages[-1]["content"]
        try:
            return model.generate_content(f"{query} \n Bağlam: {last_context}").text
        except: return None
    return None

if flow_btn:
    result = run_tool("Bu proje için Mermaid.js formatında akış şeması kodu yaz. Sadece kod.")
    if result:
        st.divider()
        clean = result.replace("```mermaid", "").replace("```", "").strip()
        st.code(clean, language="mermaid")
        st.link_button("🖼️ Şemayı Gör", f"https://mermaid.live/edit#base64:{urllib.parse.quote(clean)}")

if folder_btn:
    result = run_tool("Bu proje için profesyonel klasör yapısını ağaç şeklinde göster.")
    if result: st.info(f"### 📁 Klasör Yapısı\n\n{result}")

if roadmap_btn:
    result = run_tool("Bu projeyi aşamalara (Phase 1, 2, 3) ayır.")
    if result: st.success(f"### 📅 Geliştirme Planı\n\n{result}")

if tech_btn:
    result = run_tool("Bu proje için dil, framework ve veritabanı öner.")
    if result: st.warning(f"### 🛠️ Teknoloji Önerisi\n\n{result}")
