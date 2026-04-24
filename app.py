import streamlit as st
import google.generativeai as genai
import os
import time

st.set_page_config(page_title="HELP BRO | Proje Mimarı", layout="wide")

# إعداد الـ API
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key Eksik!")
    st.stop()

# دالة لاختيار الموديل بناءً على ما نجح في صور الفحص السابقة
@st.cache_resource
def load_working_model():
    # ترتيب الموديلات التي ظهرت باللون الأخضر في لقطة شاشتك
    test_list = ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-pro"]
    for name in test_list:
        try:
            m = genai.GenerativeModel(name)
            # تجربة صامتة
            m.generate_content("hi", generation_config={"max_output_tokens": 1})
            return m
        except:
            continue
    return None

model = load_working_model()

if "history" not in st.session_state:
    st.session_state.history = []

# اللوحة الجانبية
with st.sidebar:
    st.title("🤖 HELP BRO")
    st.divider()
    btn_flow = st.button("🗺️ Akış Şeması")
    btn_tech = st.button("🛠️ Teknoloji")
    if st.button("🗑️ Sohbeti Temizle"):
        st.session_state.history = []
        st.rerun()

# عرض الشات
for role, text in st.session_state.history:
    with st.chat_message(role): st.markdown(text)

# منطق الإرسال مع معالجة خطأ الزحام (Quota)
if prompt := st.chat_input("Fikriniz nedir?"):
    st.session_state.history.append(("user", prompt))
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # محاولة الإرسال
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.history.append(("assistant", response.text))
        except Exception as e:
            if "429" in str(e):
                st.warning("⚠️ Google kotası doldu. Lütfen 1 dakika bekleyip sayfayı yenileyin.")
            else:
                st.error(f"⚠️ Bağlantı hatası: {str(e)[:100]}")

# تشغيل الأزرار
if (btn_flow or btn_tech) and st.session_state.history:
    context = st.session_state.history[-1][1]
    task = "Mermaid.js flowchart code" if btn_flow else "Tech stack recommendations"
    with st.chat_message("assistant"):
        with st.spinner("İşleniyor..."):
            try:
                res = model.generate_content(f"{task} for this: {context}")
                st.info(res.text)
            except:
                st.error("Şu an yanıt alınamıyor، lütfen az sonra tekrar basın.")
