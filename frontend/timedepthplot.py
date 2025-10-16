# timedepth_plot.py
import streamlit as st 
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px 

def show_time_depth_plot():
    # Custom CSS for time-depth plot page font colors
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

            :root {
                --bg-overlay: rgba(1, 18, 38, 0.70);
                --front-img: url('https://images.unsplash.com/photo-1604599340287-2042e85a3802?q=80&w=1400&auto=format&fit=crop');
                --text: #f4f8ff;
                --muted: #cfe0ff;
                --card-border: rgba(196, 220, 255, 0.28);
            }

            .stApp {
                    font-family: 'Inter', sans-serif;
                    background:
                            linear-gradient(180deg, var(--bg-overlay), var(--bg-overlay)),
                            var(--front-img);
                    background-size: cover;
                    background-position: center;
                    background-attachment: fixed;
                    color: var(--text);
            }
    
    /* Title colors */
    h1, h2, h3 { color: var(--text) !important; }
    
    /* Control panel labels */
    .stSelectbox label, .stDateInput label, .stNumberInput label { color: var(--muted) !important; font-weight: 600; }
    
    /* Section headers in controls */
    .stMarkdown h4, .stMarkdown strong { color: var(--text) !important; }

    /* Minor containers */
    .plot-container { background: rgba(255,255,255,0.06); border: 1px solid var(--card-border); border-radius: 12px; padding: .75rem; }
    </style>
    """, unsafe_allow_html=True)
    conn= sqlite3.connect("dummy.db")
    df=pd.read_sql("SELECT * FROM profiles", conn)
    conn.close()

    df['time'] = pd.to_datetime(df['time'])

    st.title("Depth-Time Plot")
    if isinstance(df['depth'].iloc[0], bytes):
        df['depth'] = df['depth'].apply(lambda x: int.from_bytes(x, byteorder='little'))

    col_graph, col_controls = st.columns([2, 1])

    with col_controls:
        parameter = st.selectbox("Choose Profile", [ "salinity", "air_temp", "oxygen"])

        st.markdown("**Time Range**")
        time_col1,time_col2 = st.columns(2)
        with time_col1:
            time_from = st.date_input("From", df['time'].min().date())
        with time_col2:
            time_to = st.date_input("To", df['time'].max().date())

        st.markdown("**Depth Range (m)**")
        depth_col1,depth_col2 = st.columns(2)
        with depth_col1:
            depth_from = st.number_input("From", int(df['depth'].min()), int(df['depth'].max()), int(df['depth'].min()))
        with depth_col2:
            depth_to = st.number_input("To", int(df['depth'].min()), int(df['depth'].max()), int(df['depth'].max()))

        st.markdown("**Location**")
        loc_1,loc_2= st.columns(2)
        with loc_1:
            lat = st.number_input("Latitude", float(df['latitude'].min()), float(df['latitude'].max()), float(df['latitude'].mean()))
        with loc_2:
            lon = st.number_input("Longitude", float(df['longitude'].min()), float(df['longitude'].max()), float(df['longitude'].mean()))

    filtered_df = df[
        (df['time'].dt.date >= time_from) & (df['time'].dt.date <= time_to) &
        (df['depth'] >= depth_from) & (df['depth'] <= depth_to) &
        (abs(df['latitude'] - lat) < 0.1) &
        (abs(df['longitude'] - lon) < 0.1)
    ]

    with col_graph:
        heatmap_data = filtered_df.pivot(index='depth', columns='time', values=parameter)

        fig = px.imshow(
            heatmap_data.sort_index(ascending=False),
            labels=dict(x="Time", y="Depth (m)", color=parameter.capitalize()),
            aspect="auto",
            color_continuous_scale="Turbo"  
        )
        st.plotly_chart(fig, use_container_width=True)