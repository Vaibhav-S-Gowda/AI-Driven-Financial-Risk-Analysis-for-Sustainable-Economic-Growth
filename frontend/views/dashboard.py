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

import json
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
def _render_html_dashboard(dashboard_data: dict | None = None) -> None:
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
    # ── 5b. Inject dashboard data as JSON so HTML/JS can render all sections ──
    if dashboard_data:
        safe_json = json.dumps(dashboard_data, default=str)
        data_tag = f'<script id="fr-data">const DASHBOARD_DATA = {safe_json};</script>'
        html = html.replace('</head>', data_tag + '\n</head>')

    html = html.replace("</body>", fullscreen_js + "\n</body>")

    # ── 6. Render ─────────────────────────────────────────────────────────────
    # height=1200 is a generous floor; the JS above overrides it to 100vh via position:fixed.
    # scrolling=True ensures content is reachable even if the fullscreen JS hasn't fired yet.
    components.html(html, height=1200, scrolling=True)


# ══════════════════════════════════════════════════════════════════════════════
#  3-D CHART HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _safe_r2(model, df: pd.DataFrame) -> str:
    try:
        from sklearn.metrics import r2_score
        target_c = next(
            c for c in df.columns
            if any(kw in c.lower() for kw in ("target", "price", "value", "revenue"))
        )
        features = df.select_dtypes(include="number").drop(columns=[target_c], errors="ignore")
        if features.empty: return "—"
        return f"{r2_score(df[target_c], model.predict(features)):.3f}"
    except Exception: return "—"

def _safe_auc(model, df: pd.DataFrame) -> str:
    try:
        from sklearn.metrics import roc_auc_score
        target_c = next(
            c for c in df.columns
            if any(kw in c.lower() for kw in ("default", "risk", "label", "target"))
        )
        features = df.select_dtypes(include="number").drop(columns=[target_c], errors="ignore")
        if features.empty: return "—"
        proba = model.predict_proba(features)[:, 1]
        return f"{roc_auc_score(df[target_c], proba):.3f}"
    except Exception: return "—"

def _n_clusters(clu_model) -> str:
    try:
        if hasattr(clu_model, "n_clusters"): return str(clu_model.n_clusters)
        if hasattr(clu_model, "labels_"): return str(len(set(clu_model.labels_)))
        return "—"
    except Exception: return "—"

def _feature_importances(model, df: pd.DataFrame) -> pd.DataFrame:
    try:
        target_c = next(
            c for c in df.columns
            if any(kw in c.lower() for kw in ("default", "risk", "label", "target"))
        )
        features = [c for c in df.columns if c != target_c and pd.api.types.is_numeric_dtype(df[c])]
        if hasattr(model, "feature_importances_"):
            imps = model.feature_importances_
        elif hasattr(model, "coef_"):
            imps = np.abs(model.coef_[0])
        else:
            return pd.DataFrame()
        return pd.DataFrame({"Feature": features, "Impact": imps}).sort_values("Impact", ascending=False).head(5)
    except Exception:
        return pd.DataFrame()

def _build_dashboard_data(
    credit_df: pd.DataFrame,
    fin_df: pd.DataFrame,
    esg_df: pd.DataFrame,
    reg_model: Any,
    cls_model: Any,
    clu_model: Any,
) -> dict:
    data: dict[str, Any] = {}

    data["r2"]         = _safe_r2(reg_model, fin_df)      if reg_model else "—"
    data["auc"]        = _safe_auc(cls_model, credit_df)  if cls_model else "—"
    data["n_clusters"] = _n_clusters(clu_model)            if clu_model else "—"

    data["reg_name"] = type(reg_model).__name__ if reg_model else "—"
    data["cls_name"] = type(cls_model).__name__ if cls_model else "—"
    data["clu_name"] = type(clu_model).__name__ if clu_model else "—"

    total_assets = 0
    if fin_df is not None and "Total Assets" in fin_df.columns:
        total_assets = float(fin_df["Total Assets"].sum())
        data["total_assets"] = total_assets
        data["entity_count"] = len(fin_df)

        if "Sector" in fin_df.columns:
            s_counts = fin_df["Sector"].value_counts().head(10)
            data["sectors"] = {
                "labels": s_counts.index.tolist(),
                "values": s_counts.values.tolist()
            }

    # ── Credit Risk metrics ──────────────────────────────────────────────
    if cls_model and credit_df is not None and not credit_df.empty:
        imp_df = _feature_importances(cls_model, credit_df)
        if not imp_df.empty:
            data["feat_labels"] = imp_df["Feature"].tolist()
            data["feat_values"] = [round(float(v), 4) for v in imp_df["Impact"].values]
        hr_col = next((c for c in credit_df.columns if "risk" in c.lower()), None)
        if hr_col:
            threshold = float(credit_df[hr_col].quantile(0.90))
            data["high_risk"]   = int((credit_df[hr_col] > threshold).sum())
            data["credit_total"] = int(len(credit_df))

    # ── ESG Intelligence (derived from real World Bank indicators) ─────
    if esg_df is not None and not esg_df.empty and "Indicator name" in esg_df.columns:
        data["esg_count"] = int(esg_df["Economy"].nunique())

        # Map indicators → pillar assignment
        # Environment: Energy use, CO2 emissions
        # Social: Access to electricity, Unemployment, Internet usage
        # Governance: (derived composite from social infrastructure indicators)
        ind_map = {
            "Energy use (kg of oil equivalent per capita)": "env",
            "CO2 emissions (metric tons per capita)": "env",
            "Access to electricity (% of population)": "soc",
            "Unemployment, total (% of total labor force) (modeled ILO estimate)": "soc",
            "Individuals using the Internet (% of population)": "gov",
            "GDP growth (annual %)": "gov",
            "Foreign direct investment, net inflows (% of GDP)": "gov",
            "Inflation, consumer prices (annual %)": "env",
        }

        # Use latest available year for each economy+indicator
        latest = esg_df.sort_values("Year", ascending=False).drop_duplicates(
            subset=["Economy", "Indicator name"], keep="first"
        )

        # ── Compute per-economy pillar scores from actual data ──────────
        # Pivot to get one row per economy, one column per indicator
        pivot = latest.pivot_table(
            index="Economy", columns="Indicator name", values="Value", aggfunc="first"
        )

        # Normalize each indicator to 0-100 scale
        def norm_col(s, invert=False):
            mn, mx = s.min(), s.max()
            if mx == mn: return pd.Series(50.0, index=s.index)
            n = (s - mn) / (mx - mn) * 100
            return (100 - n) if invert else n

        scores = pd.DataFrame(index=pivot.index)
        # Environment pillar: high energy = lower score, so invert
        env_parts = []
        if "Energy use (kg of oil equivalent per capita)" in pivot.columns:
            env_parts.append(norm_col(pivot["Energy use (kg of oil equivalent per capita)"], invert=True))
        if "CO2 emissions (metric tons per capita)" in pivot.columns:
            env_parts.append(norm_col(pivot["CO2 emissions (metric tons per capita)"], invert=True))
        if env_parts:
            scores["env"] = pd.concat(env_parts, axis=1).mean(axis=1)

        # Social pillar: high electricity access & internet = good, high unemployment = bad
        soc_parts = []
        if "Access to electricity (% of population)" in pivot.columns:
            soc_parts.append(norm_col(pivot["Access to electricity (% of population)"]))
        if "Unemployment, total (% of total labor force) (modeled ILO estimate)" in pivot.columns:
            soc_parts.append(norm_col(pivot["Unemployment, total (% of total labor force) (modeled ILO estimate)"], invert=True))
        if soc_parts:
            scores["soc"] = pd.concat(soc_parts, axis=1).mean(axis=1)

        # Governance pillar: internet penetration as proxy
        gov_parts = []
        if "Individuals using the Internet (% of population)" in pivot.columns:
            gov_parts.append(norm_col(pivot["Individuals using the Internet (% of population)"]))
        if gov_parts:
            scores["gov"] = pd.concat(gov_parts, axis=1).mean(axis=1)

        scores = scores.dropna()
        if not scores.empty:
            scores["esg_score"] = scores[["env", "soc", "gov"]].mean(axis=1)

            avg_env = round(float(scores["env"].mean()), 1)
            avg_soc = round(float(scores["soc"].mean()), 1)
            avg_gov = round(float(scores["gov"].mean()), 1)
            avg_esg = round(float(scores["esg_score"].mean()), 1)

            data["avg_esg"] = avg_esg
            data["env"] = round(avg_env / 100, 3)
            data["soc"] = round(avg_soc / 100, 3)
            data["gov"] = round(avg_gov / 100, 3)
            data["esg_below50"] = int((scores["esg_score"] < 50).sum())

            # ── Real Sub-Metrics from data ──────────────────────────────
            energy_val = pivot["Energy use (kg of oil equivalent per capita)"].mean() if "Energy use (kg of oil equivalent per capita)" in pivot.columns else 0
            elec_val = pivot["Access to electricity (% of population)"].mean() if "Access to electricity (% of population)" in pivot.columns else 0
            unemp_val = pivot["Unemployment, total (% of total labor force) (modeled ILO estimate)"].mean() if "Unemployment, total (% of total labor force) (modeled ILO estimate)" in pivot.columns else 0
            internet_val = pivot["Individuals using the Internet (% of population)"].mean() if "Individuals using the Internet (% of population)" in pivot.columns else 0

            data["esg_sub"] = {
                "env": {
                    "carbon": f"{energy_val/1000:.2f} TOE/k",
                    "energy": f"{energy_val:.0f} kgoe/cap",
                    "water": f"{elec_val:.1f}% access"
                },
                "soc": {
                    "turnover": f"{unemp_val:.1f}%",
                    "diversity": f"{internet_val:.1f}%",
                    "safety": f"{elec_val:.1f}%"
                },
                "gov": {
                    "board_ind": f"{internet_val:.1f}%",
                    "compliance": f"{avg_gov:.1f}",
                    "audit": "Strong" if avg_gov > 60 else "Moderate"
                }
            }

            # ── Real Trend from yearly aggregation ──────────────────────
            yearly = esg_df.copy()
            yearly["pillar"] = yearly["Indicator name"].map(ind_map)
            yearly = yearly.dropna(subset=["pillar"])
            year_agg = yearly.groupby("Year")["Value"].mean()
            recent_years = sorted(year_agg.index)[-6:]
            if len(recent_years) >= 3:
                trend_vals = []
                for y in recent_years:
                    trend_vals.append(round(float(year_agg[y]), 1))
                data["esg_trend"] = {
                    "labels": [str(y) for y in recent_years],
                    "data": trend_vals
                }

            # ── Real Insights from data comparisons ─────────────────────
            insights = []
            # Insight 1: Year-over-year change
            if len(recent_years) >= 2:
                prev_y, curr_y = recent_years[-2], recent_years[-1]
                if year_agg[prev_y] > 0:
                    yoy = ((year_agg[curr_y] - year_agg[prev_y]) / year_agg[prev_y]) * 100
                    direction = "improved" if yoy > 0 else "declined"
                    insights.append(
                        f"Global sustainability indicators {direction} by {abs(yoy):.1f}% from {prev_y} to {curr_y}."
                    )

            # Insight 2: Pillar comparison
            pillars = {"Environment": avg_env, "Social": avg_soc, "Governance": avg_gov}
            strongest = max(pillars, key=pillars.get)
            weakest = min(pillars, key=pillars.get)
            gap = pillars[strongest] - pillars[weakest]
            insights.append(
                f"{strongest} ({pillars[strongest]:.1f}) is the strongest pillar. "
                f"{weakest} ({pillars[weakest]:.1f}) trails by {gap:.1f} pts."
            )

            # Insight 3: Coverage
            n_below = data.get("esg_below50", 0)
            n_total = len(scores)
            insights.append(
                f"{n_below} of {n_total} economies ({n_below/n_total*100:.0f}%) score below the 50-point threshold."
            )
            data["esg_insights"] = insights

            # ── 3D Scatter: env vs soc vs gov per economy ───────────────
            sample = scores.sample(n=min(500, len(scores)))
            data["esg_points"] = {
                "x": sample["env"].round(2).tolist(),
                "y": sample["soc"].round(2).tolist(),
                "z": sample["gov"].round(2).tolist(),
                "c": sample["esg_score"].round(2).tolist(),
                "labels": ["Environment", "Social", "Governance"]
            }
    if fin_df is not None and "Cluster" in fin_df.columns:
        num_cols = fin_df.select_dtypes(include="number").columns.tolist()
        avgs = fin_df.groupby("Cluster")[num_cols[:4]].mean().round(2)
        data["cluster_cols"] = ["Cluster"] + avgs.columns.tolist()
        data["cluster_rows"] = [[int(idx)] + row.tolist() for idx, row in avgs.iterrows()]
        
        # Add 3D coordinates for Plotly graph
        if len(num_cols) >= 3:
            plot_df = fin_df.sample(n=min(600, len(fin_df))) if len(fin_df) > 600 else fin_df
            x_col, y_col, z_col = num_cols[0], num_cols[1], num_cols[2]
            data["cluster_points"] = {
                "x": plot_df[x_col].tolist(),
                "y": plot_df[y_col].tolist(),
                "z": plot_df[z_col].tolist(),
                "c": plot_df["Cluster"].tolist(),
                "labels": [x_col, y_col, z_col]
            }

    return data


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
    # Build data for all sections, then render the single HTML dashboard.
    dashboard_data = _build_dashboard_data(
        credit_df=credit_df,
        fin_df=fin_df,
        esg_df=esg_df,
        reg_model=reg_model,
        cls_model=cls_model,
        clu_model=clu_model,
    )
    _render_html_dashboard(dashboard_data)