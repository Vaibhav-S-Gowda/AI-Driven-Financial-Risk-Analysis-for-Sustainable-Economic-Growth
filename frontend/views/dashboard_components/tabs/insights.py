import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime
import random

from backend.config import SUSTAINABLE_INDICATORS, PLOT_THEME_2D, PLOT_THEME_3D, CLUSTER_COLORS, SCENE_AXIS

def render_insights(esg_df, reg_model, cls_model, clu_model, mc_simulator):
        st.markdown("""
        <h2 style='font-size:1.25rem;font-weight:700;color:#f0f2fa;margin-bottom:0.35rem;'>AI Insights</h2>
        <p style='color:#6b7280;font-size:0.82rem;margin-bottom:2rem;'>
            Model diagnostics, regression performance, and feature-level analysis.
        </p>""", unsafe_allow_html=True)
            try:
            feature_cols = ["loan_amnt", "int_rate", "annual_inc", "dti"]
            available    = [f for f in feature_cols if f in credit_df.columns]
                # BUG FIX: don't slice feature_importances_ by len(available); get correct
            # importance count from the model itself and zip safely
            if hasattr(cls_model, "feature_importances_") and available:
                raw_imps = cls_model.feature_importances_
                # Only take importances up to however many available features we have
                n        = min(len(available), len(raw_imps))
                imps     = raw_imps[:n]
                fi_df    = (
                    pd.DataFrame({"Feature": available[:n], "Importance": imps})
                    .sort_values("Importance", ascending=True)
                )
                fig_fi = px.bar(
                    fi_df, x="Importance", y="Feature", orientation="h",
                    color="Importance",
                    color_continuous_scale=["#1e2030", "#7c6cf0", "#0ecfab"],
                    title="Feature Importance (Classification Model)",
                )
                fig_fi.update_layout(
                    **PLOT_THEME_2D, height=300,
                    showlegend=False, coloraxis_showscale=False,
                )
                st.plotly_chart(fig_fi, use_container_width=True)
                # Financial data regression — 3D scatter
            if fin_df is not None and len(fin_df) > 10:
                num_cols = fin_df.select_dtypes(include=np.number).columns.tolist()[:3]
                if len(num_cols) >= 2:
                    z_col = num_cols[2] if len(num_cols) >= 3 else num_cols[1]
                    fig_reg = go.Figure(go.Scatter3d(
                        x=fin_df[num_cols[0]], y=fin_df[num_cols[1]], z=fin_df[z_col],
                        mode="markers",
                        marker=dict(
                            size=3,
                            color=fin_df[num_cols[1]],
                            colorscale=[
                                [0.0, "#1e2030"], [0.4, "#7c6cf0"],
                                [0.75, "#0ecfab"], [1.0, "#f0f2fa"],
                            ],
                            opacity=0.7, showscale=False,
                        ),
                    ))
                    fig_reg.update_layout(
                        **PLOT_THEME_3D, height=360,
                        scene=dict(
                            bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(title=num_cols[0], **SCENE_AXIS),
                            yaxis=dict(title=num_cols[1], **SCENE_AXIS),
                            zaxis=dict(title=z_col,       **SCENE_AXIS),
                            camera=dict(eye=dict(x=1.5, y=-1.6, z=0.9)),
                        ),
                        title=dict(
                            text=f"3D Scatter: {num_cols[0]} × {num_cols[1]} × {z_col}",
                            font=dict(size=13, color="#f0f2fa"),
                        ),
                        margin=dict(l=0, r=0, t=40, b=0),
                    )
                    st.plotly_chart(fig_reg, use_container_width=True)
        except Exception as ex:
            st.error(f"Error generating insights: {ex}")
            st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
            # Derive model names and metrics from loaded objects
        reg_name  = type(reg_model).__name__
        cls_name  = type(cls_model).__name__
        clu_name  = type(clu_model).__name__
        n_segs    = getattr(clu_model, "n_clusters", len(getattr(clu_model, "cluster_centers_", [])) if hasattr(clu_model, "cluster_centers_") else "?")
            # Compute R² on financial data if available
        try:
            if fin_df is not None and len(fin_df) > 10:
                num_fin = fin_df.select_dtypes(include=np.number).dropna()
                if len(num_fin.columns) >= 2:
                    from sklearn.metrics import r2_score
                    y_true = num_fin.iloc[:, -1].values
                    y_pred = reg_model.predict(num_fin.iloc[:, :-1]) if hasattr(reg_model, "predict") else None
                    r2_val = f"{r2_score(y_true, y_pred):.2f}" if y_pred is not None and len(y_pred) == len(y_true) else "N/A"
                else:
                    r2_val = "N/A"
            else:
                r2_val = "N/A"
        except Exception:
            r2_val = "N/A"
            # Compute AUC on credit data
        try:
            from sklearn.metrics import roc_auc_score
            feat_cols = ["loan_amnt", "int_rate", "annual_inc", "dti"]
            avail     = [c for c in feat_cols if c in credit_df.columns]
            if avail and "loan_status" in credit_df.columns:
                sample_c  = credit_df[avail + ["loan_status"]].dropna().sample(min(3000, len(credit_df)), random_state=42)
                X_auc     = processor.preprocess_credit_risk(sample_c.drop(columns=["loan_status"]), training=False)
                y_auc     = sample_c["loan_status"].values
                proba_auc = cls_model.predict_proba(X_auc)[:, 1]
                auc_val   = f"{roc_auc_score(y_auc, proba_auc):.2f}"
            else:
                auc_val = "N/A"
        except Exception:
            auc_val = "N/A"
            ia, ib, ic = st.columns(3, gap="medium")
        with ia:
            st.markdown(f"""<div class='saas-card'>
                <div style='font-size:0.72rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.4rem;'>Regression Model</div>
                <div style='font-size:1.4rem;font-weight:700;color:#f0f2fa;font-family:Outfit,sans-serif;'>{reg_name}</div>
                <div style='font-size:0.78rem;color:#0ecfab;margin-top:4px;font-weight:500;'>R² = {r2_val}</div>
            </div>""", unsafe_allow_html=True)
        with ib:
            st.markdown(f"""<div class='saas-card'>
                <div style='font-size:0.72rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.4rem;'>Classification</div>
                <div style='font-size:1.4rem;font-weight:700;color:#f0f2fa;font-family:Outfit,sans-serif;'>{cls_name}</div>
                <div style='font-size:0.78rem;color:#0ecfab;margin-top:4px;font-weight:500;'>AUC = {auc_val}</div>
            </div>""", unsafe_allow_html=True)
        with ic:
            st.markdown(f"""<div class='saas-card'>
                <div style='font-size:0.72rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.4rem;'>Clustering</div>
                <div style='font-size:1.4rem;font-weight:700;color:#f0f2fa;font-family:Outfit,sans-serif;'>{clu_name}</div>
                <div style='font-size:0.78rem;color:#fbbf24;margin-top:4px;font-weight:500;'>{n_segs} Segments</div>
            </div>""", unsafe_allow_html=True)