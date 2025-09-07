# utils/ui.py
import streamlit as st
from datetime import datetime

def setup_page_config():
    st.set_page_config(layout="wide", page_title="Stellarium — Ancient Clock (Python)")
    st.title("Stellarium — Ancient Indian Clock (Python demo)")
    st.caption("Default reference star for ancient sidereal time: Spica (Chitrā).")

def create_css_styles():
    return """
    <style>
    /* Make only the plot sticky */
    .sticky-plot {
        position: -webkit-sticky;
        position: sticky;
        top: 70px;   /* adjust so Streamlit header doesn't overlap */
        z-index: 99;
    }

    /* Right column scrolls independently */
    .right-scroll {
        max-height: calc(100vh - 80px);
        overflow-y: auto;
        padding-right: 8px;
    }

    .right-scroll::-webkit-scrollbar { width: 8px; }
    .right-scroll::-webkit-scrollbar-thumb {
        background-color: rgba(255,255,255,0.3);
        border-radius: 4px;
    }
    </style>
    """

def create_sidebar(stars_df):
    with st.sidebar:
        st.header("Observer & Time")
        lat = st.number_input("Latitude (°)", value=22.572600, format="%.6f")   # Kolkata default
        lon = st.number_input("Longitude (° East)", value=88.363900, format="%.6f")
        height_m = st.number_input("Height (m)", value=10.0, step=1.0)
        tz_offset = st.number_input("Local timezone offset (hours from UTC)", value=5.50, step=0.25)

        st.markdown("---")
        st.subheader("Local date & time (your timezone)")
        default_local = datetime.now()
        picked_date = st.date_input("Date", value=default_local.date())
        picked_time = st.time_input("Time", value=default_local.time().replace(microsecond=0))

        st.markdown("---")
        st.subheader("UI / options")
        ref_star_name = st.selectbox(
            "Reference star for sidereal zero",
            stars_df["name"].tolist(),
            index=0
        )
        view_mode = st.radio("Sky view mode", ["3D planetarium dome", "2D Alt–Az chart"], index=0)
        show_grid = st.checkbox("Show grid/markers", value=True)
        show_only_visible = st.checkbox("Show only stars above horizon", value=False)
        st.caption("Sunrise is found by numeric search for solar altitude crossing −0.833°.")
    
    return {
        "lat": lat,
        "lon": lon,
        "height_m": height_m,
        "tz_offset": tz_offset,
        "picked_date": picked_date,
        "picked_time": picked_time,
        "ref_star_name": ref_star_name,
        "view_mode": view_mode,
        "show_grid": show_grid,
        "show_only_visible": show_only_visible
    }