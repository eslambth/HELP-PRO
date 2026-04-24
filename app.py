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
    [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_ai():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key: return None
    genai.configure(api_key=api_key)
    for m_name in ['models/gemini-2.5-flash', 'models/gemini-pro']:
        try:
            m = genai.GenerativeModel(m_name)
            m.generate_content("hi", generation_config={"max_output_tokens": 1})
            return m
        except: continue
    return None

model = load_ai()

if "tool_result" not in st.session_state: st.session_state.tool_result = None
if "messages" not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🤖</h1><h2 style='text-align: center;'>HELP BRO</h2>", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📊 Mimari Araçlar")
    
    if st.button("🗺️ Akış Şeması"):
        st.session_state.tool_type = "flow"
    if st.button("📁 Klasör Yapısı"):
        st.session_state.tool_type = "folder"
    if st.button("📅 Proje Planı"):
        st.session_state.tool_type = "roadmap"
    if st.button("🛠️ Teknoloji"):
        st.session_state.tool_type = "tech"
    
    st.divider()
    if model: st.success(f"✅ {model.model_name.split('/')[-1]}")

st.title("👨‍💻 Proje Mimarı")

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
        except: st.error("Lütfen biraz bekleyin.")

if "tool_type" in st.session_state and len(st.session_state.messages) > 0:
    with st.status("İşlem yapılıyor...", expanded=True):
        ctx = st.session_state.messages[-1]["content"]
        prompts = {
            "flow": "Mermaid.js flowchart code only for this project.",
            "folder": "Folder tree structure for this project.",
            "roadmap": "Project phases (1, 2, 3) roadmap.",
            "tech": "Recommended tech stack (Language, DB)."
        }
        try:
            final_res = model.generate_content(f"{prompts[st.session_state.tool_type]} \n Context: {ctx}").text
            st.markdown(f"### 📋 Sonuç")
            if st.session_state.tool_type == "flow":
                clean = final_res.replace("```mermaid", "").replace("```", "").strip()
                st.code(clean, language="mermaid")
            else:
                st.markdown(final_res)
            del st.session_state.tool_type
        except: st.error("Hata oluştu، tekrar deneyin.")
