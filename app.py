import streamlit as st
import google.generativeai as genai
import os
import time

st.set_page_config(page_title="HELP BRO", layout="wide")

# إعداد الـ API بطريقة تمنع الأخطاء القديمة
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Key missing!")
    st.stop()

genai.configure(api_key=api_key)

# اختيار الموديل الأكثر استقراراً للنسخة المجانية
model = genai.GenerativeModel('gemini-1.5-flash')

# الحالة الذاكرية للتطبيق
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# التصميم الجانبي
with st.sidebar:
    st.title("🤖 HELP BRO")
    st.divider()
    btn_flow = st.button("🗺️ Akış Şeması")
    btn_tech = st.button("🛠️ Teknoloji")
    if st.button("🗑️ Sohbeti Temizle"):
        st.session_state.chat_history = []
        st.rerun()

# عرض الرسائل
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(text)

# دالة ذكية للإرسال تمنع التعليق
def ask_ai(query):
    try:
        response = model.generate_content(query)
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ Suncucu meşgul (Quota Full). Lütfen 30 saniye bekleyin."
        return f"⚠️ Hata oluştu: {str(e)[:50]}"

# المحادثة الأساسية
if prompt := st.chat_input("Fikriniz nedir?"):
    st.session_state.chat_history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        answer = ask_ai(prompt)
        st.markdown(answer)
        st.session_state.chat_history.append(("assistant", answer))

# تشغيل الأزرار
if (btn_flow or btn_tech) and st.session_state.chat_history:
    last_msg = st.session_state.chat_history[-1][1]
    query_type = "Mermaid flowchart code" if btn_flow else "Best technology stack"
    
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            extra_res = ask_ai(f"{query_type} for this: {last_msg}")
            st.info(f"### 📊 {query_type}")
            st.markdown(extra_res)
