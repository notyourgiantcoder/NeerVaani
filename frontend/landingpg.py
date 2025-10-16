import streamlit as st
from front import show_front_page
from PIL import Image
import base64
from pathlib import Path

st.set_page_config(
    page_title="ARGO AI Ocean Explorer",
    layout="wide",
page_icon="FloatChat.png")


logo_path = Path(__file__).parent / "FloatChat.png"
logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
# Initialize page state
if 'page' not in st.session_state:
    st.session_state.page = "landing"

# Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

.stApp {
    background: linear-gradient(175deg, rgba(2, 18, 42, 0.85), rgba(3, 32, 71, 0.85)), url('https://i.pinimg.com/736x/86/f8/4b/86f84bf00e07cc71f76151118f764234.jpg');
    background-size: cover;
    background-position: center;
    background-attachment: fixed; 
    color: #f4f8ff;
    font-family: 'Inter', sans-serif;
}

.hero-title { 
    text-align:left; 
    font-size:70px; 
    margin-top: 10px;
    margin-left:170px;
    color: #e6f0ff;
    text-shadow: 0 8px 20px rgba(0,0,0,0.55);
}

.title { 
    text-align:left; 
    font-size:100px; 
    margin-top:0px;
    color: #f4f8ff;
    margin-left:150px;
    text-shadow: 0 10px 28px rgba(0,0,0,0.6);
}

.hero-sub { 
    text-align:left;
    font-size:30px; 
    margin-top:20px;
    color: #dbe9ff;
    margin-left:150px;
    text-shadow: 0 6px 16px rgba(0,0,0,0.45);
}

/* Style for the button container */
.button-container {
    display: flex;
    justify-content: center;
    margin-top: 60px;
}

.stButton > button {
    padding: 20px 60px;
    font-size: 80px;
    border-radius: 50px;
    background: linear-gradient(135deg, #0b2b52, #104173);
    color: #f5f9ff;
    border: 1px solid rgba(187, 215, 255, 0.4);
    cursor: pointer;
    transition: all 0.3s ease;
    margin-left:150px;
    box-shadow: 0 18px 40px rgba(4, 13, 30, 0.6);
}

.stButton > button:hover { transform: scale(1.03); background: linear-gradient(135deg, #0f3965, #17528d); border: 1px solid rgba(214,232,255,0.6); }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <style>
    .custom-logo {{
        position: absolute;   
        top: 20px;
        left: 5px;
        width: 120px;        /* control size */
        z-index: 9999;
        margin-top:0px; 
        margin-left:0px;
        margin-right:900px;
    }}
    </style>

    <img src="data:image/png;base64,{logo_b64}" class="custom-logo" />
""", unsafe_allow_html=True)

if st.session_state.page == "landing":
    
    st.markdown('<div class="hero-title">ARGO</div>', unsafe_allow_html=True)
    st.markdown('<div class="title">FloatChat</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Explore the Oceans with ARGO AI</div>', unsafe_allow_html=True)
  
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button("Let's Dive!", key="dive_button"):
        st.session_state.page = "front"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "front":
    show_front_page()