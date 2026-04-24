import streamlit as st
import google.generativeai as genai
import urllib.parse

import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env (أثناء التطوير المحلي)
load_dotenv()

# --- 1. إعدادات الصفحة والذكاء الاصطناعي ---
st.set_page_config(page_title="HELP BRO", page_icon="🤖", layout="wide")

# جلب المفتاح بأمان من متغيرات البيئة (أو st.secrets الخاص بـ Streamlit)
MY_API_KEY = os.environ.get("GEMINI_API_KEY")

if not MY_API_KEY:
    try:
        MY_API_KEY = st.secrets["AIzaSyBSJnT-d-auUqkMMXN8sxuRDEoaWS5UinY"]
    except:
        st.error("⚠️ يرجى إعداد مفتاح API الخاص بـ Gemini في متغيرات البيئة.")
        st.stop()

genai.configure(api_key=MY_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. واجهة المستخدم ---
st.title("🤖 HELP BRO")
st.markdown("### مساعدك الذكي لتخطيط المشاريع البرمجية")

# تهيئة ذاكرة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. منطق الدردشة ---
if prompt := st.chat_input("اشرح لي فكرة مشروعك هنا..."):
    # إضافة رسالة المستخدم للذاكرة والعرض
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد رد البوت
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            full_response = response.text
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"حدث خطأ في الرد: {e}")

# --- 4. لوحة التحكم الجانبية والمخططات ---
st.sidebar.title("🛠️ لوحة التحكم")
st.sidebar.info("بعد مناقشة الفكرة مع البوت، اضغط على الزر بالأسفل لرسم مخطط المشروع.")

if st.sidebar.button("توليد مخطط المشروع 📊"):
    if len(st.session_state.messages) > 0:
        with st.spinner("جاري تحليل المحادثة وبناء المخطط..."):
            try:
                # طلب كود Mermaid مختصر جداً
                chat_history = str(st.session_state.messages[-3:]) # نأخذ آخر 3 رسائل فقط للاختصار
                query = f"تحويل هذه الفكرة لمخطط Mermaid flowchart بسيط (graph TD). أعطني الكود فقط بدون شرح: {chat_history}"
                
                result = model.generate_content(query)
                clean_code = result.text.replace("```mermaid", "").replace("```", "").strip()
                
                # عرض الكود للمستخدم كمرجع
                st.divider()
                st.subheader("📊 المخطط الهيكلي المقترح")
                st.code(clean_code, language="mermaid")
                
                # إنشاء رابط فتح المخطط في Mermaid Live لتجنب مشاكل التحميل
                encoded_code = urllib.parse.quote(clean_code)
                link = f"https://mermaid.live/edit#base64:{encoded_code}"
                
                st.success("✅ تم توليد المخطط!")
                st.link_button("🖼️ اضغط هنا لمشاهدة المخطط بوضوح وتعديله", link)
                
            except Exception as e:
                st.sidebar.error(f"فشل توليد المخطط: {e}")
    else:
        st.sidebar.warning("يجب أن تبدأ الدردشة أولاً وتطرح فكرة!")

# --- 5. تذييل الصفحة ---
st.sidebar.divider()
st.sidebar.caption("صُنع بكل حماس لمساعدتك في رحلتك البرمجية 🚀")
