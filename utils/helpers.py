# utils/helpers.py
import numpy as np
from datetime import datetime, timedelta
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord, AltAz, get_sun
import astropy.units as u
import pandas as pd

def to_earthlocation(lat_deg: float, lon_deg: float, height_m: float) -> EarthLocation:
    return EarthLocation(lat=lat_deg * u.deg, lon=lon_deg * u.deg, height=height_m * u.m)

def time_from_local_localdt(local_dt: datetime, tz_offset_hours: float) -> Time:
    """Convert naive local datetime + tz offset to astropy Time (UTC)."""
    utc_dt = local_dt - timedelta(hours=tz_offset_hours)
    return Time(utc_dt, scale="utc")

def local_sidereal_time_hours(astropy_time: Time, lon_deg: float) -> float:
    lst = astropy_time.sidereal_time(kind="apparent", longitude=lon_deg * u.deg)
    return lst.to(u.hourangle).value

def approximate_sunrise_utc_for_local_date(
    local_date: datetime.date,
    location: EarthLocation,
    tz_offset_hours: float,
    step_minutes: int = 10
) -> Time:
    """Approx sunrise by upward crossing of Sun altitude through −0.833°."""
    from datetime import time as dtime
    local_midnight = datetime.combine(local_date, dtime(0, 0, 0))
    start_utc_dt = local_midnight - timedelta(hours=tz_offset_hours)

    minutes_in_day = 24 * 60
    n_steps = minutes_in_day // step_minutes + 1
    times_list = [start_utc_dt + timedelta(minutes=step_minutes * i) for i in range(int(n_steps))]
    times = Time(times_list, scale="utc")

    aa = AltAz(obstime=times, location=location)
    suncoords = get_sun(times).transform_to(aa)
    alt_vals = suncoords.alt.degree
    target = -0.833

    for i in range(len(alt_vals) - 1):
        if (alt_vals[i] < target) and (alt_vals[i + 1] >= target):
            a0 = alt_vals[i]
            a1 = alt_vals[i + 1]
            frac = (target - a0) / (a1 - a0) if (a1 != a0) else 0.0
            return Time(times[i].jd + frac * (times[i + 1].jd - times[i].jd), format="jd", scale="utc")
    return Time(start_utc_dt, scale="utc")

def find_time_for_lst(target_lst_hours: float, approx_time_utc: Time, lon_deg: float) -> Time:
    """Find UTC Time such that LST(longitude) ≈ target. Bisection within ±12 h."""
    def f(t: Time):
        lst_val = t.sidereal_time(kind="apparent", longitude=lon_deg * u.deg).to(u.hourangle).value
        return (lst_val - target_lst_hours + 12) % 24 - 12  # wrap to [-12, 12)

    left = approx_time_utc - 12 * u.hour
    right = approx_time_utc + 12 * u.hour
    fl = f(left)
    fr = f(right)
    for _ in range(8):
        if fl * fr <= 0:
            break
        left -= 6 * u.hour
        right += 6 * u.hour
        fl = f(left)
        fr = f(right)
    if fl * fr > 0:
        return approx_time_utc

    for _ in range(60):
        mid = Time((left.jd + right.jd) / 2.0, format="jd", scale="utc")
        fm = f(mid)
        if abs(fm) < 1e-7:
            return mid
        if fl * fm <= 0:
            right = mid
            fr = fm
        else:
            left = mid
            fl = fm
    return Time((left.jd + right.jd) / 2.0, format="jd", scale="utc")

def solve_time_from_altaz(
    target_alt_deg: float,
    target_az_deg: float,
    ra_h: float,
    dec_deg: float,
    approx_time_utc: Time,
    location: EarthLocation
):
    """
    Given target Alt/Az and star RA/Dec, find UTC time that best matches around approx_time_utc.
    Ternary search on JD within ±12 h. Returns (Time, error_deg).
    """
    def error_at_jd(jd_val):
        t = Time(jd_val, format="jd", scale="utc")
        aa = AltAz(obstime=t, location=location)
        sc = SkyCoord(ra=ra_h * u.hourangle, dec=dec_deg * u.deg)
        altaz = sc.transform_to(aa)
        alt = altaz.alt.degree
        az = altaz.az.degree
        da = alt - target_alt_deg
        dz = (az - target_az_deg + 180) % 360 - 180
        return float(np.hypot(da, dz))

    a = (approx_time_utc - 12 * u.hour).jd
    b = (approx_time_utc + 12 * u.hour).jd
    for _ in range(80):
        m1 = a + (b - a) / 3.0
        m2 = a + 2.0 * (b - a) / 3.0
        f1 = error_at_jd(m1)
        f2 = error_at_jd(m2)
        if f1 < f2:
            b = m2
        else:
            a = m1
    best = 0.5 * (a + b)
    return Time(best, format="jd", scale="utc"), error_at_jd(best)

def altaz_to_unit_vector(alt_deg: float, az_deg: float):
    """
    Convert Alt/Az to ENU unit vector:
      x = East, y = North, z = Up
      az: 0° = North, 90° = East; alt from horizon (+ up)
    """
    alt = np.radians(alt_deg)
    az = np.radians(az_deg)
    x = np.cos(alt) * np.sin(az)  # East
    y = np.cos(alt) * np.cos(az)  # North
    z = np.sin(alt)               # Up
    return x, y, z

def make_dome_mesh(radius=1.0, n_theta=40, n_phi=40):
    """
    Create a translucent hemisphere mesh (z >= 0).
    theta: 0..2π (azimuth), phi: 0..π/2 (from zenith to horizon)
    """
    theta = np.linspace(0, 2*np.pi, n_theta)
    phi = np.linspace(0, np.pi/2, n_phi)
    theta, phi = np.meshgrid(theta, phi)
    # Spherical to ENU: zenith angle = phi, so alt = 90° - zenith = π/2 - phi
    x = radius * np.sin(phi) * np.sin(theta)  # East
    y = radius * np.sin(phi) * np.cos(theta)  # North
    z = radius * np.cos(phi)                  # Up
    return x, y, z

def ring_points_alt(alt_deg, radius=1.0, n=181):
    """Points on a constant-altitude ring on the dome."""
    az = np.linspace(0, 360, n)
    x, y, z = altaz_to_unit_vector(alt_deg, az)
    return x*radius, y*radius, z*radius

def meridian_points_az(az_deg, radius=1.0, n=91):
    """Meridian half-great-circle for a constant azimuth (from horizon to zenith)."""
    alt = np.linspace(0, 90, n)
    x, y, z = altaz_to_unit_vector(alt, np.full_like(alt, az_deg))
    return x*radius, y*radius, z*radius

def compute_stars_positions_for_time(astropy_time: Time, location: EarthLocation, base_stars_df: pd.DataFrame) -> pd.DataFrame:
    """Compute alt/az for each star at the given astropy Time & EarthLocation."""
    aa = AltAz(obstime=astropy_time, location=location)
    rows = []
    for _, r in base_stars_df.iterrows():
        sc = SkyCoord(ra=(r["ra_h"] * u.hourangle), dec=(r["dec_deg"] * u.deg), frame="icrs")
        altaz = sc.transform_to(aa)
        rows.append({
            "name": r["name"],
            "ra_h": float(r["ra_h"]),
            "dec_deg": float(r["dec_deg"]),
            "mag": float(r["mag"]),
            "alt_deg": float(altaz.alt.to_value(u.deg)),
            "az_deg": float(altaz.az.to_value(u.deg)),
            "visible": bool(altaz.alt.degree > 0.0)
        })
    df = pd.DataFrame(rows)
    df["az_deg"] = np.mod(df["az_deg"].astype(float), 360.0)
    df["alt_deg"] = df["alt_deg"].astype(float).clip(-90.0, 90.0)
    return df