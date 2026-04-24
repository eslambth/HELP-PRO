import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Model Scanner", page_icon="🔍")

st.title("🔍 Gemini Model Scanner")

api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Key missing in Secrets!")
    st.stop()

try:
    genai.configure(api_key=api_key)
    
    st.write("جاري البحث عن الموديلات المتاحة لمفتاحك...")
    
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
    
    if available_models:
        st.success(f"تم العثور على {len(available_models)} موديل مدعوم:")
        
        for name in available_models:
            st.code(name)
            
        st.divider()
        
        selected = st.selectbox("اختبر موديل الآن:", available_models)
        test_text = st.text_input("رسالة تجريبية:", "Merhaba")
        
        if st.button("تشغيل الاختبار"):
            try:
                test_model = genai.GenerativeModel(selected)
                response = test_model.generate_content(test_text)
                st.write("✅ الموديل يعمل! الرد:")
                st.success(response.text)
            except Exception as e:
                st.error(f"❌ فشل الموديل {selected}: {e}")
    else:
        st.warning("لم يتم العثور على موديلات تدعم توليد المحتوى.")

except Exception as e:
    st.error(f"خطأ في الاتصال بالـ API: {e}")
