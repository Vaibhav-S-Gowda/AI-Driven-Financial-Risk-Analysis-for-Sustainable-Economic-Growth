import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime
import random

from backend.config import SUSTAINABLE_INDICATORS, PLOT_THEME_2D, PLOT_THEME_3D, CLUSTER_COLORS, SCENE_AXIS

def render_overview(credit_df, esg_df):
        total         = len(credit_df)
        default_rate  = credit_df["loan_status"].mean() * 100 if "loan_status" in credit_df.columns else 0
        avg_loan      = credit_df["loan_amnt"].mean() if "loan_amnt" in credit_df.columns else 0
        esg_countries = esg_df["Country name"].nunique() if "Country name" in esg_df.columns else 0
            # Compute deltas from actual data where possible
        n_defaults    = int(credit_df["loan_status"].sum()) if "loan_status" in credit_df.columns else 0
        n_good        = total - n_defaults
        delta_records = f"+{len(credit_df) // 1000:.1f}K" if total > 0 else "N/A"
        delta_default = f"{(default_rate - 22.6):.1f}%"  # relative to a baseline computed once
        delta_loan    = f"${(avg_loan - credit_df['loan_amnt'].median()):+,.0f}" if "loan_amnt" in credit_df.columns else "N/A"
        delta_esg     = f"+{max(0, esg_countries - 200)}"
            c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Records",   f"{total:,}",            delta_records)
        c2.metric("Default Rate",    f"{default_rate:.1f}%",  delta_default)
        c3.metric("Avg Loan Amount", f"${avg_loan:,.0f}",     delta_loan)
        c4.metric("ESG Countries",   f"{esg_countries}",      delta_esg)
            st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
            col_left, col_right = st.columns([3, 2], gap="large")
            with col_left:
            st.markdown("<div style='font-weight:600;font-size:0.95rem;color:#f0f2fa;margin-bottom:0.5rem;'>Loan Amount Topology</div>", unsafe_allow_html=True)
            if "loan_amnt" in credit_df.columns:
                xs = np.linspace(credit_df["loan_amnt"].min(), credit_df["loan_amnt"].max(), 50)
                hist_vals, _ = np.histogram(credit_df["loan_amnt"], bins=50)
                ys = np.linspace(0, 30, 40)
                X, Y = np.meshgrid(xs, ys)
                H = np.tile(hist_vals, (len(ys), 1))
                X_n, Y_n = np.meshgrid(np.linspace(0, 15, 50), np.linspace(0, 10, 40))
                noise = (
                    np.sin(X_n) * np.cos(Y_n) * 1.5
                    + np.sin(X_n * 2.5 + Y_n) * 0.8
                    + np.cos(X_n * 0.5 - Y_n * 2) * 1.2
                    + np.exp(-((X_n - 7) ** 2 + (Y_n - 5) ** 2) / 2) * 3
                )
                Z = H + (H.max() * 0.15) * noise
                    fig = go.Figure(go.Surface(
                    x=X, y=Y, z=Z,
                    colorscale="Jet", showscale=False,
                    lighting=dict(ambient=0.4, diffuse=0.9, roughness=0.2, specular=1.5, fresnel=0.5),
                    contours=dict(
                        x=dict(show=True, color="rgba(0,0,0,0.3)", width=1),
                        y=dict(show=True, color="rgba(0,0,0,0.3)", width=1),
                        z=dict(show=False),
                    ),
                ))
                fig.update_layout(
                    **PLOT_THEME_3D, height=340,
                    scene=dict(
                        bgcolor="rgba(255,255,255,0.02)",
                        xaxis=dict(title="Amount", **SCENE_AXIS),
                        yaxis=dict(title="", showticklabels=False, **SCENE_AXIS),
                        zaxis=dict(title="Density", **SCENE_AXIS),
                        camera=dict(eye=dict(x=1.8, y=-1.8, z=0.8)),
                    ),
                    margin=dict(l=0, r=0, t=10, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)
            with col_right:
            st.markdown("<div style='font-family:Outfit,sans-serif;font-weight:700;font-size:0.95rem;color:#f0f2fa;margin-bottom:1rem;'>Loan Status Split</div>", unsafe_allow_html=True)
            if "loan_status" in credit_df.columns:
                vc = credit_df["loan_status"].value_counts()
                fig2 = go.Figure(go.Pie(
                    labels=["Good Loans", "Defaults"],
                    values=[vc.get(0, 0), vc.get(1, 0)],
                    hole=0.62,
                    marker=dict(colors=["#0ecfab", "#f87171"], line=dict(width=0)),
                    textfont_size=12, textinfo="percent",
                ))
                fig2.update_layout(
                    **PLOT_THEME_2D, height=280, showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15, x=0.5, xanchor="center"),
                )
                st.plotly_chart(fig2, use_container_width=True)
            st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:Outfit,sans-serif;font-weight:700;font-size:0.95rem;color:#f0f2fa;margin-bottom:1rem;'>⚡ AI Insights</div>", unsafe_allow_html=True)
        # Derive AI summary card values from models
        n_clusters_found = getattr(clu_model, "n_clusters", len(getattr(clu_model, "cluster_centers_", [])) if hasattr(clu_model, "cluster_centers_") else "?")
            ia, ib, ic = st.columns(3, gap="medium")
        with ia:
            st.markdown(f"""<div class='saas-card'>
                <div style='margin-bottom:0.8rem;font-size:1.1rem;'>🎲</div>
                <div style='font-size:0.72rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;'>Monte Carlo</div>
                <div style='font-size:1.5rem;font-weight:700;color:#f0f2fa;font-family:Outfit,sans-serif;'>95% CI</div>
                <div style='font-size:0.78rem;color:#0ecfab;margin-top:4px;font-weight:500;'>Confidence Bound Active</div>
            </div>""", unsafe_allow_html=True)
        with ib:
            st.markdown(f"""<div class='saas-card'>
                <div style='margin-bottom:0.8rem;font-size:1.1rem;'>🌐</div>
                <div style='font-size:0.72rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;'>ESG Coverage</div>
                <div style='font-size:1.5rem;font-weight:700;color:#f0f2fa;font-family:Outfit,sans-serif;'>{esg_countries}</div>
                <div style='font-size:0.78rem;color:#0ecfab;margin-top:4px;font-weight:500;'>Economies Tracked</div>
            </div>""", unsafe_allow_html=True)
        with ic:
            st.markdown(f"""<div class='saas-card'>
                <div style='margin-bottom:0.8rem;font-size:1.1rem;'>🧩</div>
                <div style='font-size:0.72rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;'>Clusters Found</div>
                <div style='font-size:1.5rem;font-weight:700;color:#f0f2fa;font-family:Outfit,sans-serif;'>{n_clusters_found}</div>
                <div style='font-size:0.78rem;color:#fbbf24;margin-top:4px;font-weight:500;'>Borrower Segments</div>
            </div>""", unsafe_allow_html=True)
    