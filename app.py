import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

# --- 1. إعدادات الصفحة والذكاء الاصطناعي ---
st.set_page_config(page_title="HELP BRO", page_icon="🤖", layout="wide")

# جلب المفتاح بأمان من Secrets الخاص بـ Streamlit
try:
    MY_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=MY_API_KEY)
except Exception as e:
    st.error("⚠️ خطأ في العثور على المفتاح. تأكد من إضافته في Streamlit Cloud Secrets.")
    st.stop()

# استخدمنا الموديل الذي ظهر لك في الفحص
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
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # استخدام الموديل الجديد
            response = model.generate_content(prompt)
            full_response = response.text
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"حدث خطأ في الرد: {e}")

# --- 4. لوحة التحكم الجانبية والمخططات ---
st.sidebar.title("🛠️ لوحة التحكم")
if st.sidebar.button("توليد مخطط المشروع 📊"):
    if len(st.session_state.messages) > 0:
        with st.spinner("جاري تحليل المحادثة وبناء المخطط..."):
            try:
                # نأخذ سياق المحادثة لتحويله لمخطط
                chat_history = " ".join([m["content"] for m in st.session_state.messages[-3:]])
                query = f"قم بتحويل هذه الفكرة لمخطط Mermaid flowchart بسيط (graph TD). أعطني كود المخطط فقط بدون أي شرح أو مقدمات: {chat_history}"
                
                result = model.generate_content(query)
                clean_code = result.text.replace("```mermaid", "").replace("```", "").strip()
                
                st.divider()
                st.subheader("📊 المخطط الهيكلي المقترح")
                st.code(clean_code, language="mermaid")
                
                # رابط Mermaid Live للمشاهدة بوضوح
                encoded_code = urllib.parse.quote(clean_code)
                link = f"https://mermaid.live/edit#base64:{{'code':'{encoded_code}'}}"
                
                st.success("✅ تم توليد المخطط!")
                st.link_button("🖼️ اضغط هنا لمشاهدة المخطط وتعديله", link)
                
            except Exception as e:
                st.sidebar.error(f"فشل توليد المخطط: {e}")
    else:
        st.sidebar.warning("يجب أن تبدأ الدردشة أولاً!")

# --- 5. تذييل الصفحة ---
st.sidebar.divider()
st.sidebar.caption("صُنع بكل حماس لمساعدتك 🚀")
