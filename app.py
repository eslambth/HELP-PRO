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

# تصميم مخصص (CSS) لجعل الواجهة تبدو احترافية
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; padding: 15px; margin-bottom: 10px; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3em; 
        background-color: #FF4B4B; color: white; border: none;
    }
    .stButton>button:hover { background-color: #ff3333; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد مفتاح API ---
try:
    # جلب المفتاح من Secrets (في ستريمليت كلاود) أو البيئة المحلية
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ مفتاح API مفقود. يرجى إضافته في إعدادات Secrets باسم GEMINI_API_KEY")
        st.stop()
        
    genai.configure(api_key=api_key)
    # استخدام المسار الكامل للموديل لتجنب خطأ 404
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"خطأ في الإعداد: {e}")
    st.stop()

# --- 3. الشريط الجانبي (Sidebar) ---
with st.sidebar:
    st.title("🛠️ لوحة التحكم")
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
    st.info("قم بمناقشة مشروعك مع البوت، وعند الانتهاء اضغط على الزر أدناه لتوليد المخطط الهيكلي.")
    
    st.divider()
    
    # زر توليد المخطط
    generate_btn = st.button("✨ توليد مخطط المشروع (Flowchart)")
    
    st.divider()
    st.caption("🎓 مشروع جامعي: مساعد تخطيط المشاريع الذكي")
    st.caption("تم التطوير بواسطة: HELP BRO Team")

# --- 4. واجهة المحادثة الرئيسية ---
st.title("🤖 HELP BRO")
st.markdown("#### مساعدك الذكي لتحويل الأفكار إلى مخططات برمجية")

# تهيئة الذاكرة في المتصفح
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "أهلاً بك! أنا مساعدك المهندس. اشرح لي فكرة مشروعك وسأساعدك في تخطيطها ورسم مخطط التدفق (Flowchart) لها. 💡"}
    ]

# عرض رسائل الدردشة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# منطقة إدخال المستخدم
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

# --- 5. منطق توليد المخطط عند الضغط على الزر ---
if generate_btn:
    if len(st.session_state.messages) > 1:
        st.divider()
        with st.expander("📊 المخطط الهيكلي المقترح (Mermaid)", expanded=True):
            with st.spinner("جاري تحليل المحادثة ورسم المخطط..."):
                try:
                    # استخلاص سياق المحادثة
                    context = "\n".join([m["content"] for m in st.session_state.messages[-4:]])
                    diagram_prompt = f"قم بإنشاء كود Mermaid flowchart (graph TD) يمثل سير العمل التقني لهذا المشروع بناءً على المحادثة. أعطني الكود فقط بدون أي شرح: {context}"
                    
                    # استخدام المسار الكامل للموديل لضمان العمل
                    result = model.generate_content(diagram_prompt)
                    clean_code = result.text.replace("```mermaid", "").replace("```", "").strip()
                    
                    # عرض الكود البرمجي للمخطط
                    st.subheader("كود المخطط (Mermaid)")
                    st.code(clean_code, language="mermaid")
                    
                    # إنشاء روابط التصدير
                    encoded_code = urllib.parse.quote(clean_code)
                    mermaid_url = f"https://mermaid.live/edit#base64:{{'code':'{encoded_code}'}}"
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.link_button("🖼️ عرض المخطط بوضوح (Mermaid Live)", mermaid_url)
                    with col2:
                        st.download_button("📂 تحميل المخطط كملف نصي", data=clean_code, file_name="project_structure.txt")
                        
                    st.success("✅ تم توليد المخطط بنجاح!")
                    
                except Exception as e:
                    st.error(f"تعذر رسم المخطط: {e}")
    else:
        st.sidebar.warning("⚠️ يرجى البدء بالدردشة أولاً!")

# --- 6. تذييل الصفحة ---
st.markdown("---")
st.caption("ملاحظة: هذا البوت يستخدم نموذج Gemini 1.5 Flash لتحليل البيانات.")
