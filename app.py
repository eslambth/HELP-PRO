import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

# --- 1. SAYFA AYARLARI VE MODERN TASARIM ---
st.set_page_config(
    page_title="HELP BRO | Proje Mimarı",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS: Modern ve şık bir arayüz için
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stChatMessage {
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #30363d;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background: linear-gradient(45deg, #FF4B4B, #FF8F8F);
        color: white;
        font-weight: 600;
        border: none;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4);
    }

    .sidebar .sidebar-content {
        background-color: #0e1117;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API YAPILANDIRMASI ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ API Anahtarı bulunamadı! Lütfen Secrets kısmına ekleyin.")
        st.stop()
        
    genai.configure(api_key=api_key)
    # Çalıştığından emin olduğumuz model adını buraya yazın (Örn: 'gemini-1.5-flash')
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")
    st.stop()

# --- 3. YAN PANEL (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
    st.title("🛠️ Kontrol Paneli")
    st.markdown("---")
    st.info("💡 **Nasıl Çalışır?**\nProjenizi bot ile tartışın, fikirler olgunlaştığında aşağıdaki butona basarak akış şemasını oluşturun.")
    
    st.markdown("### 📊 Görselleştirme")
    generate_btn = st.button("✨ Akış Şeması Oluştur (Flowchart)")
    
    st.markdown("---")
    st.caption("🎓 **Üniversite Projesi**")
    st.caption("Geliştirici: **HELP BRO Team**")

# --- 4. ANA SOHBET EKRANI ---
st.title("🤖 HELP BRO")
st.markdown("#### Yazılım Projeleriniz İçin Akıllı Planlama Asistanı")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba! Ben senin yazılım mimarı asistanınım. Proje fikrini anlat, planlamana ve akış şemasını çizmemize yardımcı olayım. 🚀"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Proje fikrinizi buraya yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")

# --- 5. FLOWCHART ÜRETME MANTIĞI ---
if generate_btn:
    if len(st.session_state.messages) > 1:
        st.markdown("---")
        with st.expander("📊 Önerilen Proje Akış Şeması (Mermaid)", expanded=True):
            with st.spinner("Şema çiziliyor..."):
                try:
                    context = "\n".join([m["content"] for m in st.session_state.messages[-4:]])
                    diagram_prompt = f"Aşağıdaki konuşmaya göre bir Mermaid flowchart (graph TD) oluştur. Sadece kodu ver, açıklama yapma: {context}"
                    
                    result = model.generate_content(diagram_prompt)
                    clean_code = result.text.replace("```mermaid", "").replace("```", "").strip()
                    
                    st.subheader("Mimari Kod")
                    st.code(clean_code, language="mermaid")
                    
                    encoded_code = urllib.parse.quote(clean_code)
                    mermaid_url = f"https://mermaid.live/edit#base64:{{'code':'{encoded_code}'}}"
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.link_button("🖼️ Şemayı Tam Ekran Görüntüle", mermaid_url)
                    with c2:
                        st.download_button("📂 Şema Kodunu İndir", data=clean_code, file_name="proje_akisi.txt")
                    
                    st.success("✅ Akış şeması başarıyla oluşturuldu!")
                except Exception as e:
                    st.error(f"Şema oluşturulamadı: {e}")
    else:
        st.sidebar.warning("⚠️ Lütfen önce bir proje fikri girin!")

# --- 6. FOOTER ---
st.markdown("---")
st.caption("© 2026 HELP BRO AI - Gemini 1.5 Flash tarafından desteklenmektedir.")
