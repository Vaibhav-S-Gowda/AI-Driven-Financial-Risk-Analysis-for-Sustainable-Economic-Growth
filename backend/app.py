import streamlit as st
import os
import sys
import joblib
import numpy as np

# --- System Path Setup ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from data_processor import DataProcessor
from monte_carlo import MonteCarloSimulator
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

# --- CSS Injection ---
css_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Asset Loading ---
@st.cache_resource
def load_assets():
    processor = DataProcessor()
    credit_df = processor.load_credit_risk_data()
    processor.preprocess_credit_risk(credit_df, training=True)
    fin_df = processor.load_financial_data()
    esg_df = processor.load_esg_data()
    esg_df = esg_df[esg_df["Indicator name"].isin(SUSTAINABLE_INDICATORS)]
    
    base_dir = os.path.dirname(__file__)
    reg_model = joblib.load(os.path.join(base_dir, "models", "regression_model.pkl"))
    cls_model = joblib.load(os.path.join(base_dir, "models", "classification_model.pkl"))
    clu_model = joblib.load(os.path.join(base_dir, "models", "clustering_model.pkl"))
    clu_scaler = joblib.load(os.path.join(base_dir, "models", "clustering_scaler.pkl"))
    
    mc_sim = MonteCarloSimulator(reg_model)
    return processor, credit_df, fin_df, esg_df, reg_model, cls_model, clu_model, clu_scaler, mc_sim

try:
    processor, credit_df, fin_df, esg_df, reg_model, cls_model, clu_model, clu_scaler, mc_simulator = load_assets()
except Exception as e:
    st.error(f"Error loading assets: {e}")
    st.stop()

# --- Navigation Logic ---
def get_nav_from_url():
    try:
        val = st.query_params.get("nav", "landing")
        return val
    except Exception:
        return "landing"

def push_nav_to_url(val: str):
    st.query_params["nav"] = val

# Sync session state with URL
if "page" not in st.session_state:
    st.session_state.page = get_nav_from_url()

# --- Simulation Logic (Integrated from Backend) ---
def run_gbm_simulation(initial_investment, years, annual_return, volatility, inflation_rate, num_simulations, monthly_contribution=0.0):
    dt = 1 / 12
    steps = int(years * 12)
    mu = annual_return / 100
    sigma = volatility / 100
    inf = inflation_rate / 100

    real_mu = (1 + mu) / (1 + inf) - 1
    nom_drift = (mu - 0.5 * sigma ** 2) * dt
    real_drift = (real_mu - 0.5 * sigma ** 2) * dt
    diffusion = sigma * np.sqrt(dt)

    nom_paths = np.zeros((num_simulations, steps + 1))
    real_paths = np.zeros((num_simulations, steps + 1))
    nom_paths[:, 0] = initial_investment
    real_paths[:, 0] = initial_investment

    Z = np.random.standard_normal((num_simulations, steps))

    for t in range(steps):
        nom_paths[:, t + 1] = (nom_paths[:, t] * np.exp(nom_drift + diffusion * Z[:, t]) + monthly_contribution)
        real_paths[:, t + 1] = (real_paths[:, t] * np.exp(real_drift + diffusion * Z[:, t]) + monthly_contribution)

    return nom_paths, real_paths

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
        clu_scaler, 
        mc_simulator
    )

# Ensure URL matches state
push_nav_to_url(st.session_state.page)