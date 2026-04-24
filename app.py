Skip to content
eslambth
HELP-PRO
Repository navigation
Code
Issues
Pull requests
Actions
Projects
Wiki
Security and quality
Insights
Settings
HELP-PRO
/
app.py
in
main

Edit

Preview
Indent mode

Spaces
Indent size

4
Line wrap mode

No wrap
Editing app.py file contents
  1
  2
  3
  4
  5
  6
  7
  8
  9
 10
 11
 12
 13
 14
 15
 16
 17
 18
 19
 20
 21
 22
 23
 24
 25
 26
 27
 28
 29
 30
 31
 32
 33
 34
 35
 36
import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="HELP BRO", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: white; }
    .stButton>button { background: #238636; color: white; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key Missing!")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def get_model():
    # سيجرب الكود كل الصيغ الممكنة لاسم الموديل ليتخطى خطأ 404
    names_to_test = ["gemini-1.5-flash", "gemini-pro", "models/gemini-1.5-flash"]
    for name in names_to_test:
        try:
            m = genai.GenerativeModel(name)
            m.generate_content("hi", generation_config={"max_output_tokens": 1})
            return m
        except:
            continue
    return None

model = get_model()

if "history" not in st.session_state:
Use Control + Shift + m to toggle the tab key moving focus. Alternatively, use esc then tab to move to the next interactive element on the page.
