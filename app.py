import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="HELP BRO", layout="wide")

# تصميم الواجهة (CSS بسيط لضمان السرعة)
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stButton>button { background: #238636; color: white; border-radius: 10px; width: 100%; }
    [data-testid="stSidebar"] { background-color: #010409; }
    </style>
    """, unsafe_allow_html=True)

# الاتصال بالـ API
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # استخدام gemini-pro مباشرة لتجنب خطأ 404
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        st.error(f"API Configuration Error: {e}")
else:
    st.error("API Key Missing!")

# اللوحة الجانبية
with st.sidebar:
    st.title("🤖 HELP BRO")
    st.info("Proje Planlama Merkezi v3.1")
    st.divider()
    # ميزات المشروع
    flow_btn = st.button("🗺️ Akış Şeması")
    folder_btn = st.button("📁 Klasör Yapısı")
    tech_btn = st.button("🛠️ Teknoloji")

# منطقة الدردشة
st.title("👨‍💻 Proje Mimarı")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Fikriniz nedir?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Model Error: {e}. Lütfen biraz bekleyip tekrar deneyin.")

# تنفيذ الميزات الإضافية
if (flow_btn or folder_btn or tech_btn) and len(st.session_state.messages) > 0:
    context = st.session_state.messages[-1]["content"]
    queries = {
        "flow": "Bu proje için Mermaid flowchart kodu yaz. Sadece kod.",
        "folder": "Bu proje için klasör yapısını göster.",
        "tech": "Bu proje için teknoloji önerileri yap."
    }
    q = queries["flow"] if flow_btn else queries["folder"] if folder_btn else queries["tech"]
    
    with st.expander("📊 Sonuç", expanded=True):
        try:
            res = model.generate_content(f"{q} \n Bağlam: {context}")
            st.markdown(res.text)
        except:
            st.error("İşlem başarısız. Lütfen bekleyin.")
