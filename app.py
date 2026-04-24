import streamlit as st
import google.generativeai as genai
import os

# --- إعداد المفتاح ---
# تأكد أنك وضعت المفتاح في Secrets بـ Streamlit باسم GEMINI_API_KEY
MY_API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

st.title("🔍 فاحص موديلات Gemini")

if not MY_API_KEY:
    st.error("❌ مفتاح API غير مفقود! تأكد من إعداده في الـ Secrets.")
else:
    try:
        genai.configure(api_key=MY_API_KEY)
        
        st.write("جاري البحث عن الموديلات المتاحة لمفتاحك...")
        
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if available_models:
            st.success(f"✅ تم العثور على {len(available_models)} موديل مدعوم:")
            # عرض الموديلات في قائمة
            for model_name in available_models:
                st.code(model_name)
            
            st.info("💡 انسخ أحد الأسماء أعلاه وضعه في كود المشروع (غالباً سيكون models/gemini-1.5-flash)")
        else:
            st.warning("⚠️ المفتاح يعمل ولكن لا توجد موديلات متاحة لهذا الحساب.")
            
    except Exception as e:
        st.error(f"❌ فشل الاتصال بـ API: {e}")
