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

# --- Asset Loading (cached to avoid reloading 130MB of models on every interaction) ---
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
    st.error(f"Error loading assets: {e}")
    st.stop()

# --- Navigation Logic ---
def get_nav_from_url():
    try:
        val = st.query_params.get("nav", "dashboard")
        return val
    except Exception:
        return "dashboard"

def push_nav_to_url(val: str):
    st.query_params["nav"] = val

# Sync session state with URL
if "page" not in st.session_state:
    st.session_state.page = get_nav_from_url()

# --- Rendering Views ---
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
        clu_scaler
    )

# Ensure URL matches state
push_nav_to_url(st.session_state.page)