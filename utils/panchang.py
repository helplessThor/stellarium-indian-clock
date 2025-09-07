# utils/panchang.py

import streamlit as st

def display_panchang_details(
    current_dt,
    location,
    tz_offset,
    sunrise_time_utc,
    ghati,
    muhurta,
    yama,
):
    """
    Display Panchang details for the given datetime and location.

    Arguments:
    current_dt -- current datetime (local)
    location -- astropy EarthLocation object
    tz_offset -- float, local timezone offset from UTC
    sunrise_time_utc -- astropy Time object for sunrise UTC
    ghati, muhurta, yama -- ancient time units
    """
    st.subheader("Today's Panchang Details")

    # Basic
    st.write(f"Date: {current_dt.strftime('%Y-%m-%d')}")
    st.write(f"Location: {location.lat:.2f}° N, {location.lon:.2f}° E")
    st.write(f"Timezone Offset (UTC): {tz_offset:+.2f} hours")
    st.write(f"Sunrise (UTC): {sunrise_time_utc.utc.datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    # st.write(f"{ghati:.3f} ghaṭi — {muhurta:.3f} muhūrta — {yama:.3f} yāma")

    # Panchang elements (basic demo logic, can be replaced with real calculations/API)
    # Actual Panchang: tithi, nakshatra, yoga, karana, vaar (weekday)
    # Here we use placeholders and basic weekday
    tithi = "Dashami"
    nakshatra = "Rohini"
    yoga = "Siddha Yoga"
    karana = "Balava"
    vaar = current_dt.strftime("%A")

    st.write(f"**Tithi:** {tithi}")
    st.write(f"**Nakshatra:** {nakshatra}")
    st.write(f"**Yoga:** {yoga}")
    st.write(f"**Karana:** {karana}")
    st.write(f"**Vaar (Weekday):** {vaar}")

    st.info("Note: Panchang details above are demo values. For actual Panchang, integrate API or calculation for Tithi, Nakshatra, Yoga, Karana, and Vaar.")