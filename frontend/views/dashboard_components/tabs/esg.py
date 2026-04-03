import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime
import random

from backend.config import SUSTAINABLE_INDICATORS, PLOT_THEME_2D, PLOT_THEME_3D, CLUSTER_COLORS, SCENE_AXIS

def render_esg(esg_df):
        st.markdown("""
        <h2 style='font-size:1.25rem;font-weight:700;color:#f0f2fa;margin-bottom:0.35rem;'>ESG Intelligence</h2>
        <p style='color:#6b7280;font-size:0.82rem;margin-bottom:2rem;'>
            Macroeconomic and sustainability indicators across 214 economies.
        </p>""", unsafe_allow_html=True)
            countries = sorted(esg_df["Country name"].unique()) if "Country name" in esg_df.columns else []
        col_a, col_b = st.columns([1, 2])
        with col_a:
            selected_country   = st.selectbox("Select Country", countries)
            selected_indicator = st.selectbox("Select Indicator", SUSTAINABLE_INDICATORS)
        with col_b:
            if countries:
                filtered = esg_df[
                    (esg_df["Country name"] == selected_country)
                    & (esg_df["Indicator name"] == selected_indicator)
                ]
                if not filtered.empty:
                    # BUG FIX: stricter year column filter (4-digit numeric string)
                    year_cols = [
                        c for c in filtered.columns
                        if c.isdigit() and len(c) == 4 and 1960 <= int(c) <= 2100
                    ]
                    if year_cols:
                        ts = filtered[year_cols].iloc[0].dropna()
                        ts.index = ts.index.astype(int)
                        fig_esg = go.Figure()
                        fig_esg.add_trace(go.Scatter(
                            x=ts.index, y=ts.values,
                            mode="lines+markers",
                            line=dict(color="#0ecfab", width=2.5),
                            marker=dict(size=5, color="#0ecfab"),
                            fill="tozeroy",
                            fillcolor="rgba(14,207,171,0.06)",
                        ))
                        fig_esg.update_layout(
                            **PLOT_THEME_2D, height=340,
                            title=dict(
                                text=f"{selected_indicator} — {selected_country}",
                                font=dict(size=13, color="#f0f2fa"),
                            ),
                        )
                        st.plotly_chart(fig_esg, use_container_width=True)
                    else:
                        st.info("No year data available for this selection.")
                else:
                    st.info("No data for this country / indicator combination.")
    