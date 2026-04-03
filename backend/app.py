import streamlit as st
import os
import sys
import joblib

# Ensure sibling modules in backend/ are importable regardless of cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_processor import DataProcessor
from monte_carlo import MonteCarloSimulator

# Include the parent directory in sys.path to resolve frontend module
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from frontend.views.landing import render_landing
from frontend.views.signin import render_signin
from frontend.views.dashboard import render_dashboard
from backend.config import SUSTAINABLE_INDICATORS

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinRisk AI Dashboard",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Inject CSS ───────────────────────────────────────────────────────────────
css_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── Load Assets ──────────────────────────────────────────────────────────────
@st.cache_resource
def load_assets():
    processor  = DataProcessor()
    credit_df  = processor.load_credit_risk_data()
    processor.preprocess_credit_risk(credit_df, training=True)
    fin_df     = processor.load_financial_data()
    esg_df     = processor.load_esg_data()
    esg_df     = esg_df[esg_df["Indicator name"].isin(SUSTAINABLE_INDICATORS)]
    base_dir   = os.path.dirname(__file__)
    reg_model  = joblib.load(os.path.join(base_dir, "models", "regression_model.pkl"))
    cls_model  = joblib.load(os.path.join(base_dir, "models", "classification_model.pkl"))
    clu_model  = joblib.load(os.path.join(base_dir, "models", "clustering_model.pkl"))
    clu_scaler = joblib.load(os.path.join(base_dir, "models", "clustering_scaler.pkl"))
    mc_sim     = MonteCarloSimulator(reg_model)
    return processor, credit_df, fin_df, esg_df, reg_model, cls_model, clu_model, clu_scaler, mc_sim

try:
    processor, credit_df, fin_df, esg_df, reg_model, cls_model, clu_model, clu_scaler, mc_simulator = load_assets()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading assets: {e}")
    st.stop()

# ─── URL Routing (safe, no experimental APIs) ─────────────────────────────────
def get_nav_from_url():
    try:
        val = st.query_params.get("nav", None)
        if isinstance(val, list):
            return val[0] if val else None
        return val
    except Exception:
        return None

def push_nav_to_url(val: str):
    try:
        st.query_params["nav"] = val
    except Exception:
        pass

nav_val = get_nav_from_url()
if nav_val in ("landing", "login", "dashboard"):
    st.session_state.setdefault("page", nav_val)
    if st.session_state["page"] != nav_val:
        st.session_state["page"] = nav_val

st.session_state.setdefault("page", "landing")
push_nav_to_url(st.session_state["page"])

# ─── Render Appropriate View ──────────────────────────────────────────────────
if st.session_state.page == "landing":
    render_landing()
elif st.session_state.page == "login":
    render_signin()
elif st.session_state.page == "dashboard":
    render_dashboard(
        processor, 
        credit_df, 
        fin_df, 
        esg_df, 
        reg_model, 
        cls_model, 
        clu_model, 
        clu_scaler, 
        mc_simulator
    )