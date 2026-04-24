import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

# --- 1. إعدادات الصفحة والتصميم الظاهري ---
st.set_page_config(
    page_title="HELP BRO | AI Architect",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إضافة CSS مخصص لتحسين شكل المحادثة
st.markdown("""
    <style>
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد مفتاح API ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ مفتاح API غير موجود. يرجى إعداده في الـ Secrets باسم GEMINI_API_KEY")
        st.stop()
        
    genai.configure(api_key=api_key)
    # استخدام الموديل الأكثر استقراراً
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"حدث خطأ في الإعداد: {e}")
    st.stop()

# --- 3. الشريط الجانبي (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
    st.title("🛠️ مهندس المشاريع")
    st.info("هذا البوت يساعدك على تحويل أفكارك البرمجية إلى مخططات هندسية واضحة.")
    
    st.divider()
    
    if st.button("✨ توليد مخطط المشرع (Flowchart)"):
        if "messages" in st.session_state and len(st.session_state.messages) > 1:
            st.session_state.generate_diagram = True
        else:
            st.warning("يرجى مناقشة فكرة المشروع مع البوت أولاً!")
            
    st.divider()
    st.caption("🎓 مشروع جامعي مطور بواسطة HELP BRO Team")

# --- 4. واجهة المحادثة الرئيسية ---
st.title("🤖 HELP BRO")
st.subheader("مساعدك الذكي في هندسة البرمجيات")

# تهيئة الذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "أهلاً بك! أنا مساعدك المهندس. اشرح لي فكرة مشروعك وسأساعدك في تخطيطها ورسم مخطط التدفق لها. 💡"}
    ]

# عرض الرسائل
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# إدخال المستخدم
if prompt := st.chat_input("بماذا يمكنني أن أساعدك اليوم؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("جاري التفكير..."):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"خطأ في الاتصال: {e}")

# --- 5. منطق توليد المخطط (يظهر تحت المحادثة عند الطلب) ---
if st.session_state.get("generate_diagram", False):
    with st.expander("📊 مخطط التدفق المقترح (Mermaid Chart)", expanded=True):
        with st.spinner("جاري رسم المخطط..."):
            try:
                history = "\n".join([m["content"] for m in st.session_state.messages[-3:]])
                diagram_prompt = f"قم بإنشاء كود Mermaid flowchart (graph TD) يمثل سير العمل في هذا المشروع. أعطني الكود فقط: {history}"
                
                result = model.generate_content(diagram_prompt)
                code = result.text.replace("```mermaid", "").replace("```", "").strip()
                
                st.code(code, language="mermaid")
                
                # رابط Mermaid Live
                encoded_code = urllib.parse.quote(code)
                url = f"https://mermaid.live/edit#base64:{{'code':'{encoded_code}'}}"
                
                st.link_button("🖼️ فتح المخطط في نافذة كاملة", url)
                
                # ميزة إضافية: تحميل الكود كملف
                st.download_button("📂 تحميل كود المخطط", data=code, file_name="diagram.txt")
                
                st.session_state.generate_diagram = False
            except Exception as e:
                st.error(f"تعذر توليد المخطط: {e}")
