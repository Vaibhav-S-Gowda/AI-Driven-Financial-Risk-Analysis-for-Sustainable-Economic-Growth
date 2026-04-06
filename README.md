# AI Financial Risk Analysis using Monte Carlo Simulation | Sustainable Economic Growth

An AI-powered financial risk analysis system that uses machine learning and Monte Carlo simulation to predict risk, detect loan defaults, and support sustainable economic growth. Built with Streamlit, Scikit-Learn, and Plotly for interactive analytics and visualization.

---

## 🚀 Key Features

- AI Risk Score Prediction (Regression)  
  Predicts financial risk scores using machine learning models.

- Monte Carlo Simulation for Risk Analysis  
  Runs multiple simulations to estimate uncertainty and provide 95% confidence intervals.

- Loan Default Prediction (Classification)  
  Identifies high-risk applicants using classification models.

- Customer Segmentation (Clustering)  
  Uses K-Means to group users based on financial behavior and patterns.

- ESG & Economic Growth Dashboard  
  Visualizes sustainability indicators like GDP, energy usage, and environmental metrics (SDG 8 & 9).

- Interactive Dashboard UI  
  Clean, modern dark-themed interface built with Streamlit and Plotly.

---

## 🛠️ Tech Stack

- Machine Learning: Scikit-Learn (Random Forest, K-Means)  
- Data Processing: Pandas, NumPy, Openpyxl  
- Frontend/UI: Streamlit, Custom CSS  
- Visualization: Plotly Express  

---

## 📂 Project Structure

- `app.py`: Main Streamlit application.
- `data_processor.py`: Core logic for data cleaning, feature engineering, and ESG reshaping.
- `style.css`: Custom premium styling.
- `models/`: Directory containing trained ML models and the data processor.
- `credit_risk_dataset.csv`: Source for risk and classification models.
- `financial_dataset.csv`: Source for market behavior clustering.
- `esgdata_download-2026-01-09.xlsx`: Source for economic stability trends.

## 🏁 How to Run

1. **Install Dependencies**:
   ```bash
   pip install streamlit pandas numpy scikit-learn plotly openpyxl joblib
   ```

2. **Run the Dashboard**:
   ```bash
   streamlit run app.py
   ```

## 📊 Methodology

1. **Preprocessing**: Missing values are imputed via median strategy. Categorical fields are label-encoded. Time-series data from Excel is melted and filtered for sustainable growth indicators.
2. **Regression**: Uses Random Forest Regressor to predict a weighted risk score derived from interest rates and income ratios.
3. **Monte Carlo Simulation**: Runs 1000 iterations to generate a distribution of risk scores, providing a 95% confidence interval for better decision support.
4. **Classification**: Uses Random Forest Classifier to detect `loan_status` (defaults).
5. **Clustering**: Employs K-Means on behavioral features like Savings Ratio and Spending Score to segment market participants.


---

## 🎯 Use Cases

- Financial risk assessment  
- Loan approval systems  
- Investment risk analysis  
- Sustainable economic planning  
- ESG data insights  

---

## 🔑 Keywords

AI Financial Risk Analysis, Monte Carlo Simulation, Machine Learning Finance, Risk Prediction, ESG Analytics, Sustainable Finance, Loan Default Prediction, Data Science Project

---

## ⭐ Why This Project?

This project combines AI and simulation techniques to move beyond traditional financial analysis. By modeling uncertainty and risk dynamically, it helps users make smarter, data-driven financial decisions for long-term sustainability.




------------------------------------------------------------------





# FinRisk AI — Monte Carlo Dashboard
### AI-Driven Financial Risk Analysis for Sustainable Economic Growth

A professional, Dappr-inspired financial dashboard that simulates portfolio risk using **Geometric Brownian Motion (GBM) Monte Carlo simulation** — entirely in the browser, with an optional Python Flask backend for server-side computation.

---

## 📁 Project Structure

```
finrisk/
├── backend/
│   ├── app.py              ← Flask Monte Carlo API server
│   └── requirements.txt    ← Python dependencies
├── frontend/
│   └── index.html          ← Complete single-file dashboard
└── README.md
```

---

## 🚀 Running Locally

### Option A — Browser Only (no backend needed)
The Monte Carlo engine runs entirely in JavaScript. Just open the file:
```bash
open frontend/index.html
# or on Windows:
start frontend/index.html
```
The simulation auto-runs on page load with default parameters.

---

### Option B — With Flask Backend (recommended for >2000 sims)

**Step 1 — Set up Python environment**
```bash
cd backend
python -m venv venv

# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

**Step 2 — Start the Flask server**
```bash
python app.py
# Server starts at http://localhost:5000
```

**Step 3 — Open the dashboard**
```bash
open ../frontend/index.html
```
The frontend automatically detects the backend at `localhost:5000` and uses it. If the backend is unavailable, it silently falls back to the JS engine.

**Step 4 — Verify the backend is working**
```
GET http://localhost:5000/health
→ {"status": "ok", "service": "FinRisk AI Backend"}
```

---

## ⚙️ How to Use the Dashboard

1. **Configure parameters** in the right panel (Scenario A):
   - Initial investment, time horizon, expected return, volatility, inflation, simulations, monthly contribution

2. **Click "Run Simulation"** — results appear instantly

3. **Switch tabs** between Nominal and Real (inflation-adjusted) paths

4. **Expand "Compare Scenario B"** to set a second parameter set and see side-by-side results

5. **Read AI Insights** in the right panel for automated risk commentary

---

## 📐 How Monte Carlo Simulation Works Here

### Model: Geometric Brownian Motion

Each simulation path follows the SDE:

```
dS = S · (μ dt + σ dW)
```

In discrete form (monthly steps):
```
S(t+1) = S(t) · exp((μ − ½σ²)·dt + σ·√dt·Z) + monthly_contribution
```

Where:
- `S` = portfolio value
- `μ` = expected annual return
- `σ` = annual volatility
- `dt` = 1/12 (monthly time step)
- `Z ~ N(0,1)` = standard normal random variable (Box-Muller in JS)

### Process
1. For each of the N simulations, draw a full path of monthly random shocks
2. Aggregate all terminal values into a distribution
3. Compute percentile bands (P5, P25, P50, P75, P95)
4. Derive risk metrics from the distribution

### Risk Metrics Computed
| Metric | Description |
|--------|-------------|
| Mean / Median | Expected and typical final values |
| P5 / P95 | Worst / best case (5th/95th percentile) |
| Std Deviation | Spread of outcomes |
| Prob. of Loss | % of paths ending below initial investment |
| VaR (95%) | Maximum expected loss at 95% confidence |
| Real values | All above adjusted for inflation via Fisher equation |

---

## 🌐 Deployment

### Frontend → Vercel (free)
```bash
# Install Vercel CLI
npm i -g vercel

cd frontend
vercel deploy
# Follow prompts → your dashboard is live at vercel.app URL
```

Or drag-and-drop `frontend/` folder at https://vercel.com/new

---

### Backend → Render (free tier)

1. Push the `backend/` folder to a GitHub repository
2. Go to https://render.com → New → Web Service
3. Connect your repo
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3.11
5. Deploy → copy your URL (e.g. `https://finrisk-api.onrender.com`)
6. In `frontend/index.html`, update line:
   ```js
   const BACKEND_URL = "https://finrisk-api.onrender.com";
   ```
7. Redeploy frontend

---

### Backend → Railway (alternative)
```bash
npm install -g @railway/cli
railway login
cd backend
railway init
railway up
# Copy the deployment URL and update BACKEND_URL in index.html
```

---

## 🔧 Customisation

### Change default parameters
Edit the `<input>` default `value` attributes in `frontend/index.html`

### Add more simulations
Max is set to 5000 on the backend. Increase in `app.py`:
```python
n_sims = min(int(d.get("num_simulations", 1000)), 10000)
```

### Change chart colours
Edit the CSS variables at the top of `index.html`:
```css
:root {
  --green: #10B981;
  --blue:  #3B82F6;
  /* etc. */
}
```

---

## 🛡️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JS |
| Charts | Chart.js 4.4 |
| Fonts | Plus Jakarta Sans (Google Fonts) |
| Backend (optional) | Python 3.11, Flask 3.0, NumPy |
| Hosting | Vercel (frontend) + Render/Railway (backend) |

---

## 📝 Notes

- The JS engine uses a **Box-Muller transform** for normally distributed random numbers
- The Flask backend uses **NumPy's vectorised operations** for 10× faster simulation
- All paths are computed server-side for >1000 simulations when backend is available
- Inflation adjustment uses the **Fisher equation**: real_return = (1+nominal)/(1+inflation) − 1