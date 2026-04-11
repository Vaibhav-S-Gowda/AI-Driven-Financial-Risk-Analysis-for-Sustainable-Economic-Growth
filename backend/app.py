import streamlit as st
import os
import sys
import joblib
import numpy as np

# --- System Path Setup ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from data_processor import DataProcessor
from frontend.views.landing import render_landing
from frontend.views.signin import render_signin
from frontend.views.dashboard import render_dashboard
from backend.config import SUSTAINABLE_INDICATORS

# --- Page Configuration ---
st.set_page_config(
    page_title="FinRisk AI Dashboard",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Navigation Logic (resolved BEFORE heavy loading) ---
def get_nav_from_url():
    try:
        val = st.query_params.get("nav", "landing") # defaults to landing
        return val
    except Exception:
        return "landing"

def push_nav_to_url(val: str):
    st.query_params["nav"] = val

if "page" not in st.session_state:
    st.session_state.page = get_nav_from_url()

# --- Fast paths: Landing & Sign-in render instantly (no model loading!) ---
if st.session_state.page == "landing":
    push_nav_to_url("landing")
    render_landing()
    st.stop()

if st.session_state.page == "login":
    push_nav_to_url("login")
    render_signin()
    st.stop()

# --- Dashboard path: show premium FinRisk AI loader while models load ---
LOADING_HTML = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    [data-testid="stSidebar"], [data-testid="stHeader"], footer, #MainMenu, [data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }
    
    .premium-loader-overlay {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: #09090B;
        z-index: 9999999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-family: 'Inter', 'Plus Jakarta Sans', system-ui, sans-serif;
        user-select: none;
    }
</style>
<div class="premium-loader-overlay">

    <!-- Orbital Ring Animation -->
    <div style="position:relative;width:80px;height:80px;margin-bottom:40px">
        <!-- Outer ring -->
        <div style="position:absolute;inset:0;border-radius:50%;border:1.5px solid rgba(255,255,255,0.04)"></div>
        <!-- Orbiting dot -->
        <div style="position:absolute;inset:-2px;border-radius:50%;border:1.5px solid transparent;border-top-color:#3B82F6;animation:orbitSpin 1.8s cubic-bezier(0.5,0,0.5,1) infinite"></div>
        <!-- Inner ring -->
        <div style="position:absolute;inset:12px;border-radius:50%;border:1px solid rgba(255,255,255,0.03)"></div>
        <!-- Inner orbiting dot (counter) -->
        <div style="position:absolute;inset:10px;border-radius:50%;border:1px solid transparent;border-bottom-color:rgba(124,58,237,0.6);animation:orbitSpin 2.4s cubic-bezier(0.5,0,0.5,1) infinite reverse"></div>
        <!-- Center diamond -->
        <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center">
            <div style="width:6px;height:6px;background:#3B82F6;border-radius:1.5px;transform:rotate(45deg);opacity:0.9;animation:centerPulse 2s ease-in-out infinite"></div>
        </div>
    </div>

    <!-- Brand -->
    <div style="font-size:13px;font-weight:600;color:rgba(255,255,255,0.85);letter-spacing:3px;text-transform:uppercase;margin-bottom:8px">FinRisk AI</div>
    <div style="width:24px;height:1px;background:linear-gradient(90deg,transparent,rgba(59,130,246,0.5),transparent);margin-bottom:32px"></div>

    <!-- Status Lines (staggered fade) -->
    <div style="display:flex;flex-direction:column;gap:10px;align-items:center">
        <div style="font-size:11px;color:rgba(255,255,255,0.2);letter-spacing:0.5px;animation:statusFade 3s ease infinite">
            Loading models
        </div>
        <div style="font-size:11px;color:rgba(255,255,255,0.12);letter-spacing:0.5px;animation:statusFade 3s ease 0.8s infinite">
            Processing datasets
        </div>
        <div style="font-size:11px;color:rgba(255,255,255,0.08);letter-spacing:0.5px;animation:statusFade 3s ease 1.6s infinite">
            Building intelligence
        </div>
    </div>

    <!-- Thin progress line at bottom -->
    <div style="position:fixed;bottom:0;left:0;right:0;height:2px;background:rgba(255,255,255,0.02)">
        <div style="height:100%;background:linear-gradient(90deg,#3B82F6,#7C3AED,#3B82F6);background-size:200% 100%;animation:shimmerBar 2s ease-in-out infinite"></div>
    </div>

    <!-- Bottom copyright -->
    <div style="position:fixed;bottom:20px;font-size:10px;color:rgba(255,255,255,0.08);letter-spacing:0.5px">
        RISK INTELLIGENCE PLATFORM
    </div>
</div>

<style>
    @keyframes orbitSpin {
        0%   { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes centerPulse {
        0%, 100% { opacity: 0.4; transform: rotate(45deg) scale(1); }
        50%      { opacity: 1;   transform: rotate(45deg) scale(1.3); }
    }
    @keyframes statusFade {
        0%, 100% { opacity: 0.15; }
        40%, 60% { opacity: 0.5; }
    }
    @keyframes shimmerBar {
        0%   { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
</style>
"""

# Show the loading screen as a placeholder that gets replaced
loader = st.empty()
loader.markdown(LOADING_HTML, unsafe_allow_html=True)

# --- Asset Loading (cached — only runs if dashboard is open) ---
@st.cache_resource
def load_assets():
    processor = DataProcessor()
    credit_df = processor.load_credit_risk_data()
    credit_df = processor.preprocess_credit_risk(credit_df, training=True)
    fin_df = processor.load_financial_data()
    esg_df = processor.load_esg_data()
    esg_df = esg_df[esg_df["Indicator name"].isin(SUSTAINABLE_INDICATORS)]
    
    base_dir = os.path.dirname(__file__)
    reg_model = joblib.load(os.path.join(base_dir, "models", "regression_model.pkl"))
    cls_model = joblib.load(os.path.join(base_dir, "models", "classification_model.pkl"))
    clu_model = joblib.load(os.path.join(base_dir, "models", "clustering_model.pkl"))
    clu_scaler = joblib.load(os.path.join(base_dir, "models", "clustering_scaler.pkl"))
    
    return processor, credit_df, fin_df, esg_df, reg_model, cls_model, clu_model, clu_scaler

try:
    processor, credit_df, fin_df, esg_df, reg_model, cls_model, clu_model, clu_scaler = load_assets()
except Exception as e:
    loader.empty()
    st.error(f"Error loading assets: {e}")
    st.stop()

# Clear the loading screen and render the dashboard
loader.empty()

push_nav_to_url("dashboard")
render_dashboard(
    processor, credit_df, fin_df, esg_df,
    reg_model, cls_model, clu_model, clu_scaler
)