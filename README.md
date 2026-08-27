# Tamil Nadu Rice Yield Prediction & Agricultural Decision Support System

An end-to-end Machine Learning, Time-Series Forecasting, and Explainable AI (SHAP) decision support platform tailored for Tamil Nadu rice farming.

---

## 🌾 Project Overview

This system predicts year-wise **Rice Yield (tonnes/ha)** for 30 Tamil Nadu districts based on historical seasonal climate data, soil properties, and agricultural inputs (1997–2023). It incorporates **SHAP (SHapley Additive exPlanations)** for transparent model decisions, a **District Historical Condition Insights Engine** for risk alerts, and a **Bilingual Farmer UI** with Tamil voice output.

### 🌟 Key System Highlights
- **Strict Chronological Data Splitting**: Trained on 1997–2018, validated on 2019–2021, and tested on unseen 2022–2023 data (no future data leakage).
- **Seasonal Features Integrity**: Preserves separate Kharif, Rabi, and Zaid seasonal averages without invalid re-aggregation.
- **Genuine SHAP Explainability**: Decomposes every individual yield prediction into positive and negative feature contributions.
- **District Condition Insights**: Compares farmer inputs against district-specific historical distribution quantiles ($p_{10}, p_{25}, p_{75}, p_{90}$) without altering ML model outputs.
- **Seasonal Weather Forecasting**: Employs Exponential Smoothing & Moving Averages with historical backtesting (2019–2021) for future-year prediction (2024–2030).
- **Bilingual Interface & Tamil Voice**: Full English + Tamil interface with Web Speech API text-to-speech engine.

---

## 🏗️ Project Architecture

```
                 TAMIL NADU RICE YIELD DECISION SYSTEM
                                   |
         +-------------------------+-------------------------+
         |                                                   |
  YIELD PREDICTION ENGINE                             HISTORICAL INSIGHTS
         |                                                   |
  ML Model (Extra Trees / Gradient Boosting)          Historical Percentile Range
         |                                                   |
  Predicted Yield (tonnes/ha)                         Condition Status & Risk Advice
         |                                                   |
         +-------------------------+-------------------------+
                                   |
                          SHAP EXPLAINABILITY
                                   |
                     FastAPI REST Backend (Port 8000)
                                   |
                  Farmer Web Interface (Port 3000)
                                   |
                           Tamil Voice Output
```

---

## 📊 Dataset Audit Summary (`DS_Final_1997_2023(1).xlsx`)

- **Total Records:** 810 rows, 26 columns (30 districts × 27 years)
- **Year Range:** 1997 – 2023
- **Target Variable:** `Yield` (Mean = 3.57 tonnes/ha, Std = 1.01 tonnes/ha)
- **Data Quality Fixes:**
  - 25 rows missing `Yield` filtered during ML training.
  - Domain bound checks: invalid `Kharif Humidity = 67087.0%` anomaly corrected to NaN before median imputation.
  - Standardized text: `coastal alluviam` $\rightarrow$ `coastal alluvium`.

---

## 📈 ML Model Performance Comparison (Phase 5)

Evaluated on unseen historical test years (2022–2023):

| Model | Validation MAE | Validation $R^2$ | Test MAE (tonnes/ha) | Test $R^2$ | Overfit $R^2$ Gap |
|---|---|---|---|---|---|
| **Extra Trees (Tuned)** 🏆 | 0.5192 | 0.4182 | **0.2819** | **0.6517** | 0.387 |
| **Random Forest (Tuned)** | 0.5246 | 0.4042 | **0.2952** | **0.6439** | 0.381 |
| **Gradient Boosting (Tuned)** | 0.5287 | 0.4015 | **0.2894** | **0.6346** | 0.395 |
| **Lasso Regression** | 0.5821 | 0.2590 | 0.4010 | 0.3858 | 0.126 |
| **Linear Regression** | 0.5497 | 0.3850 | 0.4848 | 0.1261 | 0.122 |

---

## 🔮 Weather Forecaster Backtesting (Phase 9–12)

Backtested by training on 1997–2018 weather trajectories and forecasting 2019–2021 across 15 seasonal variables:

- **Exponential Smoothing ($\alpha=0.3$):** MAE = 7.91, RMSE = 20.10, **MAPE = 16.3%**
- **5-Year Moving Average:** MAE = 8.24, RMSE = 20.11, **MAPE = 18.0%**
- **Linear Trend:** MAE = 8.56, RMSE = 21.34, **MAPE = 19.0%**

---

## 🚀 How to Run the Application

### 1. Prerequisites
Ensure Python 3.10+ is installed with required packages:
```bash
pip install pandas numpy scikit-learn shap fastapi uvicorn joblib statsmodels openpyxl
```

### 2. Start Backend API Server
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Start Frontend Web Server
```bash
python -m http.server 3000 --directory frontend
```
- Open Web Interface: [http://127.0.0.1:3000](http://127.0.0.1:3000)

---

## 📁 Repository Structure

```
Rice_Yield_Prediction/
├── data/
│   ├── raw/                           # Original Excel dataset (pristine)
│   └── processed/                     # Cleaned dataset & numpy train/val/test splits
├── src/
│   ├── preprocessing/                 # Dataset audit, cleaning, and sklearn pipeline
│   ├── models/                        # ML regression model training and comparison
│   ├── forecasting/                   # Time-series weather forecasters & backtesting
│   ├── insights/                      # Historical condition distribution engine
│   ├── explainability/                # SHAP global and local explainer
│   ├── crop_health/                   # Rule-based crop health advisor
│   └── inference.py                   # Unified prediction engine
├── models/                            # Saved .joblib model & pipeline artifacts
├── outputs/                           # Audit JSON reports, metrics, & comparison tables
├── backend/app/main.py                # FastAPI REST endpoints
├── frontend/                          # HTML, CSS glassmorphism, & JS with Tamil Voice
└── README.md
```
