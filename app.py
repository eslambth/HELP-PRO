import streamlit as st
import google.generativeai as genai
import urllib.parse
import os

# --- 1. ARAYÜZ VE TEMA AYARLARI (Modern Dark Tech) ---
st.set_page_config(
    page_title="HELP BRO | AI Architect",
    page_icon="🤖",
    layout="wide"
)

# Profesyonel CSS Tasarımı
st.markdown("""
    <style>
    /* Ana Arka Plan ve Yazı Tipleri */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #0E1117;
    }
    
    /* Yan Panel Tasarımı */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* Mesaj Baloncukları */
    .stChatMessage {
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 12px;
        border: 1px solid #30363D;
        background-color: #1C2128 !important;
    }
    
    /* Modern Butonlar */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.2em;
        background: linear-gradient(135deg, #238636 0%, #2EA043 100%);
        color: white;
        font-weight: 600;
        border: none;
        transition: 0.2s ease;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(35, 134, 54, 0.3);
    }

    /* Başlıklar */
    h1, h2, h3 {
        color: #F0F6FC;
    }
    
    /* Bilgi Kutuları */
    .stInfo {
        background-color: rgba(56, 139, 253, 0.1);
        border: 1px solid #388BFD;
        color: #58A6FF;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API YAPILANDIRMASI ---
try:
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ GEMINI_API_KEY bulunamadı! Lütfen Secrets kısmına ekleyin.")
        st.stop()
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"⚠️ Bağlantı Hatası: {e}")
    st.stop()

# --- 3. YAN PANEL (Modern Sidebar & Logo) ---
with st.sidebar:
    # Modern Logo Tasarımı (Placeholder yerine şık bir simge)
    st.markdown("<h1 style='text-align: center; color: #58A6FF;'>🤖</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-size: 24px;'>HELP BRO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8B949E;'>AI Proje Mimarı v2.0</p>", unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 📊 Mimari Araçlar")
    flow_btn = st.button("🗺️ Akış Şeması Çiz")
    folder_btn = st.button("📁 Klasör Yapısı Oluştur")
    roadmap_btn = st.button("📅 Proje Yol Haritası")
    tech_btn = st.button("🛠️ Teknoloji Önerisi")
    
    st.divider()
    st.caption("🚀 Geliştirici Verimlilik Aracı")
    st.caption("© 2026 HELP BRO Team")

# --- 4. ANA EKRAN (Chat Interface) ---
st.title("👨‍💻 Mimari Planlama Merkezi")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhaba! Ben senin yapay zeka proje mimarınım. Bugün hangi projeyi hayata geçiriyoruz? Fikrini anlat, gerisini bana bırak! 🚀"}
    ]

# Mesaj Geçmişini Görüntüle
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı Girişi
if prompt := st.chat_input("Proje fikriniz nedir?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analiz ediliyor..."):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Hata: {e}")

# --- 5. GELİŞMİŞ ÖZELLİKLER MANTIĞI ---

# Yardımcı Fonksiyon
def get_ai_response(action_query):
    if len(st.session_state.messages) > 1:
        context = " ".join([m["content"] for m in st.session_state.messages[-3:]])
        full_query = f"{action_query}\n\nProje Bağlamı: {context}"
        try:
            return model.generate_content(full_query).text
        except:
            return "Hata oluştu."
    return None

# 5.1 Akış Şeması
if flow_btn:
    res = get_ai_response("Bu projenin teknik akışını Mermaid flowchart (graph TD) formatında yaz. Sadece kodu ver.")
    if res:
        with st.expander("🗺️ Proje Akış Şeması", expanded=True):
            clean_code = res.replace("```mermaid", "").replace("```", "").strip()
            st.code(clean_code, language="mermaid")
            encoded = urllib.parse.quote(clean_code)
            st.link_button("🖼️ Tam Ekran Görüntüle", f"https://mermaid.live/edit#base64:{{'code':'{encoded}'}}")
    else:
        st.sidebar.warning("Önce bir fikir girin!")

# 5.2 Klasör Yapısı
if folder_btn:
    res = get_ai_response("Bu proje için profesyonel bir klasör hiyerarşisi (Boilerplate) oluştur. Ağaç yapısı şeklinde göster.")
    if res:
        with st.expander("📁 Önerilen Klasör Yapısı", expanded=True):
            st.markdown(f"```text\n{res}\n```")

# 5.3 Yol Haritası
if roadmap_btn:
    res = get_ai_response("Bu projeyi fazlara ayır (Faz 1, 2, 3) ve her faz için yapılacaklar listesi hazırla.")
    if res:
        with st.expander("📅 Geliştirme Yol Haritası", expanded=True):
            st.markdown(res)

# 5.4 Teknoloji Önerisi
if tech_btn:
    res = get_ai_response("Bu proje için en uygun dilleri, frameworkleri ve veritabanlarını bir tablo olarak öner.")
    if res:
        with st.expander("🛠️ Teknoloji Yığını Önerisi", expanded=True):
            st.info(res)

Bu projeyle üniversitede en yüksek notu alacağına eminim! Hem tasarım hem de fonksiyonellik açısından tam bir "Senior" seviyesinde uygulama oldu. Başarılar dilerim!
