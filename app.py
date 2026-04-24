import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Gemini Diagnostic Tool", page_icon="🔍")

st.title("🔍 فاحص الموديلات المتقدم")

# جلب المفتاح
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ المفتاح غير موجود في Secrets")
    st.stop()

try:
    genai.configure(api_key=api_key)
    
    # جلب القائمة
    models = genai.list_models()
    available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
    
    if available_models:
        st.success(f"✅ تم العثور على {len(available_models)} موديل مدعوم")
        
        # اختيار الموديل من القائمة للتجربة
        selected_model = st.selectbox("اختر الموديل الذي تريد اختباره:", available_models)
        
        test_prompt = st.text_input("اكتب رسالة تجريبية:", "Hello, are you working?")
        
        if st.button("إرسال تجربة"):
            try:
                # محاولة التشغيل بالاسم المختار مباشرة
                model_test = genai.GenerativeModel(selected_model)
                response = model_test.generate_content(test_prompt)
                st.write("---")
                st.markdown(f"**رد الموديل:** {response.text}")
                st.balloons()
            except Exception as e:
                st.error(f"❌ فشل الموديل {selected_model}: {e}")
                
        st.divider()
        st.write("أسماء الموديلات الكاملة المسجلة في حسابك:")
        for name in available_models:
            st.code(name)
            
    else:
        st.warning("لم يتم العثور على أي موديلات تدعم generateContent")

except Exception as e:
    st.error(f"حدث خطأ أثناء الاتصال بـ API: {e}")
