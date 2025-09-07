# app.py
# ------------------------------------------------------------
# Stellarium — Ancient Indian Clock (Streamlit + Astropy)
# Planetarium-style interactive sky dome (3D) + classic 2D view
# ------------------------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time as dtime
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord, AltAz, get_sun
import astropy.units as u
import plotly.graph_objects as go
import time

# Import modules
from utils.helpers import (
    to_earthlocation, time_from_local_localdt, local_sidereal_time_hours,
    approximate_sunrise_utc_for_local_date, find_time_for_lst, solve_time_from_altaz,
    altaz_to_unit_vector, make_dome_mesh, ring_points_alt, meridian_points_az,
    compute_stars_positions_for_time
)
from utils.ui import setup_page_config, create_sidebar
from utils.star_catalog import get_star_catalog
from utils.plots import create_3d_planetarium, create_2d_altaz_chart
from utils.panchang import display_panchang_details  # <-- Import Panchang display function

# Session state initialization
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now()
if "last_plot_update" not in st.session_state:
    st.session_state.last_plot_update = datetime.now()
if "current_time" not in st.session_state:
    st.session_state.current_time = datetime.now()
if "plot_refresh_counter" not in st.session_state:
    st.session_state.plot_refresh_counter = 0

# ============================================================
# Custom CSS for independent scrolling
# ============================================================
st.markdown(
    """
    <style>
    /* Main container for columns */
    .main-container {
        display: flex;
        flex-direction: row;
        gap: 5px;
        position: relative;
    }
    
    /* Left column with plot - fixed */
    .left-column {
        flex: 2.4;
        position: sticky;
        top: 20px;
        height: 20px;
        z-index: 99;
    }
    
    /* Right column scrolls independently */
    .right-column {
        flex: 1;
        max-height: calc(100vh - 100px);
        overflow-y: auto;
        padding-right: 8px;
    }
    
    /* Make the plot container sticky */
    .sticky-plot {
        position: sticky;
        top: 40px;
        z-index: 100;
    }
    
    /* Scrollable content in right column */
    .scrollable-content {
        max-height: calc(100vh - 100px);
        overflow-y: auto;
    }
    
    .right-column::-webkit-scrollbar { width: 8px; }
    .right-column::-webkit-scrollbar-thumb {
        background-color: rgba(255,255,255,0.3);
        border-radius: 4px;
    }
    
    /* Fix for Streamlit column spacing */
    [data-testid="column"] {
        padding: 0;
    }
    
    /* Ensure proper spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    
    /* Real-time clock styling */
    .real-time-clock {
        font-size: 1.2em;
        font-weight: bold;
        color: #4CAF50;
        margin-bottom: 10px;
        padding: 5px;
        background-color: #f0f2f6;
        border-radius: 5px;
        text-align: center;
    }
    
    /* Auto refresh status */
   /* .refresh-status {
        font-size: 0.9em;
        color: #666;
        margin-top: 10px;
        padding: 5px;
        background-color: #f9f9f9;
        border-radius: 5px;
    }*/
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Main application
# ============================================================
def main():
    # Setup page configuration
    setup_page_config()
    
    # Get star catalog
    stars_df = get_star_catalog()
    
    # Create sidebar and get user inputs
    user_inputs = create_sidebar(stars_df)
    
    # Extract user inputs
    lat = user_inputs["lat"]
    lon = user_inputs["lon"]
    height_m = user_inputs["height_m"]
    tz_offset = user_inputs["tz_offset"]
    picked_date = user_inputs["picked_date"]
    picked_time = user_inputs["picked_time"]
    ref_star_name = user_inputs["ref_star_name"]
    view_mode = user_inputs["view_mode"]
    show_grid = user_inputs["show_grid"]
    show_only_visible = user_inputs["show_only_visible"]
    
    # Update current time
    current_time = datetime.now()
    time_diff = (current_time - st.session_state.last_update).total_seconds()
    
    # Update time every second without refreshing the whole page
    if time_diff >= 1:
        st.session_state.current_time = current_time
        st.session_state.last_update = current_time
        st.session_state.plot_refresh_counter += 1
    
    # Check if we need to update the plot (every 20 minutes = 1200 seconds)
    plot_update_needed = st.session_state.plot_refresh_counter >= 1200
    if plot_update_needed:
        st.session_state.last_plot_update = current_time
        st.session_state.plot_refresh_counter = 0
    
    # Use the current time for display
    current_dt = datetime.combine(picked_date, st.session_state.current_time.time().replace(microsecond=0))
    
    # Core computations
    utc_time = time_from_local_localdt(current_dt, tz_offset)
    location = to_earthlocation(lat, lon, height_m)
    lst_hours = local_sidereal_time_hours(utc_time, lon)
    
    # Compute star positions (only update if needed for plot refresh)
    if not plot_update_needed and "stars_df_cached" in st.session_state:
        stars_df = st.session_state.stars_df_cached
    else:
        stars_df = compute_stars_positions_for_time(utc_time, location, stars_df)
        st.session_state.stars_df_cached = stars_df
    
    # Calculate sunrise and ancient time units
    sunrise_time_utc = approximate_sunrise_utc_for_local_date(
        current_dt.date(), location, tz_offset, step_minutes=10
    )
    seconds_since_sunrise = (utc_time.utc.datetime - sunrise_time_utc.utc.datetime).total_seconds()
    
    if seconds_since_sunrise < 0:
        prev = approximate_sunrise_utc_for_local_date(
            (current_dt - timedelta(days=1)).date(), location, tz_offset, 10
        )
        seconds_since_sunrise = (utc_time.utc.datetime - prev.utc.datetime).total_seconds()
        sunrise_time_utc = prev
    
    ghati_sec = 24 * 60  # 1 ghaṭi = 24 min = 1440 s
    ghati = seconds_since_sunrise / ghati_sec
    muhurta = ghati / 2.0
    yama = ghati / 7.5
    
    # Create layout with proper columns
    col1, col2 = st.columns([2.4, 1])
    
    with col1:
        st.markdown('<div class="left-column">', unsafe_allow_html=True)
        if view_mode == "3D planetarium dome":
            st.subheader("Planetarium (drag to rotate / scroll to zoom)")
            fig = create_3d_planetarium(stars_df, show_grid, show_only_visible)
        else:
            st.subheader("Sky view (Azimuth vs Altitude)")
            fig = create_2d_altaz_chart(stars_df, show_grid, show_only_visible)
        
        st.markdown('<div class="sticky-plot">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, use_container_height=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.subheader("Notes & next steps")
        st.write(
            """
- Coordinates and sidereal time by **Astropy**; sunrise is found via numeric altitude crossing (-0.833°).
- For higher accuracy: apply precession/nutation to epoch-of-date; use a refined root solver for sunrise; extend the catalog (HYG/Hipparcos).
- The **3D dome** shows ENU coordinates (x=East, y=North, z=Up). Horizon is the rim; yellow points are above the horizon.
- Toggle "Show only stars above horizon" to declutter the view.
            """
        )
        # Display refresh status
        st.markdown("---")
        st.markdown('<div class="refresh-status">', unsafe_allow_html=True)
        st.write("**Auto-refresh status:**")
        st.write(f"⌛ Clock updates: Every second")
        st.write(f"🔄 Plot updates: Every 20 minutes")
        st.write(f"📊 Last plot update: {st.session_state.last_plot_update.strftime('%H:%M:%S')}")
        st.write(f"⏱️ Next plot update in: {1200 - st.session_state.plot_refresh_counter} seconds")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="right-column">', unsafe_allow_html=True)
        st.markdown('<div class="scrollable-content">', unsafe_allow_html=True)
        
        # Display real-time clock
        st.markdown(f'<div class="real-time-clock">🕒 {st.session_state.current_time.strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)
        
        # Display observer and clock information
        st.subheader("Observer & Clocks")
        st.write(f"**Local time:** {current_dt.strftime('%Y-%m-%d %H:%M:%S')}  (UTC: {utc_time.iso})")
        st.write(f"**Local Sidereal Time (LST):** {lst_hours:.6f} h")
        st.markdown("**Ancient clock (since sunrise)**")
        sunrise_local_dt = sunrise_time_utc.utc.datetime + timedelta(hours=tz_offset)
        st.write(f"Sunrise (approx local): {sunrise_local_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"{ghati:.3f} ghaṭi — {muhurta:.3f} muhūrta — {yama:.3f} yāma")
        st.markdown("---")

        # ========== Panchang Functionality ==========
        if st.button("Show Today's Panchang"):
            display_panchang_details(
                current_dt=current_dt,
                location=location,
                tz_offset=tz_offset,
                sunrise_time_utc=sunrise_time_utc,
                ghati=ghati,
                muhurta=muhurta,
                yama=yama,
            )
        # ========== End Panchang Functionality ==========

        # Star selection and time solver
        st.subheader("Star selection & time solver")
        st.write("Pick a star to compute transit time or solve the time from an observed Alt/Az.")
        
        sel_name = st.selectbox(
            "Choose star", 
            stars_df["name"].tolist(),
            index=stars_df["name"].tolist().index(ref_star_name)
        )
        star_row = stars_df[stars_df["name"] == sel_name].iloc[0]
        
        # Display star details safely
        star_info = star_row[["name", "ra_h", "dec_deg", "mag", "alt_deg", "az_deg", "visible"]].to_dict()
        st.table(pd.DataFrame([star_info], dtype=str))
        
        st.info("Spica (Chitrā) is used traditionally in many Siddhāntic texts as a key reference (default).")
        
        if st.button("Compute meridian transit time (LST ≈ RA)"):
            target_ra_h = float(star_row["ra_h"])
            found_time = find_time_for_lst(target_ra_h, utc_time, lon)
            found_local = found_time.utc.datetime + timedelta(hours=tz_offset)
            st.success(
                f"Star **{sel_name}** meridian transit ≈ "
                f"Local: {found_local.strftime('%Y-%m-%d %H:%M:%S')} "
                f"(UTC: {found_time.iso})"
            )
            # Hour angle now
            ha_now = (lst_hours - target_ra_h + 24) % 24
            if ha_now > 12: 
                ha_now -= 24
            st.write(f"Current hour angle (H = LST - RA): **{ha_now:.6f} h** (negative ⇒ east of meridian)")
        
        st.markdown("—")
        st.write("Or use the star's **current** Alt/Az (from the sky view) to solve the time:")
        if st.button("Solve time from observed Alt/Az (use star's current Alt/Az)"):
            target_alt = float(star_row["alt_deg"])
            target_az = float(star_row["az_deg"])
            found_time2, err_deg = solve_time_from_altaz(
                target_alt, target_az, star_row["ra_h"], star_row["dec_deg"], utc_time, location
            )
            local_found = found_time2.utc.datetime + timedelta(hours=tz_offset)
            st.success(
                f"Solved time (best-fit) ≈ "
                f"Local: {local_found.strftime('%Y-%m-%d %H:%M:%S')} "
                f"(UTC: {found_time2.iso})"
            )
            st.write(f"Estimated positional error: **{err_deg:.4f}°**")
            delta_seconds = (found_time2.utc.datetime - utc_time.utc.datetime).total_seconds()
            st.write(f"Difference from current input time: **{delta_seconds:.1f} s**")
        
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Use JavaScript to periodically update the time without full page refresh
    st.markdown(
        f"""
        <script>
        function updateTime() {{
            // This will trigger a script run every second
            window.parent.postMessage({{type: 'streamlit:setComponentValue', value: {int(time.time())}}}, '*');
        }}
        setInterval(updateTime, 1000);
        </script>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.caption("Built with Astropy + Plotly + Streamlit — demo by Kuntal.")

if __name__ == "__main__":
    main()






# # app.py
# # ------------------------------------------------------------
# # Stellarium — Ancient Indian Clock (Streamlit + Astropy)
# # Planetarium-style interactive sky dome (3D) + classic 2D view
# # ------------------------------------------------------------
# import streamlit as st
# import pandas as pd
# import numpy as np
# from datetime import datetime, timedelta, time as dtime
# from astropy.time import Time
# from astropy.coordinates import EarthLocation, SkyCoord, AltAz, get_sun
# import astropy.units as u
# import plotly.graph_objects as go
# import time

# # Import modules
# from utils.helpers import (
#     to_earthlocation, time_from_local_localdt, local_sidereal_time_hours,
#     approximate_sunrise_utc_for_local_date, find_time_for_lst, solve_time_from_altaz,
#     altaz_to_unit_vector, make_dome_mesh, ring_points_alt, meridian_points_az,
#     compute_stars_positions_for_time
# )
# from utils.ui import setup_page_config, create_sidebar
# from utils.star_catalog import get_star_catalog
# from utils.plots import create_3d_planetarium, create_2d_altaz_chart

# # Session state initialization
# if "last_update" not in st.session_state:
#     st.session_state.last_update = datetime.now()
# if "last_plot_update" not in st.session_state:
#     st.session_state.last_plot_update = datetime.now()
# if "current_time" not in st.session_state:
#     st.session_state.current_time = datetime.now()
# if "plot_refresh_counter" not in st.session_state:
#     st.session_state.plot_refresh_counter = 0

# # ============================================================
# # Custom CSS for independent scrolling
# # ============================================================
# st.markdown(
#     """
#     <style>
#     /* Main container for columns */
#     .main-container {
#         display: flex;
#         flex-direction: row;
#         gap: 5px;
#         position: relative;
#     }
    
#     /* Left column with plot - fixed */
#     .left-column {
#         flex: 2.4;
#         position: sticky;
#         top: 20px;
#         height: 20px;
#         z-index: 99;
#     }
    
#     /* Right column scrolls independently */
#     .right-column {
#         flex: 1;
#         max-height: calc(100vh - 100px);
#         overflow-y: auto;
#         padding-right: 8px;
#     }
    
#     /* Make the plot container sticky */
#     .sticky-plot {
#         position: sticky;
#         top: 40px;
#         z-index: 100;
#     }
    
#     /* Scrollable content in right column */
#     .scrollable-content {
#         max-height: calc(100vh - 100px);
#         overflow-y: auto;
#     }
    
#     .right-column::-webkit-scrollbar { width: 8px; }
#     .right-column::-webkit-scrollbar-thumb {
#         background-color: rgba(255,255,255,0.3);
#         border-radius: 4px;
#     }
    
#     /* Fix for Streamlit column spacing */
#     [data-testid="column"] {
#         padding: 0;
#     }
    
#     /* Ensure proper spacing */
#     .block-container {
#         padding-top: 2rem;
#         padding-bottom: 0rem;
#     }
    
#     /* Real-time clock styling */
#     .real-time-clock {
#         font-size: 1.2em;
#         font-weight: bold;
#         color: #4CAF50;
#         margin-bottom: 10px;
#         padding: 5px;
#         background-color: #f0f2f6;
#         border-radius: 5px;
#         text-align: center;
#     }
    
#     /* Auto refresh status */
#     .refresh-status {
#         font-size: 0.9em;
#         color: #666;
#         margin-top: 10px;
#         padding: 5px;
#         background-color: #f9f9f9;
#         border-radius: 5px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# # ============================================================
# # Main application
# # ============================================================
# def main():
#     # Setup page configuration
#     setup_page_config()
    
#     # Get star catalog
#     stars_df = get_star_catalog()
    
#     # Create sidebar and get user inputs
#     user_inputs = create_sidebar(stars_df)
    
#     # Extract user inputs
#     lat = user_inputs["lat"]
#     lon = user_inputs["lon"]
#     height_m = user_inputs["height_m"]
#     tz_offset = user_inputs["tz_offset"]
#     picked_date = user_inputs["picked_date"]
#     picked_time = user_inputs["picked_time"]
#     ref_star_name = user_inputs["ref_star_name"]
#     view_mode = user_inputs["view_mode"]
#     show_grid = user_inputs["show_grid"]
#     show_only_visible = user_inputs["show_only_visible"]
    
#     # Update current time
#     current_time = datetime.now()
#     time_diff = (current_time - st.session_state.last_update).total_seconds()
    
#     # Update time every second without refreshing the whole page
#     if time_diff >= 1:
#         st.session_state.current_time = current_time
#         st.session_state.last_update = current_time
#         st.session_state.plot_refresh_counter += 1
    
#     # Check if we need to update the plot (every 20 minutes = 1200 seconds)
#     plot_update_needed = st.session_state.plot_refresh_counter >= 1200
#     if plot_update_needed:
#         st.session_state.last_plot_update = current_time
#         st.session_state.plot_refresh_counter = 0
    
#     # Use the current time for display
#     current_dt = datetime.combine(picked_date, st.session_state.current_time.time().replace(microsecond=0))
    
#     # Core computations
#     utc_time = time_from_local_localdt(current_dt, tz_offset)
#     location = to_earthlocation(lat, lon, height_m)
#     lst_hours = local_sidereal_time_hours(utc_time, lon)
    
#     # Compute star positions (only update if needed for plot refresh)
#     if not plot_update_needed and "stars_df_cached" in st.session_state:
#         stars_df = st.session_state.stars_df_cached
#     else:
#         stars_df = compute_stars_positions_for_time(utc_time, location, stars_df)
#         st.session_state.stars_df_cached = stars_df
    
#     # Calculate sunrise and ancient time units
#     sunrise_time_utc = approximate_sunrise_utc_for_local_date(
#         current_dt.date(), location, tz_offset, step_minutes=10
#     )
#     seconds_since_sunrise = (utc_time.utc.datetime - sunrise_time_utc.utc.datetime).total_seconds()
    
#     if seconds_since_sunrise < 0:
#         prev = approximate_sunrise_utc_for_local_date(
#             (current_dt - timedelta(days=1)).date(), location, tz_offset, 10
#         )
#         seconds_since_sunrise = (utc_time.utc.datetime - prev.utc.datetime).total_seconds()
#         sunrise_time_utc = prev
    
#     ghati_sec = 24 * 60  # 1 ghaṭi = 24 min = 1440 s
#     ghati = seconds_since_sunrise / ghati_sec
#     muhurta = ghati / 2.0
#     yama = ghati / 7.5
    
#     # Create layout with proper columns
#     col1, col2 = st.columns([2.4, 1])
    
#     with col1:
#         st.markdown('<div class="left-column">', unsafe_allow_html=True)
#         if view_mode == "3D planetarium dome":
#             st.subheader("Planetarium (drag to rotate / scroll to zoom)")
#             fig = create_3d_planetarium(stars_df, show_grid, show_only_visible)
#         else:
#             st.subheader("Sky view (Azimuth vs Altitude)")
#             fig = create_2d_altaz_chart(stars_df, show_grid, show_only_visible)
        
#         st.markdown('<div class="sticky-plot">', unsafe_allow_html=True)
#         st.plotly_chart(fig, use_container_width=True, use_container_height=True)
#         st.markdown('</div>', unsafe_allow_html=True)
#         st.markdown('</div>', unsafe_allow_html=True)
#         st.subheader("Notes & next steps")
#         st.write(
#             """
# - Coordinates and sidereal time by **Astropy**; sunrise is found via numeric altitude crossing (-0.833°).
# - For higher accuracy: apply precession/nutation to epoch-of-date; use a refined root solver for sunrise; extend the catalog (HYG/Hipparcos).
# - The **3D dome** shows ENU coordinates (x=East, y=North, z=Up). Horizon is the rim; yellow points are above the horizon.
# - Toggle "Show only stars above horizon" to declutter the view.
#             """
#         )
    
#     with col2:
#         st.markdown('<div class="right-column">', unsafe_allow_html=True)
#         st.markdown('<div class="scrollable-content">', unsafe_allow_html=True)
        
#         # Display real-time clock
#         st.markdown(f'<div class="real-time-clock">🕒 {st.session_state.current_time.strftime("%Y-%m-%d %H:%M:%S")}</div>', unsafe_allow_html=True)
        
#         # Display observer and clock information
#         st.subheader("Observer & Clocks")
#         st.write(f"**Local time:** {current_dt.strftime('%Y-%m-%d %H:%M:%S')}  (UTC: {utc_time.iso})")
#         st.write(f"**Local Sidereal Time (LST):** {lst_hours:.6f} h")
#         st.markdown("**Ancient clock (since sunrise)**")
#         sunrise_local_dt = sunrise_time_utc.utc.datetime + timedelta(hours=tz_offset)
#         st.write(f"Sunrise (approx local): {sunrise_local_dt.strftime('%Y-%m-%d %H:%M:%S')}")
#         st.write(f"{ghati:.3f} ghaṭi — {muhurta:.3f} muhūrta — {yama:.3f} yāma")
#         st.markdown("---")
        
#         # Star selection and time solver
#         st.subheader("Star selection & time solver")
#         st.write("Pick a star to compute transit time or solve the time from an observed Alt/Az.")
        
#         sel_name = st.selectbox(
#             "Choose star", 
#             stars_df["name"].tolist(),
#             index=stars_df["name"].tolist().index(ref_star_name)
#         )
#         star_row = stars_df[stars_df["name"] == sel_name].iloc[0]
        
#         # Display star details safely
#         star_info = star_row[["name", "ra_h", "dec_deg", "mag", "alt_deg", "az_deg", "visible"]].to_dict()
#         st.table(pd.DataFrame([star_info], dtype=str))
        
#         st.info("Spica (Chitrā) is used traditionally in many Siddhāntic texts as a key reference (default).")
        
#         if st.button("Compute meridian transit time (LST ≈ RA)"):
#             target_ra_h = float(star_row["ra_h"])
#             found_time = find_time_for_lst(target_ra_h, utc_time, lon)
#             found_local = found_time.utc.datetime + timedelta(hours=tz_offset)
#             st.success(
#                 f"Star **{sel_name}** meridian transit ≈ "
#                 f"Local: {found_local.strftime('%Y-%m-%d %H:%M:%S')} "
#                 f"(UTC: {found_time.iso})"
#             )
#             # Hour angle now
#             ha_now = (lst_hours - target_ra_h + 24) % 24
#             if ha_now > 12: 
#                 ha_now -= 24
#             st.write(f"Current hour angle (H = LST - RA): **{ha_now:.6f} h** (negative ⇒ east of meridian)")
        
#         st.markdown("—")
#         st.write("Or use the star's **current** Alt/Az (from the sky view) to solve the time:")
#         if st.button("Solve time from observed Alt/Az (use star's current Alt/Az)"):
#             target_alt = float(star_row["alt_deg"])
#             target_az = float(star_row["az_deg"])
#             found_time2, err_deg = solve_time_from_altaz(
#                 target_alt, target_az, star_row["ra_h"], star_row["dec_deg"], utc_time, location
#             )
#             local_found = found_time2.utc.datetime + timedelta(hours=tz_offset)
#             st.success(
#                 f"Solved time (best-fit) ≈ "
#                 f"Local: {local_found.strftime('%Y-%m-%d %H:%M:%S')} "
#                 f"(UTC: {found_time2.iso})"
#             )
#             st.write(f"Estimated positional error: **{err_deg:.4f}°**")
#             delta_seconds = (found_time2.utc.datetime - utc_time.utc.datetime).total_seconds()
#             st.write(f"Difference from current input time: **{delta_seconds:.1f} s**")
        
#         # Display refresh status
#         st.markdown("---")
#         st.markdown('<div class="refresh-status">', unsafe_allow_html=True)
#         st.write("**Auto-refresh status:**")
#         st.write(f"⌛ Clock updates: Every second")
#         st.write(f"🔄 Plot updates: Every 20 minutes")
#         st.write(f"📊 Last plot update: {st.session_state.last_plot_update.strftime('%H:%M:%S')}")
#         st.write(f"⏱️ Next plot update in: {1200 - st.session_state.plot_refresh_counter} seconds")
#         st.markdown('</div>', unsafe_allow_html=True)
        
#         st.markdown('</div>', unsafe_allow_html=True)
#         st.markdown('</div>', unsafe_allow_html=True)
    
#     # Use JavaScript to periodically update the time without full page refresh
#     st.markdown(
#         f"""
#         <script>
#         function updateTime() {{
#             // This will trigger a script run every second
#             window.parent.postMessage({{type: 'streamlit:setComponentValue', value: {int(time.time())}}}, '*');
#         }}
#         setInterval(updateTime, 1000);
#         </script>
#         """,
#         unsafe_allow_html=True
#     )
    
#     st.markdown("---")
#     st.caption("Built with Astropy + Plotly + Streamlit — demo by Kuntal.")

# if __name__ == "__main__":
#     main()