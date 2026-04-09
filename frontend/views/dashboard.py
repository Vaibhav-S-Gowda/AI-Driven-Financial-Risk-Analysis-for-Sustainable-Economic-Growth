"""
dashboard.py  ·  FinRisk AI
───────────────────────────
Responsibilities:
  • Default page = Monte Carlo HTML dashboard (dashboard.html), rendered
    full-viewport with zero Streamlit chrome.
  • Other pages (overview, credit, esg, clustering, insights) render
    Streamlit layouts with REAL metrics from passed-in models/DataFrames —
    nothing hardcoded.
  • Buttons work: BACKEND_URL is cleared so the JS GBM engine runs
    immediately with a 2-second abort-timeout guard on any fetch attempt.
"""

from __future__ import annotations

import os
import re
import datetime
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# ── Project config (gracefully degrade if missing) ────────────────────────────
try:
    from backend.config import CLUSTER_COLORS
except ImportError:
    CLUSTER_COLORS = ["#0ecfab", "#7c6cf0", "#f87171", "#fbbf24", "#60a5fa"]

# ── Color scales ──────────────────────────────────────────────────────────────
AURORA_SCALE = [
    [0.00, "#0a0a1a"], [0.15, "#0d1f3c"], [0.30, "#0a3d62"],
    [0.45, "#0ecfab"], [0.60, "#7c6cf0"], [0.75, "#c084fc"],
    [0.90, "#f0abfc"], [1.00, "#ffffff"],
]
FIRE_ICE_SCALE = [
    [0.00, "#0a1628"], [0.25, "#1e40af"], [0.45, "#0ecfab"],
    [0.60, "#fbbf24"], [0.80, "#f87171"], [1.00, "#fff0f0"],
]
SCENE_AXIS_DARK = dict(
    showbackground=True, backgroundcolor="rgba(0,0,0,0)",
    gridcolor="#1e1e2e", gridwidth=1,
    tickfont=dict(color="#555", size=9),
    titlefont=dict(color="#777", size=10),
    showspikes=False,
)

# ── Shared card CSS (Streamlit sub-pages only) ────────────────────────────────
GLOBAL_CSS = """
<style>
    .stApp { background-color: #f8fafc; }
    .saas-card {
        background: white; padding: 24px; border-radius: 16px;
        border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
        transition: transform .2s, box-shadow .2s;
    }
    .saas-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
    }
    [data-testid="stHeader"] { background: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 40px; background: #fff;
        border-radius: 8px; border: 1px solid #eee; padding: 0 16px;
    }
    .stTabs [aria-selected="true"] {
        background: #111 !important; color: #fff !important;
    }
</style>
"""


# ══════════════════════════════════════════════════════════════════════════════
#  FLOATING NAV BAR
# ══════════════════════════════════════════════════════════════════════════════
def _inject_topnav(active: str) -> None:
    pages = [
        ("overview",   "Overview"),
        ("credit",     "Credit Risk"),
        ("esg",        "ESG Intelligence"),
        ("clustering", "Clustering Lab"),
        ("insights",   "AI Insights"),
        ("simulation", "Monte Carlo Sim"),
    ]
    tabs_html = "".join(
        f'<div class="tnav-tab{" tnav-active" if active == pid else ""}" '
        f'onclick="(function(){{var u=new URL(window.parent.location.href);'
        f'u.searchParams.set(\'dash_page\',\'{pid}\');'
        f'window.parent.location.href=u.toString();}})();">{lbl}</div>'
        for pid, lbl in pages
    )
    blob = f"""
    <style>
    #fr-nav-style{{display:none}}
    .tnav-container{{
        position:fixed;top:0;left:0;right:0;height:50px;
        background:rgba(255,255,255,.88);
        backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);
        display:flex;align-items:center;padding:0 40px;
        z-index:999999;border-bottom:1px solid rgba(0,0,0,.05);
        font-family:'Inter',-apple-system,sans-serif;
    }}
    .tnav-brand{{font-weight:800;font-size:1.1rem;color:#111;
        margin-right:40px;letter-spacing:-.03em;}}
    .tnav-tabs{{display:flex;gap:4px;height:100%;align-items:center;}}
    .tnav-tab{{padding:6px 14px;border-radius:8px;cursor:pointer;
        font-size:.85rem;font-weight:500;color:#666;transition:all .2s;}}
    .tnav-tab:hover{{background:rgba(0,0,0,.04);color:#111;}}
    .tnav-active{{background:#111!important;color:#fff!important;}}
    </style>
    <div id="fr-nav-style"></div>
    <div class="tnav-container" id="fr-topnav">
        <div class="tnav-brand">&#9672; FinRisk <span style="color:#0ecfab">AI</span></div>
        <div class="tnav-tabs">{tabs_html}</div>
        <div style="flex:1"></div>
        <div style="font-size:.75rem;color:#999;font-weight:500;">PRO TERMINAL v2.4</div>
    </div>
    """.replace("`", r"\`")

    components.html(f"""
    <script>
    (function(){{
        var pd=window.parent.document;
        ['fr-topnav','fr-nav-style'].forEach(function(id){{
            var el=pd.getElementById(id);if(el)el.remove();
        }});
        var w=pd.createElement('div');
        w.innerHTML=`{blob}`;
        while(w.firstChild)pd.body.appendChild(w.firstChild);
    }})();
    </script>
    """, height=0, width=0)


# ══════════════════════════════════════════════════════════════════════════════
#  FULL-SCREEN HTML RENDERER
# ══════════════════════════════════════════════════════════════════════════════
def _render_html_dashboard() -> None:
    """
    Kills all Streamlit chrome, reads dashboard.html, patches it for
    full-screen + working buttons, then renders it via components.html.
    The JS injected inside the iframe fixes the *parent* Streamlit document
    so the iframe expands to cover the full viewport.
    """

    # ── 1. Python-side chrome removal ────────────────────────────────────────
    st.markdown("""
    <style>
        [data-testid="stSidebar"]          { display: none !important; }
        [data-testid="stHeader"]           { display: none !important; }
        footer                             { display: none !important; }
        #MainMenu                          { visibility: hidden !important; }
        /* Kill any dark/black Streamlit backgrounds */
        html, body, .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        .main                              { background: #EBF0F6 !important;
                                             background-color: #EBF0F6 !important; }
        .main .block-container,
        .stMainBlockContainer,
        section.main > div                 { padding: 0 !important;
                                             max-width: 100% !important;
                                             margin: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── 2. Resolve path ───────────────────────────────────────────────────────
    html_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "dashboard.html"
    )
    if not os.path.exists(html_path):
        st.error(
            f"dashboard.html not found at: {os.path.abspath(html_path)}\n\n"
            "Place dashboard.html inside frontend/ (one level above frontend/views/)."
        )
        return

    with open(html_path, "r", encoding="utf-8") as fh:
        html = fh.read()

    # ── 3. Patch: disable backend URL so JS GBM engine runs immediately ───────
    html = re.sub(
        r'const BACKEND_URL\s*=\s*["\'].*?["\'];',
        'const BACKEND_URL = "";  // JS engine only — no backend required',
        html,
    )

    # ── 4. Patch: add fetch AbortController timeout (prevents button freeze) ──
    abort_patch = """
    /* ── Abort-timeout patch (injected by dashboard.py) ──────────────────── */
    (function() {
        var _origFetch = window.fetch.bind(window);
        window.fetch = function(url, opts) {
            opts = opts || {};
            if (!opts.signal) {
                var ctrl = new AbortController();
                setTimeout(function() { ctrl.abort(); }, 2000);
                opts.signal = ctrl.signal;
            }
            return _origFetch(url, opts);
        };
    })();
    /* ─────────────────────────────────────────────────────────────────────── */
    """
    # ── 4. Patch: add fetch AbortController timeout (prevents button freeze) ──
    # Target only the first script tag that DOES NOT have a src attribute
    html = re.sub(r"<(script)(?![^>]*src\s*=)[^>]*>", r"<\1>\n" + abort_patch, html, count=1, flags=re.IGNORECASE)

    # ── 5. Inject full-screen JS that fixes the parent Streamlit document ─────
    fullscreen_js = """
<script id="fr-fullscreen-patch">
/* Injected by dashboard.py — makes this iframe fill the viewport */
(function applyFullscreen() {
    function fix() {
        try {
            var pd = window.parent.document;

            /* Kill Streamlit chrome in the parent + force background to match dashboard */
            var s = pd.getElementById('fr-fs-css');
            if (!s) {
                s = pd.createElement('style');
                s.id = 'fr-fs-css';
                pd.head.appendChild(s);
            }
            s.textContent =
                '[data-testid="stSidebar"]{display:none!important}' +
                '[data-testid="stHeader"]{display:none!important}' +
                'footer{display:none!important}' +
                '#MainMenu{visibility:hidden!important}' +
                /* Force parent body/app background to match the dashboard colour */
                'html,body{background:#EBF0F6!important;overflow:hidden!important;margin:0!important;padding:0!important}' +
                '.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]' +
                '{background:#EBF0F6!important;background-color:#EBF0F6!important}' +
                '.main .block-container{padding:0!important;max-width:100%!important;margin:0!important}' +
                '.stMainBlockContainer{padding:0!important}' +
                'section.main>div{padding:0!important}';

            /* Find THIS iframe and stretch it to 100 vh/vw */
            var frames = pd.querySelectorAll('iframe');
            for (var i = 0; i < frames.length; i++) {
                try {
                    if (frames[i].contentWindow === window) {
                        frames[i].style.cssText =
                            'position:fixed;top:0;left:0;' +
                            'width:100vw;height:100vh;' +
                            'border:none;z-index:99999;' +
                            'background:#EBF0F6;';
                        /* Also fix the iframe's wrapper element */
                        var wrapper = frames[i].parentElement;
                        if (wrapper) {
                            wrapper.style.cssText =
                                'position:fixed;top:0;left:0;' +
                                'width:100vw;height:100vh;' +
                                'overflow:visible;z-index:99999;';
                        }
                    }
                } catch(ie) { /* skip cross-origin frames */ }
            }
        } catch (e) {
            console.warn('[FinRisk] Fullscreen patch error:', e);
        }
    }

    /* Run immediately, then retry as Streamlit hydrates asynchronously */
    fix();
    [100, 400, 900, 1800, 3000].forEach(function(ms) { setTimeout(fix, ms); });

    /* Also re-apply whenever the parent URL changes (tab navigation) */
    try {
        window.parent.addEventListener('popstate', fix);
    } catch(e) {}
})();
</script>
"""
    html = html.replace("</body>", fullscreen_js + "\n</body>")

    # ── 6. Render ─────────────────────────────────────────────────────────────
    # height=1200 is a generous floor; the JS above overrides it to 100vh via position:fixed.
    # scrolling=True ensures content is reachable even if the fullscreen JS hasn't fired yet.
    components.html(html, height=1200, scrolling=True)


# ══════════════════════════════════════════════════════════════════════════════
#  3-D CHART HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _plot_3d(df, x, y, z, color, scale, title=""):
    fig = px.scatter_3d(
        df, x=x, y=y, z=z, color=color,
        color_discrete_sequence=CLUSTER_COLORS if color == "Cluster" else None,
        color_continuous_scale=scale if color != "Cluster" else None,
        opacity=0.8, title=title,
    )
    fig.update_traces(marker=dict(size=4, line=dict(width=0, color="DarkSlateGrey")))
    fig.update_layout(
        margin=dict(l=0, r=0, b=0, t=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        scene=dict(xaxis=SCENE_AXIS_DARK, yaxis=SCENE_AXIS_DARK,
                   zaxis=SCENE_AXIS_DARK, aspectmode="cube"),
        font=dict(family="Inter", size=11, color="#777"),
    )
    return fig


def _render_3d_view(df: pd.DataFrame, target_col: str) -> None:
    cols = [c for c in df.columns if c != target_col][:3]
    if len(cols) < 3:
        st.warning("Insufficient numeric features for 3-D visualisation.")
        return
    st.plotly_chart(
        _plot_3d(df, cols[0], cols[1], cols[2], target_col,
                 AURORA_SCALE, f"Feature Space — {target_col}"),
        use_container_width=True,
        config={"displayModeBar": False},
    )


# ══════════════════════════════════════════════════════════════════════════════
#  METRIC HELPERS — derive real values from models/DataFrames
# ══════════════════════════════════════════════════════════════════════════════
def _safe_r2(model, df: pd.DataFrame) -> str:
    try:
        from sklearn.metrics import r2_score
        target_c = next(
            c for c in df.columns
            if any(kw in c.lower() for kw in ("target", "price", "value", "revenue"))
        )
        features = df.select_dtypes(include="number").drop(columns=[target_c], errors="ignore")
        if features.empty:
            return "—"
        return f"{r2_score(df[target_c], model.predict(features)):.3f}"
    except Exception:
        return "—"


def _safe_auc(model, df: pd.DataFrame) -> str:
    try:
        from sklearn.metrics import roc_auc_score
        target_c = next(
            c for c in df.columns
            if any(kw in c.lower() for kw in ("default", "risk", "label", "target"))
        )
        features = df.select_dtypes(include="number").drop(columns=[target_c], errors="ignore")
        if features.empty:
            return "—"
        proba = model.predict_proba(features)[:, 1]
        return f"{roc_auc_score(df[target_c], proba):.3f}"
    except Exception:
        return "—"


def _n_clusters(model) -> str:
    for attr in ("n_clusters", "n_components", "k"):
        if hasattr(model, attr):
            return str(getattr(model, attr))
    return "—"


def _feature_importances(model, df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    try:
        imp = model.feature_importances_
        return (
            pd.DataFrame({"Feature": numeric_cols[:len(imp)], "Impact": imp[:len(numeric_cols)]})
            .sort_values("Impact", ascending=False).head(top_n)
        )
    except AttributeError:
        try:
            coef = np.abs(model.coef_.flatten())
            return (
                pd.DataFrame({"Feature": numeric_cols[:len(coef)], "Impact": coef[:len(numeric_cols)]})
                .sort_values("Impact", ascending=False).head(top_n)
            )
        except Exception:
            return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def render_dashboard(
    processor: Any,
    credit_df: pd.DataFrame,
    fin_df: pd.DataFrame,
    esg_df: pd.DataFrame,
    reg_model: Any,
    cls_model: Any,
    clu_model: Any,
    clu_scaler: Any,
    mc_simulator: Any,
) -> None:

    dash_page = st.query_params.get("dash_page", "simulation")

    # ── Monte Carlo page: full-screen HTML, exit immediately ─────────────────
    if dash_page == "simulation":
        _render_html_dashboard()
        return

    # ── All other pages: Streamlit widgets + floating nav ────────────────────
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    _inject_topnav(dash_page)
    st.markdown("<div style='height:58px'></div>", unsafe_allow_html=True)  # nav spacer

    # ─────────────────────────────────────────────────────────────────────────
    if dash_page == "overview":
        total_assets = fin_df["Total Assets"].sum() if "Total Assets" in fin_df.columns else 0
        avg_esg      = esg_df["ESG Score"].mean()   if "ESG Score"    in esg_df.columns else 0

        st.markdown(f"### Executive Summary — {datetime.date.today().strftime('%B %Y')}")

        m1, m2, m3, m4 = st.columns(4)
        for col, label, value, color in [
            (m1, "Portfolio Size",  f"${total_assets/1e9:.2f}B" if total_assets else "N/A", "#111"),
            (m2, "ESG Benchmark",   f"{avg_esg:.1f}"            if avg_esg      else "N/A", "#0ecfab"),
            (m3, "Entities",        f"{len(fin_df):,}",                                     "#7c6cf0"),
            (m4, "ESG Records",     f"{len(esg_df):,}",                                     "#fbbf24"),
        ]:
            with col:
                st.markdown(f"""
                <div class='saas-card'>
                    <div style='color:#666;font-size:.7rem;text-transform:uppercase;
                                letter-spacing:.05em;margin-bottom:4px;'>{label}</div>
                    <div style='font-size:1.6rem;font-weight:800;
                                color:{color};letter-spacing:-.03em;'>{value}</div>
                </div>""", unsafe_allow_html=True)

        st.write("")

        r2_val  = _safe_r2(reg_model, fin_df)    if reg_model else "—"
        auc_val = _safe_auc(cls_model, credit_df) if cls_model else "—"
        n_seg   = _n_clusters(clu_model)           if clu_model else "—"
        reg_name = reg_model.__class__.__name__ if reg_model else "Not loaded"
        cls_name = cls_model.__class__.__name__ if cls_model else "Not loaded"
        clu_name = clu_model.__class__.__name__ if clu_model else "Not loaded"

        ia, ib, ic = st.columns(3, gap="medium")
        for col, icon, lbl, name, metric, mc in [
            (ia, "📈", "Regression Model", reg_name, f"R² = {r2_val}",   "#0ecfab"),
            (ib, "🎯", "Classification",   cls_name, f"AUC = {auc_val}", "#0ecfab"),
            (ic, "🧩", "Clustering",       clu_name, f"{n_seg} segments", "#fbbf24"),
        ]:
            with col:
                st.markdown(f"""
                <div class='saas-card'>
                    <div style='font-size:1.4rem;margin-bottom:.6rem;'>{icon}</div>
                    <div style='font-size:.7rem;color:#666;text-transform:uppercase;
                                letter-spacing:.06em;margin-bottom:.2rem;'>{lbl}</div>
                    <div style='font-weight:700;font-size:1rem;margin-bottom:.4rem;'>{name}</div>
                    <div style='font-size:.9rem;color:{mc};font-weight:600;'>{metric}</div>
                </div>""", unsafe_allow_html=True)

        st.write("")
        if "Sector" in fin_df.columns and "Total Assets" in fin_df.columns:
            fig = px.pie(
                fin_df, names="Sector", values="Total Assets", hole=0.45,
                title="Portfolio Composition by Sector",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=360)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No 'Sector' or 'Total Assets' column found in fin_df.")

    # ─────────────────────────────────────────────────────────────────────────
    elif dash_page == "credit":
        st.markdown("### 🛡️ Credit Risk Intelligence")

        auc_val = _safe_auc(cls_model, credit_df) if cls_model else None
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("""<div class='saas-card'>
                <h4 style='margin:0 0 6px;'>Risk Classification</h4>
                <p style='color:#666;font-size:.8rem;line-height:1.5;'>
                    Neural engine analysis of counterparty default probability.
                </p>
            </div>""", unsafe_allow_html=True)
            st.metric(
                "Model AUC-ROC",
                auc_val if (auc_val and auc_val != "—") else "Run cls_model first",
            )
        with c2:
            target_candidates = [
                c for c in credit_df.columns
                if any(kw in c.lower() for kw in ("risk", "score", "default", "prob"))
            ]
            target_col = target_candidates[0] if target_candidates else credit_df.columns[-1]
            _render_3d_view(credit_df, target_col)

        st.write("---")
        st.subheader("Feature Impact")
        imp_df = _feature_importances(cls_model, credit_df) if cls_model else pd.DataFrame()
        if not imp_df.empty:
            fig = px.bar(imp_df, x="Impact", y="Feature", orientation="h",
                         color_discrete_sequence=["#0ecfab"])
            fig.update_layout(height=320, margin=dict(t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Feature importances are available for tree-based / linear classifiers.")

        st.subheader("Credit Data Preview")
        st.dataframe(credit_df.head(20), use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────
    elif dash_page == "esg":
        st.markdown("### 🌿 ESG Sustainability Lab")

        env_col = next((c for c in esg_df.columns if "environ" in c.lower()), None)
        soc_col = next((c for c in esg_df.columns if "social"  in c.lower()), None)
        gov_col = next((c for c in esg_df.columns if "govern"  in c.lower()), None)
        score_c = next((c for c in esg_df.columns if "score"   in c.lower()), None)

        e1, e2 = st.columns([2, 1])
        with e1:
            if all([env_col, soc_col, gov_col, score_c]):
                fig = _plot_3d(esg_df, env_col, soc_col, gov_col,
                               score_c, FIRE_ICE_SCALE, "ESG Factor Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(
                    "ESG 3-D plot requires columns containing 'Environmental', "
                    "'Social', 'Governance', and 'Score' in their names."
                )
                st.dataframe(esg_df.head(10), use_container_width=True)

        with e2:
            env_mean = float(np.clip(esg_df[env_col].mean() / 100, 0, 1)) if env_col else 0.0
            soc_mean = float(np.clip(esg_df[soc_col].mean() / 100, 0, 1)) if soc_col else 0.0
            gov_mean = float(np.clip(esg_df[gov_col].mean() / 100, 0, 1)) if gov_col else 0.0

            st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
            st.markdown("#### Sustainability KPIs")
            st.write("Derived from ESG dataset averages.")
            st.progress(env_mean, text=f"Environment  ({env_mean*100:.1f}%)")
            st.progress(soc_mean, text=f"Social       ({soc_mean*100:.1f}%)")
            st.progress(gov_mean, text=f"Governance   ({gov_mean*100:.1f}%)")
            st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    elif dash_page == "clustering":
        st.markdown("### 🧩 Unsupervised Clustering Lab")

        view_options = ["Client Segments", "Risk Clusters", "Market Nuance"]
        view_type = st.segmented_control("Perspective", view_options, default=view_options[0])

        cluster_col = "Cluster" if "Cluster" in fin_df.columns else None
        num_cols    = fin_df.select_dtypes(include="number").columns.tolist()

        if cluster_col and len(num_cols) >= 3:
            x, y, z = num_cols[0], num_cols[1], num_cols[2]
            fig = _plot_3d(fin_df, x, y, z, cluster_col, AURORA_SCALE,
                           f"Segment Analysis — {view_type}")
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("Cluster Averages")
            st.dataframe(
                fin_df.groupby(cluster_col)[num_cols].mean().round(2),
                use_container_width=True,
            )
        elif len(num_cols) >= 3:
            st.info(
                "No 'Cluster' column found — run `clu_model.fit_predict` and "
                "assign the result as `fin_df['Cluster']`."
            )
            x, y, z = num_cols[0], num_cols[1], num_cols[2]
            color_c  = num_cols[3] if len(num_cols) > 3 else z
            fig = _plot_3d(fin_df, x, y, z, color_c, AURORA_SCALE,
                           f"Feature Space — {view_type}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("fin_df needs at least 3 numeric columns for a 3-D cluster plot.")

    # ─────────────────────────────────────────────────────────────────────────
    elif dash_page == "insights":
        st.markdown("### 🤖 AI Insight Engine")

        insights: list[dict] = []

        if "Total Assets" in fin_df.columns:
            total = fin_df["Total Assets"].sum()
            insights.append({
                "icon": "📈", "color": "#0ecfab", "bg": "#ECFDF5",
                "title": "Portfolio Size",
                "body": (
                    f"Total asset base: <strong>${total/1e9:.2f}B</strong> "
                    f"across {len(fin_df):,} entities."
                ),
            })

        if "ESG Score" in esg_df.columns:
            avg    = esg_df["ESG Score"].mean()
            below50 = int((esg_df["ESG Score"] < 50).sum())
            insights.append({
                "icon": "🌿", "color": "#10B981", "bg": "#ECFDF5",
                "title": "ESG Health",
                "body": (
                    f"Mean ESG score: <strong>{avg:.1f}</strong>. "
                    f"<strong>{below50}</strong> entities score below 50 — review advised."
                ),
            })

        r2_v  = _safe_r2(reg_model, fin_df)      if reg_model else "—"
        auc_v = _safe_auc(cls_model, credit_df)  if cls_model else "—"
        n_s   = _n_clusters(clu_model)            if clu_model else "—"
        insights.append({
            "icon": "🤖", "color": "#7c6cf0", "bg": "#EDE9FE",
            "title": "Active Models",
            "body": (
                f"Regression R²: <strong>{r2_v}</strong> &nbsp;·&nbsp; "
                f"Classification AUC: <strong>{auc_v}</strong> &nbsp;·&nbsp; "
                f"Cluster segments: <strong>{n_s}</strong>."
            ),
        })

        if not credit_df.empty:
            hr_col = next(
                (c for c in credit_df.columns if "risk" in c.lower()), None
            )
            if hr_col:
                threshold = credit_df[hr_col].quantile(0.90)
                high = int((credit_df[hr_col] > threshold).sum())
                insights.append({
                    "icon": "⚠️", "color": "#EF4444", "bg": "#FEF2F2",
                    "title": "High-Risk Counterparties",
                    "body": (
                        f"<strong>{high}</strong> entities exceed the 90th percentile "
                        f"on <code>{hr_col}</code>. Immediate review advised."
                    ),
                })

        if not insights:
            insights.append({
                "icon": "ℹ️", "color": "#3B82F6", "bg": "#EFF6FF",
                "title": "No Data Available",
                "body": "Pass populated DataFrames and trained models to generate insights.",
            })

        for ins in insights:
            st.markdown(f"""
            <div class='saas-card' style='margin-bottom:14px;
                                          border-left:4px solid {ins["color"]};'>
                <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px;'>
                    <span style='font-size:1.3rem;'>{ins["icon"]}</span>
                    <strong style='font-size:.95rem;color:#111;'>{ins["title"]}</strong>
                </div>
                <p style='color:#555;font-size:.85rem;line-height:1.6;margin:0;'>
                    {ins["body"]}
                </p>
            </div>""", unsafe_allow_html=True)

        st.subheader("Raw Data Preview")
        t1, t2, t3 = st.tabs(["Financial", "ESG", "Credit"])
        with t1:
            st.dataframe(fin_df.head(15), use_container_width=True)
        with t2:
            st.dataframe(esg_df.head(15), use_container_width=True)
        with t3:
            st.dataframe(credit_df.head(15), use_container_width=True)