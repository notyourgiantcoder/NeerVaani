import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime, timedelta
from timedepthplot import show_time_depth_plot
from map_page import show_map
from chatbot_ui import show_chatbot_ui


st.set_page_config(
    page_title="ARGO-FloatChat",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
      --bg-overlay: rgba(1, 18, 38, 0.70);
      --text: #f4f8ff;
      --muted: #cfe0ff;
      --accent: #6cb8ff;
      --accent-strong: #4aa2ff;
      --card: rgba(4, 28, 64, 0.65);
      --card-border: rgba(196, 220, 255, 0.28);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .block-container { padding: 1rem 1.5rem; }

    .stApp {
        font-family: 'Inter', sans-serif;
        min-height: 100vh;
        color: var(--text);
        background:
          linear-gradient(180deg, var(--bg-overlay), var(--bg-overlay)),
          url("https://images.unsplash.com/photo-1604599340287-2042e85a3802?q=80&w=1400&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }

    /* Navigation buttons */
    div.stButton > button:first-child {
        background: rgba(6, 26, 60, 0.75);
        color: var(--text);
        font-weight: 600;
        font-size: 18px;
        padding: 8px 20px;
        border: 1px solid var(--card-border);
        border-radius: 999px;
        cursor: pointer;
        transition: all 0.25s ease;
        box-shadow: 0 8px 22px rgba(0,0,0,0.35);
    }
    div.stButton > button:first-child:hover {
        background: rgba(255, 255, 255, 0.18);
        color: #0a1f33;
        border-color: rgba(214,232,255,0.6);
    }
    div.stButton > button:first-child:active {
        transform: translateY(1px);
        border-color: var(--text);
    }

    /* Hero Section */
    .hero-section { text-align: center; padding: 4rem 0; margin-bottom: 3rem; }
    .hero-title {
        font-size: 4rem; font-weight: 700;
        background: linear-gradient(135deg, #ffffff, #bfe1ff);
        -webkit-background-clip: text; background-clip: text; color: transparent;
        text-shadow: 0 10px 26px rgba(0, 0, 0, 0.45);
        margin-bottom: 1rem;
    }
    .hero-subtitle { font-size: 1.5rem; font-weight: 500; color: var(--muted); letter-spacing: .5px; }
    .hero-description { font-size: 1.05rem; color: var(--text); max-width: 760px; margin: 0 auto; line-height: 1.7; opacity: .95; }

    /* Feature Cards */
    .feature-card {
        background: var(--card);
        backdrop-filter: blur(10px);
        border-radius: 18px;
        padding: 1.6rem;
        margin-bottom: 1.4rem;
        border: 1px solid var(--card-border);
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.35);
        transition: transform .2s ease, box-shadow .2s ease;
        height: 100%;
    }
    .feature-card:hover { transform: translateY(-4px); box-shadow: 0 20px 48px rgba(0, 0, 0, 0.45); }
    .feature-title { font-size: 1.25rem; font-weight: 600; color: var(--text); margin-bottom: .75rem; display:flex; align-items:center; gap:10px; }
    .feature-description { color: var(--muted); line-height: 1.6; font-size: .98rem; }
    .feature-icon { width: 22px; height: 22px; background: linear-gradient(135deg, #6cb8ff, #4aa2ff); border-radius: 8px; }

    /* Page Title Styling */
    .page-title {
        font-size: 2.2rem; font-weight: 700; color: var(--text); margin-bottom: 1.6rem; text-align: center;
        text-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
    }

    /* Content Cards */
    .content-card {
        background: rgba(255,255,255,0.06);
        border-radius: 14px; padding: 1.2rem; border: 1px solid var(--card-border);
        margin-bottom: 1rem; color: var(--text);
    }

    /* Statistics Cards */
    .stat-card {
        background: rgba(6, 28, 64, 0.8);
        border-radius: 12px; padding: 1rem; text-align: center;
        border: 1px solid var(--card-border);
        box-shadow: 0 10px 28px rgba(0,0,0,0.35);
    }
    .stat-value { font-size: 1.6rem; font-weight: 700; color: var(--accent); margin-bottom: .4rem; }
    .stat-label { font-size: .9rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }

    /* Sidebar and inputs */
    .sidebar-content { background: rgba(255,255,255,0.08); border-radius: 14px; padding: 1.2rem; border: 1px solid var(--card-border); }
    .stSelectbox > div > div > div { background: rgba(4, 24, 56, 0.8); border: 1px solid var(--card-border); border-radius: 8px; color: var(--text); }
    .stSelectbox > div > div > div > div { color: var(--text); }

    /* Plot Container */
    .plot-container { background: rgba(255,255,255,0.06); border-radius: 14px; padding: 1rem; margin-bottom: 1rem; border: 1px solid var(--card-border); }

    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-title { font-size: 2.6rem; }
        .hero-subtitle { font-size: 1.2rem; }
        .feature-card { padding: 1.4rem; }
    }

    /* Text Colors */
    .stMarkdown { color: var(--text); }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.12); border-radius: 4px; }
    ::-webkit-scrollbar-thumb { background: rgba(108, 184, 255, 0.6); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(108, 184, 255, 0.8); }
</style>
""", unsafe_allow_html=True)

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

@st.cache_resource
def create_dummy_data():
    conn = sqlite3.connect("dummy.db", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TIMESTAMP,
        depth REAL,
        latitude REAL,
        longitude REAL,
        salinity REAL,
        temperature REAL,
        air_temp REAL,
        oxygen REAL
    )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM profiles")
    if cursor.fetchone()[0] == 0:
        np.random.seed(42)
        base_time = datetime(2024, 1, 1, 0, 0, 0)
        lat, lon = 12.9716, 77.5946
        rows = []
        for i in range(100):
            t = base_time + timedelta(days=i*3)
            depth = np.random.choice([0, 10, 20, 50, 100, 200])
            latitude = lat + np.random.randn() * 0.1
            longitude = lon + np.random.randn() * 0.1
            salinity = 34 + np.random.rand() * 2
            temperature = 15 + np.random.rand() * 10
            air_temp = 20 + np.random.rand() * 5
            oxygen = 200 + np.random.rand() * 50
            rows.append((t, depth, latitude, longitude, salinity, temperature, air_temp, oxygen))

        base_time_2025 = datetime(2025, 1, 1, 0, 0, 0)
        for i in range(100):
            t = base_time_2025 + timedelta(days=i*3)
            depth = np.random.choice([0, 10, 20, 50, 100, 200])
            latitude = lat + np.random.randn() * 0.1
            longitude = lon + np.random.randn() * 0.1
            salinity = 34.5 + np.random.rand() * 2
            temperature = 16 + np.random.rand() * 10
            air_temp = 21 + np.random.rand() * 5
            oxygen = 210 + np.random.rand() * 50
            rows.append((t, depth, latitude, longitude, salinity, temperature, air_temp, oxygen))

        cursor.executemany("""
        INSERT INTO profiles (time, depth, latitude, longitude, salinity, temperature, air_temp, oxygen)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        
        conn.commit()
    return conn

@st.cache_data
def load_data():
    conn = create_dummy_data()
    df = pd.read_sql_query("SELECT * FROM profiles", conn)
    df['time'] = pd.to_datetime(df['time'])
    df['year'] = df['time'].dt.year
    return df

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()


nav_cols = st.columns([0.6, 1, 1, 1, 1, 1, 0.6])
nav_items = [
    ("", "Home", 'home'),
    ("", "FloatChat", 'chatbot'),
    ("", "Map", 'map'),
    ("", "Profile Comparision", 'comparison'),
    ("", "Depth-Time Plots", 'time_depth')
]

for i, (icon, label, page) in enumerate(nav_items):
    with nav_cols[i+1]:  # Skip first column for left spacing; last column for right spacing
        if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{page}"):
            navigate_to(page)


if st.session_state.current_page == "home":
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">ARGO FloatChat</div>
        <div class="hero-subtitle">Analyse Ocean data with ease</div>
        <div class="hero-description">
            Analyse ARGO Float data with simple commands, talk to our chatbot and get real time updates along with visulizations of the required profiles, everything at one place.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">
                <div class="feature-icon"></div>
                FloatChat AI
            </div>
            <div class="feature-description">
                Intelligent chatbot that makes ocean data accessible to everyone. Query float locations, 
                temperature trends, and salinity variations using natural language. Perfect for researchers 
                and educators alike.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">
                <div class="feature-icon"></div>
                Smart Analytics
            </div>
            <div class="feature-description">
                Advanced statistical analysis and anomaly detection. Compare multiple datasets, 
                identify trends, and generate comprehensive reports with automated insights.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">
                <div class="feature-icon"></div>
                Interactive Mapping
            </div>
            <div class="feature-description">
                Real-time visualization of ARGO float trajectories across global oceans. 
                Interactive maps with zoom controls, temporal filters, and detailed float information 
                for comprehensive monitoring.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">
                <div class="feature-icon"></div>
                Real-time Data
            </div>
            <div class="feature-description">
                Access to live ARGO float data streams with automatic updates. 
                Monitor ocean conditions as they happen with minimal latency.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">
                <div class="feature-icon"></div>
                Advanced Visualization
            </div>
            <div class="feature-description">
                Depth-time heatmaps, profile comparisons, and multi-dimensional analysis tools. 
                Explore temperature, salinity, and oxygen variations across different depths 
                and time periods with interactive charts.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">
                <div class="feature-icon"></div>
                Research Tools
            </div>
            <div class="feature-description">
                Comprehensive suite of tools for oceanographic research including 
                profile comparison, statistical analysis, and export capabilities.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ffffff; margin-bottom: 2rem;'>Platform Statistics</h2>", unsafe_allow_html=True)
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">200+</div>
            <div class="stat-label">Active Floats</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">1M+</div>
            <div class="stat-label">Data Points</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">24/7</div>
            <div class="stat-label">Monitoring</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col4:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">Global</div>
            <div class="stat-label">Coverage</div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == "chatbot":
    st.markdown('<div class="page-title">FloatChat - Ocean Data Assistant</div>', unsafe_allow_html=True)
    show_chatbot_ui()

elif st.session_state.current_page == "map":
    st.markdown('<div class="page-title">ARGO float location</div>', unsafe_allow_html=True)
    show_map()

elif st.session_state.current_page == "comparison":
    st.markdown('<div class="page-title">Profile Comparison Analysis</div>', unsafe_allow_html=True)
    df = load_data()
    main_col, sidebar_col = st.columns([0.7, 0.3])

    with sidebar_col:
        st.markdown("### Analysis Controls")
        available_years = sorted(df['year'].unique())
        properties = ['salinity', 'temperature', 'air_temp', 'oxygen']
        property_labels = {
            'salinity': ' Salinity',
            'temperature': ' Temperature', 
            'air_temp': ' Air Temperature',
            'oxygen': 'Oxygen'
        }
        
        selected_property = st.selectbox("Choose Profile Type", properties, 
                                       format_func=lambda x: property_labels[x])
        
        st.markdown("**Select Years to Compare**")
        col_from, col_to = st.columns(2)
        with col_from:
            year1 = st.selectbox("From Year", available_years, index=0)
        with col_to:
            year2 = st.selectbox("To Year", available_years, index=1 if len(available_years) > 1 else 0)

    with main_col:
        # Comparison page: remove glass morph effect from graph containers only
        st.markdown(
            """
            <style>
            .comparison-plain .plot-container { 
                background: transparent !important; 
                border: none !important; 
                backdrop-filter: none !important; 
                box-shadow: none !important; 
            }
            /* Give Plotly charts a simple solid background for readability */
            .comparison-plain [data-testid="stPlotlyChart"],
            .comparison-plain .js-plotly-plot {
                background: #ffffff !important;
                border-radius: 10px;
                padding: 8px;
            }
            </style>
            <section class="comparison-plain">
            """,
            unsafe_allow_html=True,
        )
        df_year1 = df[df['year'] == year1]
        df_year2 = df[df['year'] == year2]

        
    # Combined comparison plot removed as requested

        
        st.subheader(" Distribution Analysis")
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(y=df_year1[selected_property], name=f'{year1}', 
                                boxpoints='outliers', marker_color='#4fc3f7'))
        fig_box.add_trace(go.Box(y=df_year2[selected_property], name=f'{year2}', 
                                boxpoints='outliers', marker_color='#f06292'))
        fig_box.update_layout(
            title=f"{selected_property.title()} Distribution Comparison", 
            yaxis_title=selected_property.title(),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig_box, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("Individual Year Analysis")
        year_col1, year_col2 = st.columns(2)
        with year_col1:
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            fig1 = px.line(df_year1, x='time', y=selected_property, 
                          title=f"{selected_property.title()} - {year1}", 
                          color_discrete_sequence=['#4fc3f7'])
            fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with year_col2:
            st.markdown('<div class="plot-container">', unsafe_allow_html=True)
            fig2 = px.line(df_year2, x='time', y=selected_property, 
                          title=f"{selected_property.title()} - {year2}", 
                          color_discrete_sequence=['#f06292'])
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("Statistical Summary")
        stats_col1, stats_col2 = st.columns(2)
        with stats_col1:
            st.markdown(f"** {year1} Statistics**")
            st.write(f"**Mean:** {df_year1[selected_property].mean():.2f}")
            st.write(f"**Std Dev:** {df_year1[selected_property].std():.2f}")
            st.write(f"**Min:** {df_year1[selected_property].min():.2f}")
            st.write(f"**Max:** {df_year1[selected_property].max():.2f}")
        with stats_col2:
            st.markdown(f"** {year2} Statistics**")
            st.write(f"**Mean:** {df_year2[selected_property].mean():.2f}")
            st.write(f"**Std Dev:** {df_year2[selected_property].std():.2f}")
            st.write(f"**Min:** {df_year2[selected_property].min():.2f}")
            st.write(f"**Max:** {df_year2[selected_property].max():.2f}")

        # Close comparison section wrapper
        st.markdown("</section>", unsafe_allow_html=True)

elif st.session_state.current_page == "time_depth":
    st.markdown('<div class="page-title">Depth-Time Analysis</div>', unsafe_allow_html=True)
    show_time_depth_plot()

st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
