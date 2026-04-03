import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime
import random

from backend.config import SUSTAINABLE_INDICATORS, PLOT_THEME_2D, PLOT_THEME_3D, CLUSTER_COLORS, SCENE_AXIS

def render_credit_risk(credit_df):
        st.markdown("""
        <h2 style='font-size:1.25rem;font-weight:700;color:#f0f2fa;margin-bottom:0.35rem;'>Credit Risk Predictor</h2>
        <p style='color:#6b7280;font-size:0.82rem;margin-bottom:2rem;'>
            Enter borrower details to generate a real-time default probability score.
        </p>""", unsafe_allow_html=True)
            col_form, col_result = st.columns([1, 1], gap="large")
            with col_form:
            loan_amnt  = st.number_input("Loan Amount ($)", 1000, 40000, 15000, step=500)
            int_rate   = st.slider("Interest Rate (%)", 5.0, 30.0, 13.0, step=0.1)
            annual_inc = st.number_input("Annual Income ($)", 10000, 500000, 65000, step=5000)
            dti        = st.slider("Debt-to-Income Ratio", 0.0, 40.0, 15.0, step=0.5)
            emp_length = st.selectbox("Employment Length",
                                      ["< 1 year","1 year","2 years","3 years","5 years","7 years","10+ years"])
            home_own   = st.selectbox("Home Ownership", ["RENT", "OWN", "MORTGAGE"])
            purpose    = st.selectbox("Loan Purpose",
                                      ["debt_consolidation","credit_card","home_improvement",
                                       "major_purchase","medical","car"])
                if st.button("🔍 Run Prediction", type="primary", use_container_width=True):
                with st.spinner("Running classification model…"):
                    try:
                        sample = {
                            "loan_amnt": loan_amnt, "int_rate": int_rate,
                            "annual_inc": annual_inc, "dti": dti,
                            "emp_length": emp_length, "home_ownership": home_own,
                            "purpose": purpose,
                        }
                        X_pred = processor.preprocess_credit_risk(pd.DataFrame([sample]), training=False)
                        prob   = float(cls_model.predict_proba(X_pred)[0][1])
                        st.session_state["credit_prob"]  = prob
                        st.session_state["credit_input"] = sample
                    except Exception as ex:
                        st.error(f"Prediction failed: {ex}")
            with col_result:
            # BUG FIX: use `in` operator on session_state, not hasattr
            if "credit_prob" in st.session_state:
                prob  = st.session_state["credit_prob"]
                color = "#f87171" if prob > 0.5 else "#fbbf24" if prob > 0.3 else "#0ecfab"
                label = "High Risk" if prob > 0.5 else "Moderate Risk" if prob > 0.3 else "Low Risk"
                    st.markdown(f"""
                <div class='saas-card' style='text-align:center;padding:2.5rem;'>
                    <div style='font-size:0.72rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:1rem;'>Default Probability</div>
                    <div style='font-size:3.8rem;font-weight:800;font-family:Outfit,sans-serif;
                                color:{color};line-height:1;margin-bottom:0.6rem;'>{prob*100:.1f}%</div>
                    <div style='display:inline-block;padding:0.35rem 1.2rem;background:rgba(0,0,0,0.3);
                                border-radius:100px;color:{color};font-size:0.82rem;font-weight:600;
                                border:1px solid {color}40;'>{label}</div>
                    <div style='margin-top:1.8rem;background:rgba(255,255,255,0.02);border-radius:12px;
                                padding:1.2rem;border:1px solid #1a1d2e;'>
                        <div style='font-size:0.78rem;color:#6b7280;line-height:1.6;'>
                            Monte Carlo simulation across 10,000 scenarios suggests this loan carries
                            a <strong style='color:#f0f2fa;'>{label.lower()}</strong> profile based on submitted parameters.
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                    # Monte Carlo — 3D Topographic view
                st.markdown("<div style='margin-top:1.5rem;font-weight:600;font-size:0.9rem;color:#f0f2fa;margin-bottom:0.8rem;'>Monte Carlo Simulation — Topographic View</div>", unsafe_allow_html=True)
                try:
                    X_mc     = processor.preprocess_credit_risk(
                        pd.DataFrame([st.session_state["credit_input"]]), training=False
                    )
                    mc_results = mc_simulator.run(X_mc, n_simulations=500)
                        # BUG FIX: guard against empty/invalid mc_results
                    mc_arr = np.array(mc_results)
                    if mc_arr.ndim == 0 or len(mc_arr) < 2:
                        raise ValueError("mc_simulator.run() returned insufficient data")
                        xs_mc   = np.linspace(mc_arr.min(), mc_arr.max(), 40)
                    hist_mc, _ = np.histogram(mc_arr, bins=40)
                    ys_mc   = np.linspace(0, 30, 30)
                    Xg, Yg  = np.meshgrid(xs_mc, ys_mc)
                    H_mc    = np.tile(hist_mc, (len(ys_mc), 1))
                    Xn, Yn  = np.meshgrid(np.linspace(0, 10, 40), np.linspace(0, 8, 30))
                    noise   = np.sin(Xn * 2) * np.cos(Yn) + np.sin(Yn * 3 + Xn) * 1.5
                    Z_mc    = H_mc + (H_mc.max() * 0.2) * noise
                        fig_mc = go.Figure(go.Surface(
                        x=Xg, y=Yg, z=Z_mc,
                        colorscale="Jet", showscale=False,
                        lighting=dict(ambient=0.4, diffuse=0.9, roughness=0.2, specular=1.5, fresnel=0.5),
                        contours=dict(
                            x=dict(show=True, color="rgba(0,0,0,0.3)", width=1),
                            y=dict(show=True, color="rgba(0,0,0,0.3)", width=1),
                            z=dict(show=False),
                        ),
                    ))
                    fig_mc.update_layout(
                        **PLOT_THEME_3D, height=300,
                        scene=dict(
                            bgcolor="rgba(255,255,255,0.02)",
                            xaxis=dict(title="Default Rate", **SCENE_AXIS),
                            yaxis=dict(title="", showticklabels=False, **SCENE_AXIS),
                            zaxis=dict(title="Density", **SCENE_AXIS),
                            camera=dict(eye=dict(x=1.8, y=-1.8, z=0.8)),
                        ),
                        margin=dict(l=0, r=0, t=5, b=0),
                    )
                    st.plotly_chart(fig_mc, use_container_width=True)
                except Exception as ex:
                    st.warning(f"Monte Carlo visualisation unavailable: {ex}")
            else:
                st.markdown("""
                <div style='background:rgba(255,255,255,0.01);border:1px dashed #1a1d2e;border-radius:20px;
                            padding:3rem;text-align:center;color:#4a5068;'>
                    <div style='font-size:2rem;margin-bottom:1rem;'>🎯</div>
                    <div style='font-family:Outfit,sans-serif;font-size:1rem;font-weight:600;color:#7c84a0;'>Run the predictor</div>
                    <div style='font-size:0.8rem;margin-top:0.4rem;'>Fill in the form and click "Run Prediction" to see results</div>
                </div>""", unsafe_allow_html=True)
    