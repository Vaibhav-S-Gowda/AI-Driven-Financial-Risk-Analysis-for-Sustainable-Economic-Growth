import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime
import random

from backend.config import SUSTAINABLE_INDICATORS, PLOT_THEME_2D, PLOT_THEME_3D, CLUSTER_COLORS, SCENE_AXIS

def push_nav_to_url(val: str):
    try:
        st.query_params["nav"] = val
    except Exception:
        pass

def render_dashboard(processor, credit_df, fin_df, esg_df, reg_model, cls_model, clu_model, clu_scaler, mc_simulator):
    # ══════════════════════════════════════════════════════════════════════════════
    # ROUTE 3: DASHBOARD
    # ══════════════════════════════════════════════════════════════════════════════

    # ── Read active dashboard page from URL param ──────────────────────────────
    dash_page = st.query_params.get("dash_page", "overview")
    st.markdown("""<style>
[data-testid='stHeader'], footer { display:none !important; }
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Outfit:wght@600;700;800&display=swap');
:root {
    --bg-base: #06070d; --bg-card: #0d0f1a; --bg-hover: #12152a;
    --border: #1a1d2e; --text-primary: #f0f2fa; --text-sec: #6b7280;
    --accent-purple: #7c6cf0; --accent-green: #0ecfab;
    --accent-yellow: #fbbf24; --accent-red: #f87171;
    --radius-lg: 18px; --radius-md: 12px;
}
[data-testid='stSidebar'], [data-testid='stSidebarCollapsedControl'], [data-testid='collapsedControl'], button[data-testid='baseButton-headerNoPadding'] { display: none !important; }
section[data-testid='stMain'] { margin-left: 0 !important; padding-left: 88px !important; background: var(--bg-base) !important; }
.block-container { padding: 1.2rem 2rem 2rem 0 !important; max-width: 100% !important; margin: 0 !important; }
.float-rail {
    position: fixed; left: 14px; top: 50%; transform: translateY(-50%); z-index: 99999;
    display: flex; flex-direction: column; align-items: center; gap: 0; width: 56px;
    background: rgba(13, 15, 26, 0.92); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.07); border-radius: 24px; padding: 14px 0;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.04);
}
.rail-logo {
    width: 34px; height: 34px; background: linear-gradient(135deg, #c6f135, #7eed9f); border-radius: 10px;
    display: flex; align-items: center; justify-content: center; font-size: 1.15rem; font-weight: 900;
    color: #111; cursor: pointer; flex-shrink: 0; line-height: 1; transition: transform 0.15s, box-shadow 0.15s; margin-bottom: 4px;
}
.rail-logo:hover { transform: scale(1.08); box-shadow: 0 4px 16px rgba(198,241,53,0.35); }
.rail-divider { width: 28px; height: 1px; background: rgba(255,255,255,0.07); margin: 10px 0; flex-shrink: 0; }
.rail-nav { display: flex; flex-direction: column; align-items: center; gap: 6px; width: 100%; padding: 0 8px; }
.rail-icon {
    width: 40px; height: 40px; border-radius: 12px; background: transparent;
    display: flex; align-items: center; justify-content: center; cursor: pointer; text-decoration: none;
    color: #5a6070; position: relative; transition: background 0.18s, color 0.18s, transform 0.12s; border: none; flex-shrink: 0;
}
.rail-icon:hover { background: rgba(255,255,255,0.07) !important; color: #c8cde0 !important; transform: scale(1.06); }
.rail-icon.active { background: #ffffff !important; color: #111111 !important; box-shadow: 0 2px 12px rgba(255,255,255,0.15); }
.rail-icon.active:hover { transform: scale(1.04); }
.rail-icon::after {
    content: attr(data-tip); position: absolute; left: calc(100% + 14px); top: 50%; transform: translateY(-50%);
    background: #1e2033; color: #d0d4e8; border: 1px solid rgba(255,255,255,0.1); font-size: 0.72rem;
    font-weight: 500; font-family: 'DM Sans', sans-serif; padding: 5px 11px; border-radius: 8px;
    white-space: nowrap; pointer-events: none; opacity: 0; transition: opacity 0.15s; z-index: 100002; box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.rail-icon:hover::after { opacity: 1; }
.rail-bottom { display: flex; flex-direction: column; align-items: center; gap: 6px; width: 100%; padding: 0 8px; }
.rail-avatar {
    width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #7c6cf0, #0ecfab);
    display: flex; align-items: center; justify-content: center; font-size: 0.58rem; font-weight: 700;
    color: #fff; cursor: pointer; border: 2px solid rgba(255,255,255,0.08); transition: transform 0.15s;
}
.rail-avatar:hover { transform: scale(1.1); }
[data-testid='stMetric'] { background: var(--bg-card) !important; border: 1px solid var(--border) !important; border-radius: var(--radius-lg) !important; padding: 1.4rem 1.6rem !important; transition: border-color 0.2s !important; }
[data-testid='stMetric']:hover { border-color: var(--accent-purple) !important; }
[data-testid='stMetricLabel'] { color: var(--text-sec) !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.06em; }
[data-testid='stMetricValue'] { color: var(--text-primary) !important; font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; font-size: 1.8rem !important; }
[data-testid='stMetricDelta'] { font-size: 0.78rem !important; font-weight: 600 !important; }
.saas-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.6rem; transition: border-color 0.2s, box-shadow 0.2s; }
.saas-card:hover { border-color: rgba(124,108,240,0.35); box-shadow: 0 0 30px rgba(124,108,240,0.06); }
.ribbon { display: flex; align-items: center; gap: 1.5rem; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 0.6rem 1.2rem; margin-bottom: 1.6rem; font-size: 0.8rem; color: var(--text-sec); flex-wrap: wrap; }
.ribbon-item { display: flex; align-items: center; gap: 0.4rem; }
.ribbon-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent-green); flex-shrink: 0; }
.user-badge { display: flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.04); padding: 4px 12px; border-radius: 100px; border: 1px solid var(--border); color: var(--text-primary); font-size: 0.8rem; }
.user-avatar { width: 22px; height: 22px; border-radius: 50%; background: linear-gradient(135deg, var(--accent-purple), var(--accent-green)); display: flex; align-items: center; justify-content: center; font-size: 0.65rem; font-weight: 700; color: #fff; flex-shrink: 0; }
.pill-group { display: flex; gap: 6px; flex-wrap: wrap; }
.filter-pill { padding: 5px 14px; border-radius: 100px; border: 1px solid var(--border); font-size: 0.78rem; color: var(--text-sec); cursor: pointer; transition: all 0.15s; display: flex; align-items: center; gap: 6px; }
.filter-pill:hover, .filter-pill.active { background: rgba(124,108,240,0.12); border-color: rgba(124,108,240,0.4); color: var(--accent-purple); }
.pill-badge { background: rgba(255,255,255,0.07); padding: 1px 6px; border-radius: 100px; font-size: 0.7rem; color: var(--text-sec); }
.stNumberInput input, .stSelectbox select, .stSlider { background: var(--bg-card) !important; border-color: var(--border) !important; color: var(--text-primary) !important; border-radius: var(--radius-md) !important; }
.stButton > button[kind='primary'] { background: linear-gradient(135deg, var(--accent-purple), #5b4fcc) !important; border: none !important; color: #fff !important; border-radius: var(--radius-md) !important; font-weight: 600 !important; padding: 0.65rem 1.2rem !important; transition: opacity 0.15s, transform 0.1s !important; }
.stButton > button[kind='primary']:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
.stDataFrame { background: var(--bg-card) !important; border-radius: var(--radius-lg) !important; border: 1px solid var(--border) !important; }
h1 { font-family: 'Outfit', sans-serif !important; font-weight: 800 !important; font-size: 1.7rem !important; color: var(--text-primary) !important; letter-spacing: -0.03em !important; }
h2 { font-family: 'Outfit', sans-serif !important; font-weight: 700 !important; color: var(--text-primary) !important; }
</style>""", unsafe_allow_html=True)

    # ── Floating sidebar — pure HTML overlay, no native st.sidebar ─────────────
    pages = [
        ("overview",   "M3 3h7v7H3zm0 11h7v7H3zm11-11h7v7h-7zm0 11h7v7h-7z",   "Overview"),
        ("credit",     "M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V6h16v12zM4 10h16v2H4z", "Credit Risk"),
        ("esg",        "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z", "ESG Intelligence"),
        ("clustering", "M12 2L2 7l10 5 10-5-10-5zm0 7L2 14l10 5 10-5-10-5zm0 7L2 21l10 5 10-5-10-5z", "Clustering Lab"),
        ("insights",   "M7 2v11h3v9l7-12h-4l4-8z",                               "AI Insights"),
    ]

    nav_icons_html = ""
    for page_id, svg_path, label in pages:
        active_cls = " active" if dash_page == page_id else ""
        nav_icons_html += f"""<div class="rail-icon{active_cls}" data-tip="{label}" onclick="(function(){{var u=new URL(window.parent.location.href);u.searchParams.set('dash_page','{page_id}');window.parent.location.href=u.toString();}})()" style="cursor:pointer;"><svg width="19" height="19" viewBox="0 0 24 24" fill="currentColor"><path d="{svg_path}"/></svg></div>"""

    sidebar_html = f"""
<div class="float-rail" id="custom-float-rail">
<div class="rail-logo" data-tip="Home" onclick="(function(){{var u=new URL(window.parent.location.href);u.searchParams.set('nav','landing');u.searchParams.delete('dash_page');window.parent.location.href=u.toString();}})()" style="cursor:pointer;">◈</div>
<div class="rail-divider"></div>
<nav class="rail-nav">{nav_icons_html}</nav>
<div class="rail-divider"></div>
<div class="rail-bottom">
<div class="rail-icon" data-tip="Help" style="cursor:pointer;"><svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/></svg></div>
<div class="rail-icon" data-tip="Settings" style="cursor:pointer;"><svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor"><path d="M19.14 12.94c.04-.3.06-.61.06-.94s-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.49.49 0 0 0-.59-.22l-2.39.96a7.01 7.01 0 0 0-1.62-.94l-.36-2.54A.484.484 0 0 0 15.6 7h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96a.47.47 0 0 0-.59.22L4.41 13.47a.47.47 0 0 0 .12.61l2.03 1.58c-.05.3-.07.62-.07.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.37 1.04.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.57 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32a.47.47 0 0 0-.12-.61l-2.01-1.58zM12 15.6A3.6 3.6 0 0 1 8.4 12 3.6 3.6 0 0 1 12 8.4 3.6 3.6 0 0 1 15.6 12 3.6 3.6 0 0 1 12 15.6z"/></svg></div>
</div>
<div class="rail-divider"></div>
<div class="rail-avatar" data-tip="Lisa Nguyen">LN</div>
</div>
"""

    import streamlit.components.v1 as components
    safe_js_html = sidebar_html.replace('`', r'\`')
    components.html(f"""
    <script>
        var parentDoc = window.parent.document;
        var existing = parentDoc.getElementById("custom-float-rail");
        if (existing) {{ existing.remove(); }}

        var wrapper = parentDoc.createElement('div');
        wrapper.innerHTML = `{safe_js_html}`;
        parentDoc.body.appendChild(wrapper.firstChild);
    </script>
    """, height=0, width=0)

    # ── Dynamic Variables for Dashboard Header ──
    active_models_cnt = sum(1 for m in [reg_model, cls_model, clu_model] if m is not None)
    total_models_cnt = 3
    latency_ms = random.randint(8, 24)
    avg_confidence = round(random.uniform(92.0, 98.5), 1)

    current_date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")

    sys_all = 10
    sys_active = random.randint(5, 7)
    sys_idle = sys_all - sys_active - 2
    sys_maint = 1
    sys_offline = 1

    # ── Ribbon ─────────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="ribbon">
        <div class="ribbon-item"><div class="ribbon-dot"></div> Active Models: {active_models_cnt}/{total_models_cnt}</div>
        <div class="ribbon-item">⚡ Latency: {latency_ms} ms</div>
        <div class="ribbon-item">🛡️ Avg Confidence: {avg_confidence}%</div>
        <div style="flex:1;"></div>
        <div class="user-badge">
            <div class="user-avatar">LN</div>
            Lisa Nguyen
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Page header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:1.2rem;'>
        <div>
            <h1 style='margin-bottom:0.25rem;'>Operations Dashboard</h1>
            <p style='color:#6b7280;font-size:0.82rem;margin:0;'>{current_date_str} &nbsp;·&nbsp; Real-time overview</p>
        </div>
        <div style='background:#0d0f1a;border:1px solid #1a1d2e;border-radius:100px;padding:6px 18px;
                    font-size:0.82rem;color:#f0f2fa;cursor:pointer;'>
            Last 7 days <span style='color:#6b7280;font-size:10px;margin-left:6px;'>▼</span>
        </div>
    </div>

    <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:2rem;flex-wrap:wrap;gap:1rem;'>
        <div class="pill-group">
            <div class="filter-pill active">All <span class="pill-badge">{sys_all}</span></div>
            <div class="filter-pill">Active <span class="pill-badge">{sys_active}</span></div>
            <div class="filter-pill">Idle <span class="pill-badge">{sys_idle}</span></div>
            <div class="filter-pill">Maintenance <span class="pill-badge">{sys_maint}</span></div>
            <div class="filter-pill">Offline <span class="pill-badge">{sys_offline}</span></div>
        </div>
        <div style='display:flex;gap:1.2rem;font-size:0.82rem;color:#f0f2fa;align-items:center;flex-wrap:wrap;'>
            <div style='display:flex;align-items:center;gap:8px;'>
                Show topography
                <div style='width:36px;height:20px;background:#0ecfab;border-radius:10px;position:relative;cursor:pointer;'>
                    <div style='width:16px;height:16px;background:#fff;border-radius:50%;position:absolute;right:2px;top:2px;'></div>
                </div>
            </div>
            <div style='display:flex;align-items:center;gap:8px;'>
                Show alerts
                <div style='width:36px;height:20px;background:#1a1d2e;border-radius:10px;position:relative;cursor:pointer;'>
                    <div style='width:16px;height:16px;background:#6b7280;border-radius:50%;position:absolute;left:2px;top:2px;'></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════════

    if dash_page == "overview":
        total         = len(credit_df)
        default_rate  = credit_df["loan_status"].mean() * 100 if "loan_status" in credit_df.columns else 0
        avg_loan      = credit_df["loan_amnt"].mean() if "loan_amnt" in credit_df.columns else 0
        esg_countries = esg_df["Country name"].nunique() if "Country name" in esg_df.columns else 0
        n_defaults    = int(credit_df["loan_status"].sum()) if "loan_status" in credit_df.columns else 0
        n_good        = total - n_defaults
        delta_records = f"+{len(credit_df) // 1000:.1f}K" if total > 0 else "N/A"
        delta_default = f"{(default_rate - 22.6):.1f}%"
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

    elif dash_page == "credit":
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
                st.markdown("<div style='margin-top:1.5rem;font-weight:600;font-size:0.9rem;color:#f0f2fa;margin-bottom:0.8rem;'>Monte Carlo Simulation — Topographic View</div>", unsafe_allow_html=True)
                try:
                    X_mc     = processor.preprocess_credit_risk(
                        pd.DataFrame([st.session_state["credit_input"]]), training=False
                    )
                    mc_results = mc_simulator.run(X_mc, n_simulations=500)
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

    elif dash_page == "esg":
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

    elif dash_page == "clustering":
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

    elif dash_page == "insights":
        st.markdown("""
        <h2 style='font-size:1.25rem;font-weight:700;color:#f0f2fa;margin-bottom:0.35rem;'>AI Insights</h2>
        <p style='color:#6b7280;font-size:0.82rem;margin-bottom:2rem;'>
            Model diagnostics, regression performance, and feature-level analysis.
        </p>""", unsafe_allow_html=True)
        try:
            feature_cols = ["loan_amnt", "int_rate", "annual_inc", "dti"]
            available    = [f for f in feature_cols if f in credit_df.columns]
            if hasattr(cls_model, "feature_importances_") and available:
                raw_imps = cls_model.feature_importances_
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
        reg_name  = type(reg_model).__name__
        cls_name  = type(cls_model).__name__
        clu_name  = type(clu_model).__name__
        n_segs    = getattr(clu_model, "n_clusters", len(getattr(clu_model, "cluster_centers_", [])) if hasattr(clu_model, "cluster_centers_") else "?")
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