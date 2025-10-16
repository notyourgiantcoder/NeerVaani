import streamlit as st
import requests
import time
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv

def is_ocean_data_query(user_input):
    """Check if the user input is related to ocean data."""
    keywords = [
        "ocean", "salinity", "temperature", "depth", "profile", "float", "sea", "pressure",
        "current", "marine", "water", "chlorophyll", "ph", "conductivity", "argo", "latitude", "longitude"
    ]
    user_input_lower = user_input.lower()
    return any(word in user_input_lower for word in keywords)

def fall_back_query(user_input):
    """Respond to non-ocean-data queries."""
    return (
        "Hi! 👋 I'm FloatChat, your assistant for analyzing oceanographic float data. "
        "It looks like your question isn't related to ocean data. "
        "Please ask me about ocean profiles, salinity, temperature, or other oceanographic topics!"
    )


def query_backend(user_query):
    """Query the backend API at http://127.0.0.1:5000/query"""
    load_dotenv()
    try:
        query_api = os.getenv("QUERY_API", default="http://127.0.0.1:5000/query")

        response = requests.post(
            query_api, 
            json={"query": user_query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        time.sleep(2)
        return "currently i'm not trained on this data"

    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def create_ocean_data_charts(depth_data):
    """Create beautiful charts for ocean data visualization"""
    if not depth_data:
        return None
    
    pressures = [d["pres"] for d in depth_data]
    temperatures = [d["temp"] for d in depth_data]
    salinities = [d["salinity"] for d in depth_data]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Temperature vs Depth', 'Salinity vs Depth'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Scatter(
            x=temperatures,
            y=pressures,
            mode='lines+markers',
            name='Temperature',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=6, color='#ff6b6b'),
            hovertemplate='<b>Temperature</b><br>Temp: %{x:.2f}°C<br>Depth: %{y:.1f} dbar<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=salinities,
            y=pressures,
            mode='lines+markers',
            name='Salinity',
            line=dict(color='#4ecdc4', width=3),
            marker=dict(size=6, color='#4ecdc4'),
            hovertemplate='<b>Salinity</b><br>Salinity: %{x:.3f} PSU<br>Depth: %{y:.1f} dbar<extra></extra>'
        ),
        row=1, col=2
    )
    
    
    fig.update_layout(
        title=dict(
            text='Ocean Data Profile',
            font=dict(size=20, color='black'),
            x=0.5
        ),
        showlegend=False,
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    fig.update_xaxes(
        title_text="Temperature (°C)",
        gridcolor='rgba(255,255,255,0.1)',
        row=1, col=1
    )
    fig.update_xaxes(
        title_text="Salinity (PSU)",
        gridcolor='rgba(255,255,255,0.1)',
        row=1, col=2
    )
    fig.update_yaxes(
        title_text="Pressure (dbar)",
        autorange="reversed",  
        gridcolor='rgba(255,255,255,0.1)',
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Pressure (dbar)",
        autorange="reversed",
        gridcolor='rgba(255,255,255,0.1)',
        row=1, col=2
    )
    
    return fig

def show_thinking_animation():
    """Display thinking animation"""
    thinking_placeholder = st.empty()
    
    for i in range(12):
        dots = "." * ((i % 3) + 1)
        thinking_placeholder.markdown(
            f"""
            <div class="thinking-container">
                <div class="thinking-text">Analyzing ocean data{dots}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        time.sleep(0.25)
    
    return thinking_placeholder

def display_metadata(data):
    """Display metadata in a clean format"""
    metadata_html = f"""
    <div class="metadata-container">
        <div class="metadata-item"> <strong>Location:</strong> {data.get('lat', 'N/A'):.3f}°N, {data.get('lon', 'N/A'):.3f}°E</div>
        <div class="metadata-item"> <strong>Time:</strong> {data.get('time', 'N/A')}</div>
        <div class="metadata-item"> <strong>Profile:</strong> {data.get('profile_id', 'N/A')}</div>
    </div>
    """
    st.markdown(metadata_html, unsafe_allow_html=True)

def show_chatbot_ui():
    st.set_page_config(
        page_title="FloatChat", 
        layout="wide",
        page_icon="🌊"
    )

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root { --text:#f4f8ff; --muted:#cfe0ff; --card-border: rgba(196, 220, 255, 0.28); }
    
    .stApp {
        background: linear-gradient(160deg, #081a34 0%, #173b6c 55%, #1f4d88 100%);
        font-family: 'Inter', sans-serif;
        color: var(--text);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(45deg, #8db9ff, #5a7dff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: rgba(234, 242, 255, 0.85);
        font-weight: 400;
    }
    
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .stChatMessage { margin: 1.5rem 0; padding: 0; }
    
    .stChatMessage[data-testid="chat-message-user"] { display:flex; justify-content:flex-end; align-items:flex-start; }
    
    .stChatMessage[data-testid="chat-message-user"] > div {
        background: linear-gradient(135deg, #6c8cff 0%, #4f68ff 100%);
        color: var(--text);
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        max-width: 70%;
        box-shadow: 0 12px 30px rgba(37, 71, 151, 0.45);
        margin-left: auto;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] { display:flex; justify-content:flex-start; align-items:flex-start; }
    
    .stChatMessage[data-testid="chat-message-assistant"] > div {
        background: rgba(255, 255, 255, 0.12);
        color: var(--text);
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        max-width: 80%;
        backdrop-filter: blur(14px);
        border: 1px solid var(--card-border);
        box-shadow: 0 12px 32px rgba(7, 15, 35, 0.4);
        margin-right: auto;
    }
    
    .thinking-container {
        background: rgba(255, 255, 255, 0.12);
        color: var(--text);
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        max-width: 80%;
        backdrop-filter: blur(14px);
        border: 1px solid var(--card-border);
        box-shadow: 0 12px 32px rgba(7, 15, 35, 0.4);
        margin-right: auto;
    }
    
    .thinking-text { color: rgba(234, 242, 255, 0.85); font-style: italic; letter-spacing: .02em; }
    
    /* Chat input bar: clean white pill with circular send button */
    .stChatInput { padding-bottom: max(8px, env(safe-area-inset-bottom)); margin-top: 6px; }
    
    .stChatInput > div { background: transparent; border: none; border-radius: 0; max-width: 900px; margin: 0.6rem auto 0.2rem auto; box-shadow: none; }
    
    .stChatInput:focus-within > div { transform: translateY(-1px); }
    
    .stChatInput textarea {
        background: #ffffff;
        color: #000000;
        border: 1px solid #d0d7e2;
        border-radius: 9999px;
        font-family: 'Inter', sans-serif;
        padding: 0.9rem 1.2rem;
        min-height: 48px;
        font-size: 0.98rem;
        transition: box-shadow 160ms ease, border-color 160ms ease;
    }
    .stChatInput textarea:focus { outline: none; border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }
    
    .stChatInput textarea::placeholder { color: #6b7280; opacity: 0.9; }
    
    .stChatInput button {
        background: linear-gradient(135deg, #6c8cff 0%, #4f68ff 100%);
        border: none;
        border-radius: 50%;
        color: #ffffff;
        width: 40px;
        height: 40px;
        margin: 0.4rem;
        box-shadow: 0 8px 16px rgba(37, 71, 151, 0.28);
        transition: transform 100ms ease, filter 120ms ease, box-shadow 160ms ease;
    }
    .stChatInput button:hover { filter: brightness(1.05); box-shadow: 0 10px 20px rgba(37, 71, 151, 0.35); }
    .stChatInput button:active { transform: scale(0.96); }
    .stChatInput button:disabled { filter: grayscale(0.2) brightness(0.92); box-shadow: none; }
    
    .metadata-container { margin-top: 1rem; padding: 1rem; background: rgba(5, 25, 55, 0.7); border-radius: 12px; border-left: 3px solid #6c8cff; box-shadow: 0 10px 24px rgba(5, 12, 28, 0.4); }
    
    .metadata-item { display: inline-block; margin: 0.25rem 1rem 0.25rem 0; font-size: 0.9rem; color: rgba(234, 242, 255, 0.85); }
    
    .stChatMessage img { display: none; }
    
    @media (max-width: 768px) { .main-title { font-size: 2rem; } .stChatMessage[data-testid="chat-message-user"] > div, .stChatMessage[data-testid="chat-message-assistant"] > div { max-width: 90%; } }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">FloatChat</h1>
        <p class="subtitle">Need help analysing ocean data? I'm here!</p>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.container():
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(msg["content"])
                    
                    if "metadata" in msg:
                        display_metadata(msg["metadata"])
                    
                    if "chart_data" in msg:
                        chart = create_ocean_data_charts(msg["chart_data"])
                        if chart:
                            st.plotly_chart(chart, use_container_width=True, config={'displayModeBar': False})

    if user_input := st.chat_input("Ask me about ocean data..."):

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            if is_ocean_data_query(user_input):
                thinking_placeholder = show_thinking_animation()
                response_data = query_backend(user_input)
                thinking_placeholder.empty()

                if response_data and len(response_data) > 0:
                    data = response_data[0]  
                    
                    if "query_explain" in data:
                        ai_response = data["query_explain"]
                        st.markdown(ai_response)
                        
                        display_metadata(data)
                        
                        message_obj = {
                            "role": "assistant", 
                            "content": ai_response,
                            "metadata": data 
                        }
                        
                        if "depth_levels" in data and data["depth_levels"]:
                            chart = create_ocean_data_charts(data["depth_levels"])
                            if chart:
                                st.plotly_chart(chart, use_container_width=True, config={'displayModeBar': False})
                                message_obj["chart_data"] = data["depth_levels"]
                        
                        st.session_state.messages.append(message_obj)
                    else:
                        error_msg = "No explanation available in the response."
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    error_msg = "🚫 Sorry, I couldn't retrieve ocean data right now. Please try again!"
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                error_msg = fall_back_query(user_input)
                st.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    show_chatbot_ui()
