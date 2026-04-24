import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="HELP BRO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stButton>button { background: #238636; color: white; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key Missing!")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def get_model():
    # سيجرب الكود كل الصيغ الممكنة لاسم الموديل ليتخطى خطأ 404
    names_to_test = ["gemini-1.5-flash", "gemini-pro", "models/gemini-1.5-flash"]
    for name in names_to_test:
        try:
            m = genai.GenerativeModel(name)
            m.generate_content("hi", generation_config={"max_output_tokens": 1})
            return m
        except:
            continue
    return None

model = get_model()

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.title("🤖 HELP BRO")
    st.divider()
    btn_flow = st.button("🗺️ Akış Şeması")
    btn_tech = st.button("🛠️ Teknoloji")
    if st.button("🗑️ Temizle"):
        st.session_state.history = []
        st.rerun()

for role, text in st.session_state.history:
    with st.chat_message(role): st.markdown(text)

if prompt := st.chat_input("Fikriniz nedir?"):
    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            res = model.generate_content(prompt).text
            st.markdown(res)
            st.session_state.history.append(("assistant", res))
        except Exception as e:
            st.error("Sistem meşgul، lütfen 10 saniye bekleyin.")

if (btn_flow or btn_tech) and st.session_state.history:
    last_context = st.session_state.history[-1][1]
    q = "Mermaid flowchart code" if btn_flow else "Technology stack"
    with st.chat_message("assistant"):
        try:
            result = model.generate_content(f"{q} for: {last_context}").text
            st.info(result)
        except:
            st.warning("Hata! Lütfen biraz bekleyip tekrar basın.")
