import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Model Debugger Pro", page_icon="🔍")

st.title("🔍 فاحص الموديلات المتطور")
st.write("سيقوم هذا الكود بتحديد الموديل الشغال بدقة لتجنب خطأ 404.")

# جلب المفتاح
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ مفتاح API غير موجود في الإعدادات!")
    st.stop()

try:
    genai.configure(api_key=api_key)
    
    st.info("🔄 جاري سحب القائمة واختبار الاستجابة...")
    
    # 1. جلب كل الموديلات المتاحة في حسابك
    available_models = genai.list_models()
    
    success_list = []
    fail_list = []

    for m in available_models:
        if 'generateContent' in m.supported_generation_methods:
            # 2. تجربة الموديل فعلياً بطلب صغير جداً
            try:
                test_model = genai.GenerativeModel(m.name)
                # نرسل طلب بسيط جداً للتأكد من الـ Quota والـ Support
                test_model.generate_content("hi", generation_config={"max_output_tokens": 1})
                success_list.append(m.name)
            except Exception as e:
                fail_list.append(f"{m.name} (Error: {str(e)[:50]}...)")

    # 3. عرض النتائج
    st.divider()
    
    if success_list:
        st.success(f"✅ تم العثور على {len(success_list)} موديلات تعمل بنجاح:")
        for model_name in success_list:
            st.code(model_name)
            st.write("---")
        st.balloons()
    else:
        st.error("❌ لا يوجد أي موديل يستجيب حالياً. قد يكون السبب Quota Exceeded أو مفتاح ملغي.")

    if fail_list:
        with st.expander("⚠️ موديلات موجودة ولكنها تعطي خطأ (اضغط للتفاصيل)"):
            for f in fail_list:
                st.warning(f)

except Exception as e:
    st.error(f"💥 خطأ كارثي في الاتصال: {e}")

st.markdown("""
### ماذا تفعل الآن؟
1. الموديل الذي يظهر في القائمة **الخضراء** هو الذي يجب أن تضعه في كود البوت.
2. إذا كانت القائمة الخضراء فارغة، فهذا يعني أن المشكلة في **الـ API Key** نفسه (ربما محظور أو منتهي).
""")
