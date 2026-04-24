import streamlit as st
import google.generativeai as genai
import urllib.parse
import os
import time

st.set_page_config(page_title="HELP BRO", layout="wide")

# تصميم واجهة بسيط وسريع
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stButton>button { background: #238636; color: white; border-radius: 10px; width: 100%; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# دالة الاتصال الذكية مع خاصية الانتظار (Retry Logic)
def safe_generate(model_obj, prompt_text):
    for i in range(3): # سيحاول 3 مرات في حال الزحام
        try:
            return model_obj.generate_content(prompt_text).text
        except Exception as e:
            if "429" in str(e):
                time.sleep(2) # انتظر ثانيتين لو السيرفر مشغول
                continue
            return "Hata: Şu an bağlanılamıyor."
    return "Sunucu çok meşgul، lütfen az sonra deneyin."

# إعداد الموديل (استخدمنا gemini-1.5-flash لأنه الأكثر استقراراً حالياً)
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("API Key Eksik!")

# إدارة الذاكرة (Session State)
if "messages" not in st.session_state: st.session_state.messages = []

# القائمة الجانبية
with st.sidebar:
    st.title("🤖 HELP BRO")
    st.divider()
    flow = st.button("🗺️ Akış Şeması")
    folder = st.button("📁 Klasör Yapısı")
    tech = st.button("🛠️ Teknoloji")

# عرض المحادثة
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# إدخال المستخدم
if prompt := st.chat_input("Fikriniz nedir?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        res = safe_generate(model, prompt)
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})

# تشغيل الأزرار بناءً على آخر رسالة
if (flow or folder or tech) and st.session_state.messages:
    context = st.session_state.messages[-1]["content"]
    task = "Mermaid flowchart code" if flow else "Folder tree structure" if folder else "Tech stack"
    
    with st.chat_message("assistant"):
        with st.spinner("Hazırlanıyor..."):
            result = safe_generate(model, f"{task} for: {context}")
            st.markdown(f"### 📋 {task}")
            st.markdown(result)
