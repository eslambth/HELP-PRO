import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

st.set_page_config(page_title="HELP BRO", layout="wide")

try:
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    # جرب استخدام gemini-pro فهو الأضمن للعمل مع المفاتيح الجديدة
    model = genai.GenerativeModel('gemini-pro') 
except Exception as e:
    st.error(f"API Error: {e}")

st.title("👨‍💻 Proje Planlama Merkezi")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if p := st.chat_input("Fikriniz nedir?"):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    with st.chat_message("assistant"):
        try:
            r = model.generate_content(p)
            st.markdown(r.text)
            st.session_state.messages.append({"role": "assistant", "content": r.text})
        except Exception as e:
            st.error(f"Model Error: {e}")
