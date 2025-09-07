# utils/plots.py
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from .helpers import altaz_to_unit_vector, make_dome_mesh, ring_points_alt, meridian_points_az

def create_3d_planetarium(stars_df, show_grid, show_only_visible):
    # Filter if only visible
    plot_df = stars_df.copy()
    if show_only_visible:
        plot_df = plot_df[plot_df["visible"]].reset_index(drop=True)

    # Convert to unit sphere coords
    xs, ys, zs = altaz_to_unit_vector(plot_df["alt_deg"].values, plot_df["az_deg"].values)

    # Marker sizes: brighter = larger
    sizes = np.clip(14 - plot_df["mag"].astype(float), 4, 18)
    # Colors: above horizon = bright yellow; below = steelblue (faded)
    colors = np.where(plot_df["alt_deg"].values > 0, "yellow", "lightsteelblue")

    # Dome mesh (translucent)
    X, Y, Z = make_dome_mesh(radius=1.0, n_theta=60, n_phi=40)
    surface = go.Surface(
        x=X, y=Y, z=Z,
        opacity=0.08 if show_grid else 0.0,
        showscale=False,
        hoverinfo="skip",
    )

    fig3d = go.Figure(surface)
    
    hx, hy, hz = ring_points_alt(0.0, radius=1.0, n=361)

    hx = np.atleast_1d(hx)
    hy = np.atleast_1d(hy)
    hz = np.atleast_1d(hz)

    fig3d.add_trace(go.Scatter3d(
        x=hx, y=hy, z=hz,
        mode="markers",
        marker=dict(size=3, color="white"),
        hoverinfo="skip"
    ))

    # Optional grid: altitude rings + meridians
    if show_grid:
        for alt_g in [15, 30, 45, 60, 75]:
            gx, gy, gz = ring_points_alt(alt_g, radius=1.0, n=361)

            gx = np.atleast_1d(gx)
            gy = np.atleast_1d(gy)
            gz = np.atleast_1d(gz)

            fig3d.add_trace(go.Scatter3d(
                x=gx, y=gy, z=gz, mode="lines",
                line=dict(width=1),
                hoverinfo="skip",
                showlegend=False
            ))
        for az_g in range(0, 360, 30):
            mx, my, mz = meridian_points_az(az_g, radius=1.0, n=91)
            mx = np.atleast_1d(mx)
            my = np.atleast_1d(my)
            mz = np.atleast_1d(mz)

            fig3d.add_trace(go.Scatter3d(
                x=mx, y=my, z=mz, mode="lines",
                line=dict(width=1),
                hoverinfo="skip",
                showlegend=False
            ))

    # Stars layer
    fig3d.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="markers+text",
        marker=dict(size=sizes, color=colors, opacity=0.95),
        text=[n if (m < 1.4 and a > 5) else "" for n, m, a in zip(plot_df["name"], plot_df["mag"], plot_df["alt_deg"])],
        textposition="top center",
        hovertext=[
            f"{n}<br>RA: {ra:.3f} h, Dec: {dc:.2f}°<br>Alt: {al:.2f}°, Az: {az:.2f}°"
            for n, ra, dc, al, az in zip(plot_df["name"], plot_df["ra_h"], plot_df["dec_deg"], plot_df["alt_deg"], plot_df["az_deg"])
        ],
        hoverinfo="text",
        showlegend=False
    ))

    # Axes off, equal aspect; camera slightly above horizon
    fig3d.update_scenes(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode="data"
    )

    # Cardinal directions on horizon (Alt=0 plane, radius=1)
    cardinal_points = [
        {"az": 0, "label": "N"},
        {"az": 90, "label": "E"},
        {"az": 180, "label": "S"},
        {"az": 270, "label": "W"},
    ]

    cx, cy, cz, labels = [], [], [], []
    for p in cardinal_points:
        az_rad = np.deg2rad(p["az"])
        cx.append(np.cos(0) * np.sin(az_rad))  # x
        cy.append(np.cos(0) * np.cos(az_rad))  # y
        cz.append(np.sin(0))                   # z = 0
        labels.append(p["label"])

    fig3d.add_trace(go.Scatter3d(
        x=cx, y=cy, z=cz,
        mode="text",
        text=labels,
        textfont=dict(size=16, color="red"),
        hoverinfo="skip",
        showlegend=False
    ))

    # Zenith and Nadir
    fig3d.add_trace(go.Scatter3d(
        x=[0, 0],
        y=[0, 0],
        z=[1, -1],
        mode="text",
        text=["Zenith", "Nadir"],
        textfont=dict(size=14, color="orange"),
        hoverinfo="skip",
        showlegend=False
    ))

    fig3d.update_layout(
        height=720,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="black",
        plot_bgcolor="black",
        scene_camera=dict(eye=dict(x=1.5, y=1.2, z=0.8))
    )
    
    return fig3d

def create_2d_altaz_chart(stars_df, show_grid, show_only_visible):
    plot_df = stars_df.copy()
    if show_only_visible:
        plot_df = plot_df[plot_df["visible"]].reset_index(drop=True)

    fig2d = go.Figure()

    if show_grid:
        for a in range(0, 360, 30):
            fig2d.add_trace(go.Scatter(
                x=[a, a], y=[-90, 90], mode="lines",
                line=dict(width=0.6), showlegend=False, hoverinfo="skip"
            ))
        for alt_g in [-60, -30, 0, 30, 60]:
            fig2d.add_trace(go.Scatter(
                x=[0, 360], y=[alt_g, alt_g], mode="lines",
                line=dict(width=0.6), showlegend=False, hoverinfo="skip"
            ))

    sizes2d = np.clip(14 - plot_df["mag"].astype(float), 4, 18)
    colors2d = np.where(plot_df["alt_deg"].values > 0, "yellow", "lightsteelblue")

    fig2d.add_trace(go.Scatter(
        x=plot_df["az_deg"], y=plot_df["alt_deg"],
        mode="markers+text",
        marker=dict(size=sizes2d, color=colors2d, opacity=0.95, line=dict(width=0.5)),
        text=[n if (m < 1.4 and a > 5) else "" for n, m, a in zip(plot_df["name"], plot_df["mag"], plot_df["alt_deg"])],
        textposition="top center",
        hovertext=[
            f"{n}<br>RA: {ra:.3f} h, Dec: {dc:.2f}°<br>Alt: {al:.2f}°, Az: {az:.2f}°"
            for n, ra, dc, al, az in zip(plot_df["name"], plot_df["ra_h"], plot_df["dec_deg"], plot_df["alt_deg"], plot_df["az_deg"])
        ],
        hoverinfo="text",
        showlegend=False
    ))

    # Cardinal directions (N, E, S, W)
    cardinal_points = [
        {"az": 0, "alt": -5, "label": "N"},
        {"az": 90, "alt": -5, "label": "E"},
        {"az": 180, "alt": -5, "label": "S"},
        {"az": 270, "alt": -5, "label": "W"},
    ]
    fig2d.add_trace(go.Scatter(
        x=[p["az"] for p in cardinal_points],
        y=[p["alt"] for p in cardinal_points],
        mode="text",
        text=[p["label"] for p in cardinal_points],
        textfont=dict(size=16, color="red"),
        showlegend=False,
        hoverinfo="skip"
    ))

    # Zenith (top) and Nadir (bottom)
    fig2d.add_trace(go.Scatter(
        x=[180, 180],
        y=[90, -90],
        mode="text",
        text=["Zenith", "Nadir"],
        textfont=dict(size=14, color="orange"),
        showlegend=False,
        hoverinfo="skip"
    ))

    fig2d.update_layout(
        xaxis=dict(title="Azimuth (°) — 0° = North, increases East", range=[0, 360]),
        yaxis=dict(title="Altitude (°)", range=[-90, 90]),
        height=720,
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(color="white"),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    
    return fig2d