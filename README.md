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
