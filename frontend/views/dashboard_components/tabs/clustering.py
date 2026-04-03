import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime
import random

from backend.config import SUSTAINABLE_INDICATORS, PLOT_THEME_2D, PLOT_THEME_3D, CLUSTER_COLORS, SCENE_AXIS

def render_clustering(esg_df, clu_model, clu_scaler):
        st.markdown("""
        <h2 style='font-size:1.25rem;font-weight:700;color:#f0f2fa;margin-bottom:0.35rem;'>Behavioral Clustering Lab</h2>
        <p style='color:#6b7280;font-size:0.82rem;margin-bottom:2rem;'>
            K-Means segmentation to discover hidden borrower cohorts.
        </p>""", unsafe_allow_html=True)
            try:
            cluster_features = ["loan_amnt", "int_rate", "annual_inc", "dti"]
            available        = [f for f in cluster_features if f in credit_df.columns]
                if len(available) >= 2:
                sample_size = min(2000, len(credit_df))
                sample_df   = credit_df[available].dropna().sample(sample_size, random_state=42)
                    # BUG FIX: wrap scaler transform in try/except with shape validation
                try:
                    X_clu    = clu_scaler.transform(sample_df[available])
                    clusters = clu_model.predict(X_clu)
                except Exception as ex:
                    st.error(f"Scaler/model shape mismatch — ensure the clustering model was trained on these features: {ex}")
                    st.stop()
                    sample_df            = sample_df.copy()
                sample_df["Cluster"] = clusters.astype(str)
                    col_p, col_q = st.columns(2, gap="large")
                z_col = available[2] if len(available) >= 3 else available[1]
                    with col_p:
                    fig_scatter = go.Figure()
                    for i, cl in enumerate(sorted(sample_df["Cluster"].unique())):
                        df_cl = sample_df[sample_df["Cluster"] == cl]
                        fig_scatter.add_trace(go.Scatter3d(
                            x=df_cl[available[0]], y=df_cl[available[1]], z=df_cl[z_col],
                            mode="markers", name=f"Cluster {cl}",
                            marker=dict(size=2.5, color=CLUSTER_COLORS[i % len(CLUSTER_COLORS)],
                                        opacity=0.75, line=dict(width=0)),
                        ))
                    fig_scatter.update_layout(
                        **PLOT_THEME_3D, height=400,
                        scene=dict(
                            bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(title=available[0], **SCENE_AXIS),
                            yaxis=dict(title=available[1], **SCENE_AXIS),
                            zaxis=dict(title=z_col,        **SCENE_AXIS),
                            camera=dict(eye=dict(x=1.5, y=-1.5, z=0.8)),
                        ),
                        legend=dict(font=dict(color="#a0a8c0"), bgcolor="rgba(0,0,0,0)"),
                        title=dict(text="3D Cluster Scatter", font=dict(size=13, color="#f0f2fa")),
                        margin=dict(l=0, r=0, t=40, b=0),
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)
                    with col_q:
                    cluster_counts         = sample_df["Cluster"].value_counts().reset_index()
                    cluster_counts.columns = ["Cluster", "Count"]
                    cl_labels = cluster_counts["Cluster"].tolist()
                    cl_counts  = cluster_counts["Count"].tolist()
                        fig_bar = go.Figure()
                    for i, (lbl, cnt) in enumerate(zip(cl_labels, cl_counts)):
                        col_hex = CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
                        fig_bar.add_trace(go.Scatter3d(
                            x=[i, i], y=[0, 0], z=[0, cnt],
                            mode="lines", name=f"Cluster {lbl}",
                            line=dict(color=col_hex, width=16), showlegend=True,
                        ))
                        fig_bar.add_trace(go.Scatter3d(
                            x=[i], y=[0], z=[cnt], mode="markers",
                            marker=dict(size=8, color=col_hex, symbol="circle", opacity=0.9),
                            showlegend=False,
                        ))
                    fig_bar.update_layout(
                        **PLOT_THEME_3D, height=400,
                        scene=dict(
                            bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(title="Cluster",
                                       tickvals=list(range(len(cl_labels))),
                                       ticktext=cl_labels, **SCENE_AXIS),
                            yaxis=dict(showticklabels=False, **SCENE_AXIS),
                            zaxis=dict(title="Count", **SCENE_AXIS),
                            camera=dict(eye=dict(x=1.8, y=-0.8, z=1.0)),
                        ),
                        legend=dict(font=dict(color="#a0a8c0"), bgcolor="rgba(0,0,0,0)"),
                        title=dict(text="3D Segment Sizes", font=dict(size=13, color="#f0f2fa")),
                        margin=dict(l=0, r=0, t=40, b=0),
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
                cluster_summary = sample_df.groupby("Cluster")[available].mean().round(2)
                st.markdown("<div style='font-family:Outfit,sans-serif;font-weight:700;font-size:0.9rem;color:#f0f2fa;margin-bottom:0.8rem;'>Cluster Summary Statistics</div>", unsafe_allow_html=True)
                st.dataframe(cluster_summary, use_container_width=True)
            else:
                st.warning("Insufficient numeric features for clustering.")
        except Exception as ex:
            st.error(f"Clustering error: {ex}")
    