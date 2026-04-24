import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="HELP BRO | Project Architect",
    page_icon="🤖",
    layout="wide"
)

# تصميم مخصص لجعل الواجهة احترافية
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; padding: 15px; margin-bottom: 10px; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3.5em; 
        background-color: #FF4B4B; color: white; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #ff3333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد مفتاح API والموديل ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ مفتاح API مفقود في إعدادات Secrets.")
        st.stop()
        
    genai.configure(api_key=api_key)
    # استخدام الموديل الذي نجح في الفحص تماماً
    SELECTED_MODEL = 'models/gemini-2.5-flash'
    model = genai.GenerativeModel(SELECTED_MODEL)
except Exception as e:
    st.error(f"خطأ في الإعداد: {e}")
    st.stop()

# --- 3. الشريط الجانبي (Sidebar) ---
with st.sidebar:
    st.title("🛠️ لوحة التحكم")
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.info("ناقش مشروعك، ثم اضغط على الزر لرسم المخطط الهيكلي.")
    
    st.divider()
    # زر توليد المخطط
    generate_btn = st.button("✨ توليد مخطط المشروع (Flowchart)")
    
    st.divider()
    st.caption("🎓 مشروع جامعي متطور")
    st.caption("تم التطوير بواسطة: HELP BRO Team")

# --- 4. واجهة المحادثة الرئيسية ---
st.title("🤖 HELP BRO")
st.markdown("#### مساعدك الذكي لتحويل الأفكار البرمجية إلى مخططات هندسية")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "أهلاً بك! أنا مساعدك المهندس. كيف يمكنني مساعدتك في تخطيط مشروعك اليوم؟ 💡"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("اكتب فكرة مشروعك هنا..."):
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
                st.error(f"حدث خطأ في الرد: {e}")

# --- 5. منطق توليد المخطط (Mermaid) ---
if generate_btn:
    if len(st.session_state.messages) > 1:
        st.divider()
        with st.expander("📊 المخطط الهيكلي المقترح", expanded=True):
            with st.spinner("جاري رسم المخطط..."):
                try:
                    history = "\n".join([m["content"] for m in st.session_state.messages[-3:]])
                    diagram_prompt = f"قم بإنشاء كود Mermaid flowchart (graph TD) يمثل سير العمل لهذا المشروع. أعطني الكود فقط: {history}"
                    
                    result = model.generate_content(diagram_prompt)
                    clean_code = result.text.replace("```mermaid", "").replace("```", "").strip()
                    
                    st.code(clean_code, language="mermaid")
                    
                    encoded_code = urllib.parse.quote(clean_code)
                    mermaid_url = f"https://mermaid.live/edit#base64:{{'code':'{encoded_code}'}}"
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.link_button("🖼️ فتح المخطط في Mermaid Live", mermaid_url)
                    with col2:
                        st.download_button("📂 تحميل كود المخطط", data=clean_code, file_name="flowchart.txt")
                    
                    st.success("✅ تم توليد المخطط بنجاح!")
                except Exception as e:
                    st.error(f"فشل توليد المخطط: {e}")
    else:
        st.sidebar.warning("⚠️ ابدأ الدردشة أولاً!")
