



import streamlit as st
import google.generativeai as genai
import urllib.parse
import os
from dotenv import load_dotenv





for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)




# تحميل المتغيرات محلياً فقط
load_dotenv()

st.set_page_config(page_title="HELP BRO", page_icon="🤖", layout="wide")

# جلب المفتاح من Secrets (في ستريمليت) أو من بيئة النظام
MY_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not MY_API_KEY:
    st.error("⚠️ يرجى إضافة GEMINI_API_KEY في إعدادات Streamlit Secrets.")
    st.stop()

genai.configure(api_key=MY_API_KEY)

# تم تصحيح اسم الموديل هنا
model = genai.GenerativeModel('models/gemini-1.5-flash')

st.title("🤖 HELP BRO")
st.markdown("### مساعدك الذكي لتخطيط المشاريع البرمجية")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("اشرح لي فكرة مشروعك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            full_response = response.text
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"حدث خطأ في الرد: {e}")

# --- لوحة التحكم الجانبية ---
st.sidebar.title("🛠️ لوحة التحكم")
if st.sidebar.button("توليد مخطط المشروع 📊"):
    if len(st.session_state.messages) > 0:
        with st.spinner("جاري تحليل المحادثة..."):
            try:
                chat_history = str(st.session_state.messages[-3:])
                query = f"تحويل هذه الفكرة لمخطط Mermaid flowchart بسيط (graph TD). أعطني الكود فقط بدون شرح: {chat_history}"
                
                result = model.generate_content(query)
                clean_code = result.text.replace("```mermaid", "").replace("```", "").strip()
                
                st.divider()
                st.subheader("📊 المخطط الهيكلي المقترح")
                st.code(clean_code, language="mermaid")
                
                # تصحيح رابط Mermaid Live (تحتاج ترميز base64 ليكون الرابط أدق، لكن سنكتفي بالرابط النصي حالياً)
                encoded_code = urllib.parse.quote(clean_code)
                link = f"https://mermaid.live/edit#base64:{{'code':'{encoded_code}','mermaid':'{{}}','updateEditor':false}}"
                
                st.success("✅ تم توليد المخطط!")
                st.link_button("🖼️ افتح المخطط في Mermaid Live", link)
                
            except Exception as e:
                st.sidebar.error(f"فشل توليد المخطط: {e}")
    else:
        st.sidebar.warning("ابدأ الدردشة أولاً!")
