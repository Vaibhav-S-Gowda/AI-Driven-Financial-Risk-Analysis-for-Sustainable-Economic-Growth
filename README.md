# AI-Driven Financial Risk Analysis for Sustainable Economic Growth

An intelligent framework built to analyze and predict financial risks, supporting stable and sustainable economic growth. Built with Streamlit, Scikit-Learn, and Plotly.

## 🚀 Key Features

- **Risk Score Predictor (Regression)**: Predicts a composite financial risk score for loan applicants.
- **Monte Carlo Simulation**: Provides stochastic risk intervals (95% confidence) to account for model and market volatility.
- **Financial Distress Classifier (Classification)**: Identifies high probability of loan default.
- **Market Behavior Analyzer (Clustering)**: Segments customers based on financial and behavioral indicators.
- **Sustainable Economic Growth Dashboard**: Filtered ESG visualizations focusing on GDP, Energy, and Environmental metrics (SDG 8 & 9).
- **Premium UI**: Modern dark-themed dashboard with curated CSS styles.

## 🛠️ Tech Stack

- **ML**: Scikit-Learn (Random Forest, K-Means)
- **Data**: Pandas, Numpy, Openpyxl
- **UI**: Streamlit, Custom CSS
- **Visuals**: Plotly Express

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
