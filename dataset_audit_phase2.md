# Comprehensive Dataset Audit: Existing 1997–2023 Tamil Nadu Rice Yield Dataset
## Dataset: `DS_Final_1997_2023(1).xlsx` (Sheet: `ML_Dataset`)
**Project:** Spatio-Temporal Rice Yield Prediction Using Long Short-Term Memory (LSTM)  
**Primary Study Region:** Tamil Nadu, India  
**Date of Audit:** October 13, 2026  
**Audit Protocol:** Read-Only Verification (No files modified, no imputation applied, no models trained)

---

## 1. Executive Summary

A comprehensive, programmatic, read-only audit of the primary tabular dataset `DS_Final_1997_2023(1).xlsx` was conducted. The workbook contains a single worksheet titled `ML_Dataset`, comprising **810 district-year records across 26 columns**, spanning the 27-year period from **1997 to 2023** for **30 Tamil Nadu districts**.

### Key Findings
1. **Panel Structure:** The dataset forms an ostensibly balanced spatio-temporal grid of $30 \text{ districts} \times 27 \text{ years} = 810 \text{ records}$. There are **zero duplicate district-year combinations**.
2. **Missing Yield Records (25 rows / 3.09%):**
   * **Chennai (21 rows missing):** Chennai is a dense urban metropolitan district with virtually no agricultural paddy cultivation. In 21 of 27 years, its yield is `NaN` (and in 2021 it is `0.0`).
   * **Krishnagiri (4 rows missing: 2001–2004):** Krishnagiri was officially carved out of Dharmapuri district in 2004; agricultural statistics prior to 2004 were recorded under Dharmapuri.
   * **The remaining 28 agricultural districts have 100% complete yield records across all 27 years.**
3. **Severe Data Corruption Discovered:**
   * **Row 622 (`Thiruvarur`, Year 1998):** `Kharif Humidity` is recorded as **`67087.0`** (an extreme typographical corruption; relative humidity cannot exceed 100%).
4. **Target Leakage Audit:**
   * **No `Production` column exists** in the dataset.
   * `Area` is present, but without `Production`, it does not mathematically leak `Yield = Production / Area`.
   * However, `Yield` represents annual yield, whereas the 15 climate features represent full-year seasonal aggregates (Kharif, Rabi, and Zaid). Using post-harvest Rabi and Zaid weather to predict annual yield is valid for *post-season hindcasting / spatial estimation*, but would constitute *temporal lookahead* if framed as a pre-season forecasting system.
5. **Static Features:**
   * Variables `Soil_PH`, `P`, `K`, `Fertilizer`, and `Pesticide` have **exactly 1 unique value per district** across all 27 years. They function as static district identifiers rather than annual dynamic measurements.
   * `Soil_Type` contains a typographical inconsistency: `'coastal alluvium'` (66 rows) vs `'coastal alluviam'` (15 rows in Nagapattinam).
6. **LSTM Feasibility:**
   * With only 28 valid agricultural districts over 27 years (effective $N \approx 756$ observations), the dataset is small for deep sequential architectures. An LSTM will require tight regularization and must be compared against strong tabular baselines (Ridge, Random Forest, XGBoost).

---

## 2. Task 1: Workbook Structure & Grid Inventory

### Worksheet Overview
* **Worksheet Name:** `ML_Dataset`
* **Total Rows:** 811 (1 header row + 810 data rows)
* **Total Columns:** 26
* **Temporal Range:** 1997 to 2023 (27 consecutive years)
* **Districts Represented:** 30 unique districts

### Column Schema & Data Types

| # | Column Name | Raw Data Type | Inferred Type | Semantic Description |
| :-: | :--- | :---: | :---: | :--- |
| 1 | `District` | `str` | Categorical | Administrative district name |
| 2 | `Year` | `int64` | Temporal Index | Calendar / Agricultural year (1997–2023) |
| 3 | `Kharif Temperature` | `float64` | Continuous | Mean temperature during Kharif season (°C) |
| 4 | `Kharif Rainfall` | `float64` | Continuous | Cumulative/mean rainfall during Kharif (mm) |
| 5 | `Kharif Humidity` | `float64` | Continuous | Mean relative humidity during Kharif (%) |
| 6 | `Kharif Wind_Speed` | `float64` | Continuous | Mean wind speed during Kharif (m/s) |
| 7 | `Kharif Soil_Moisture` | `float64` | Continuous | Root-zone/surface soil moisture during Kharif (fraction) |
| 8 | `Rabi Temperature` | `float64` | Continuous | Mean temperature during Rabi season (°C) |
| 9 | `Rabi Rainfall` | `float64` | Continuous | Cumulative/mean rainfall during Rabi (mm) |
| 10 | `Rabi Humidity` | `float64` | Continuous | Mean relative humidity during Rabi (%) |
| 11 | `Rabi Wind_Speed` | `float64` | Continuous | Mean wind speed during Rabi (m/s) |
| 12 | `Rabi Soil_Moisture` | `float64` | Continuous | Soil moisture during Rabi (fraction) |
| 13 | `Zaid Temperature` | `float64` | Continuous | Mean temperature during Zaid season (°C) |
| 14 | `Zaid Rainfall` | `float64` | Continuous | Cumulative/mean rainfall during Zaid (mm) |
| 15 | `Zaid Humidity` | `float64` | Continuous | Mean relative humidity during Zaid (%) |
| 16 | `Zaid Wind_Speed` | `float64` | Continuous | Mean wind speed during Zaid (m/s) |
| 17 | `Zaid Soil_Moisture` | `float64` | Continuous | Soil moisture during Zaid (fraction) |
| 18 | `Soil_PH` | `float64` | Static Numeric | District soil pH (6.5 to 8.3) |
| 19 | `Soil_Type` | `str` | Static Categorical | Primary soil classification (11 categories) |
| 20 | `N` | `int64` | Static Numeric | Soil available Nitrogen ($kg/ha$) |
| 21 | `P` | `int64` | Static Numeric | Soil available Phosphorus ($kg/ha$) |
| 22 | `K` | `int64` | Static Numeric | Soil available Potassium ($kg/ha$) |
| 23 | `Fertilizer` | `int64` | Static Numeric | Fertilizer consumption ($kg/ha$) |
| 24 | `Pesticide` | `float64` | Static Numeric | Pesticide application rate ($kg/ha$) |
| 25 | `Area` | `float64` | Continuous | Cultivated rice area in hectares ($ha$) |
| 26 | `Yield` | `float64` | Continuous Target | Annual rice yield in metric tonnes per hectare ($t/ha$) |

### District Inventory & Record Counts
Every one of the 30 districts has exactly **27 records** (1 per year from 1997 to 2023):
* *Northern & Coastal:* Chennai (27), Kancheepuram (27), Thiruvallur (27), Cuddalore (27), Villupuram (27), Vellore (27), Thiruvannamalai (27).
* *Cauvery Delta:* Thanjavur (27), Thiruvarur (27), Nagapattinam (27), Tiruchirappalli (27), Karur (27), Perambalur (27), Pudukkottai (27).
* *Western Zone:* Coimbatore (27), Erode (27), Salem (27), Namakkal (27), Dharmapuri (27), Krishnagiri (27), The Nilgiris (27).
* *Southern Zone:* Madurai (27), Dindigul (27), Theni (27), Ramanathapuram (27), Sivagangai (27), Virudhunagar (27), Tirunelveli (27), Thoothukudi (27), Kanyakumari (27).

**Duplicate District-Year Combinations:** Exactly **0** duplicates found.

---

## 3. Task 2: Data Quality, Corruptions, & Unit Verification

### Missing Data Analysis

| Column Name | Missing Count | Missing % | Affected Districts & Explanation |
| :--- | :---: | :---: | :--- |
| `Yield` | **25** | **3.09%** | Chennai (21 years: 2001–2018, 2019, 2020, 2022); Krishnagiri (4 years: 2001–2004, prior to district bifurcation). |
| `Area` | **23** | **2.84%** | Chennai (19 years: 2001–2018, 2022); Krishnagiri (4 years: 2001–2004). |
| `Kharif Temperature` | 15 | 1.85% | Madurai (11 years), Chennai (4 years). |
| `Kharif Humidity` | 15 | 1.85% | Madurai (11 years), Chennai (4 years). |
| `Kharif Wind_Speed` | 15 | 1.85% | Madurai (11 years), Chennai (4 years). |
| `Kharif Soil_Moisture` | 15 | 1.85% | Madurai (11 years), Chennai (4 years). |
| `Rabi Temperature` | 11 | 1.36% | Madurai (11 years). |
| `Rabi Humidity` | 11 | 1.36% | Madurai (11 years). |
| `Rabi Wind_Speed` | 11 | 1.36% | Madurai (11 years). |
| `Rabi Soil_Moisture` | 11 | 1.36% | Madurai (11 years). |
| `Zaid Temperature` | 15 | 1.85% | Madurai (11 years), Chennai (4 years). |
| `Zaid Humidity` | 15 | 1.85% | Madurai (11 years), Chennai (4 years). |
| `Zaid Wind_Speed` | 12 | 1.48% | Madurai (11 years), Chennai (1 year). |
| `Zaid Soil_Moisture` | 15 | 1.85% | Madurai (11 years), Chennai (4 years). |
| *All other 12 columns* | **0** | **0.00%** | Completely populated (including all Rainfall and soil columns). |

### Numerical Anomalies & Corruptions

1. **Catastrophic Outlier in Relative Humidity:**
   * **Row 622 (`Thiruvarur`, Year 1998):** `Kharif Humidity = 67087.0`.
   * *Assessment:* Physics dictates relative humidity must lie in the range $[0\%, 100\%]$. The typical Kharif humidity in Thiruvarur is $\sim 67\%\text{--}75\%$. This entry is a typographical error where $67.087$ was entered without a decimal point. It will distort neural network activations and gradient calculations unless handled.
2. **Soil Type Typographical Inconsistency:**
   * Nagapattinam contains `'coastal alluviam'` for years 1997–2000 and 2006 (15 rows), while other rows use `'coastal alluvium'` (66 rows). These represent the same physical class but will be split into two separate categories by one-hot encoders unless normalized.
3. **Verified Genuine Zero-Yield vs. Missing Data:**
   * **Chennai (2021):** `Area = 108.0 ha`, `Yield = 0.0 t/ha`. Reflects negligible/abandoned urban crop production.
   * **Ramanathapuram (2017):** `Area = 121,849.0 ha`, `Yield = 0.0 t/ha`.
   * *Critical Verification:* In 2016–2017, Tamil Nadu suffered the worst Northeast Monsoon failure in 140 years (62% rainfall deficit). In rainfed coastal Ramanathapuram, drought led to complete paddy crop failure across >120,000 hectares. This `0.0` is a **genuine physical crop disaster**, confirmed by historical drought records (and adjacent drought years: 2004 = 0.17 t/ha, 2008 = 0.24 t/ha, 2014 = 0.30 t/ha, 2018 = 0.28 t/ha). It must **not** be treated as missing data.

### Unit & Target Verification
* **Target `Yield`:** Mean is $3.57$, standard deviation is $1.25$, median is $3.65$, range is $0.00$ to $9.89$. In Indian agricultural statistics, state-level rice yield is typically reported in $kg/ha$ (around 3,000–4,000 kg/ha) or metric tonnes per hectare ($t/ha$). Here, the values are scaled in **metric tonnes per hectare ($t/ha$)**.
* **Feature `Area`:** Mean is $65,140.4\text{ ha}$, range is $32\text{ ha}$ to $225,837\text{ ha}$. Clearly recorded in **hectares ($ha$)**.
* **Target Origin:** Because `Production` is omitted from the workbook, `Yield` represents the **directly recorded historical yield figure** from the state Department of Economics and Statistics (DES) / Season and Crop Reports.

---

## 4. Task 3: Target Leakage Assessment

Target leakage occurs when an algorithm has access to information during training or testing that would not be available in real-world deployment, creating illusory predictive performance.

### Analysis of Candidate Predictors

| Feature | Leakage Risk Level | Verification & Mechanism | Recommendation |
| :--- | :---: | :--- | :--- |
| **`Production`** | **None (Absent)** | There is no production column in `ML_Dataset`. Thus, algebraic reconstruction ($Yield = Production / Area$) cannot occur. | N/A (Confirmed absent). |
| **`Area`** | **Low to Moderate** | Area represents the total acreage sown/harvested in the district. It does not algebraically leak yield. However, final harvested area is finalized post-harvest. | Retain as pre-season acreage proxy, but test models with and without `Area`. |
| **`Kharif` Climate Features** | **None** | Occurs from June to September. Available prior to the main Samba harvest. | Legitimate predictor. |
| **`Rabi` Climate Features** | **Temporal Dependency** | Occurs from October to December. The main Tamil Nadu rice crop (Samba/Thaladi) is harvested in January–February. | Legitimate for end-of-season yield estimation; unavailable for pre-sowing forecasts. |
| **`Zaid` Climate Features** | **Temporal Lookahead** | Occurs from January to May (Summer / Navarai season). If predicting annual aggregate rice yield (which predominantly reflects the Samba crop harvested in Feb), including May weather represents future information. | Must be evaluated carefully; flag as lookahead if modeling pre-harvest Samba yield. |
| **Soil Properties (`Soil_PH`, `N`, `P`, `K`, `Fertilizer`, `Pesticide`)** | **None (Static Constants)** | Exactly 1 unique value per district across all 27 years. They encode static district soil endowments. | Legitimate static features (or can be replaced with district embeddings). |

---

## 5. Task 4: Temporal & Spatial Validation Feasibility

### Feasibility of Chronological Holdout
A chronological split is not only feasible, but mandatory to prevent temporal autocorrelation leakage:
* **Training Partition:** **1997–2017** (21 years, $\sim 77.8\%$ of data, 630 district-year slots).
* **Validation Partition:** **2018–2020** (3 years, $\sim 11.1\%$ of data, 90 district-year slots) — used for hyperparameter tuning and LSTM early stopping.
* **Test Partition:** **2021–2023** (3 years, $\sim 11.1\%$ of data, 90 district-year slots) — held-out final evaluation.

### Panel Balance & Missing District-Years
1. **Urban Exclusion (Chennai):** Chennai has missing yield in 21 of 27 years and negligible rice farming. **Chennai should be excluded from agricultural model training and evaluation**, leaving **29 agricultural districts**.
2. **Krishnagiri Bifurcation (2001–2004):** Krishnagiri was formed in 2004 from Dharmapuri. For the years 2001–2004, its yield can either be imputed from Dharmapuri's historical yield or omitted during training.
3. **Effective Clean Sample Size:** Excluding Chennai leaves $29 \times 27 = 783$ potential district-year records, of which 779 have valid ground-truth yields.

### Is the Dataset Large Enough for an LSTM?
* **Statistical Reality:** 29 districts $\times$ 27 annual time steps is **extremely small** for deep sequence models. If using a sliding window lookback of $T = 3$ to $5$ years, the total number of training sequence samples is only:
  $$N_{\text{samples}} \approx 29 \times (21 - T + 1) \approx 29 \times 17 \approx 493 \text{ training sequences}$$
* **Overfitting Hazard:** A standard LSTM network with multiple hidden layers and hundreds of units will rapidly overfit 493 training instances.
* **Architecture Constraints:** An LSTM for this dataset must be **strictly low-capacity**:
  * 1 single LSTM layer with $16$ to $32$ hidden units.
  * Strong Dropout ($0.3\text{--}0.5$) and weight decay ($L_2$ regularization).
  * Early stopping with patience $\le 10$ epochs on the validation set.
* **Baseline Imperative:** Tree-based ensemble regressors (Random Forest, XGBoost) and regularized linear models (Ridge) will serve as formidable baselines and may equal or outperform the LSTM on a dataset of this scale.

---

## 6. Task 5: LSTM Data Representation & Architecture Design

### Sequence Formulation
To formulate this panel dataset for temporal deep learning:
1. **Time-Step Resolution:** Annual sequential time steps ($t \in \{1997, 1998, \dots, 2023\}$) per district $i$.
2. **Lookback Window ($T$):** Set $T = 3$ years (input sequence: $[t-3, t-2, t-1]$) to predict year $t$. A 3-year lookback captures multi-year climate cycles (e.g., ENSO / drought-recovery transitions) while preserving sufficient training sequence samples.
3. **Input Feature Vector ($X_{i,t}$):**
   * **Dynamic Climate Vector (15 features):** Seasonal NASA POWER features for year $t$ (Kharif, Rabi, Zaid for Temp, Rainfall, Humidity, Wind, Soil Moisture).
   * **Autoregressive Lagged Yields (1 feature):** Historical yield of the previous year $Yield_{i, t-1}$ (available at decision time).
   * **Static Soil / District Endowment:** Either pass normalized static features ($Soil\_PH, N, P, K, Fertilizer, Pesticide$) or concatenate a learned **District Embedding vector** ($d \in \mathbb{R}^4$) at the LSTM dense projection layer.
4. **Target ($y_{i,t}$):** Continuous rice yield in year $t$ ($t/ha$).

---

## 7. Task 6: Fair Baseline Experiment Design

To evaluate the true value of an LSTM against standard statistical and machine learning methods, all models must be trained and evaluated on the exact same chronological split with identical feature inputs.

### Models to Benchmark

| Model Class | Algorithm | Configuration & Rationale |
| :--- | :--- | :--- |
| **0. Naive / Persistence** | Historical Lag-1 Baseline | $\hat{Y}_{i,t} = Y_{i,t-1}$ (and 3-year historical district mean). Establishes the floor that any ML model must beat. |
| **1. Linear Baseline** | Ridge Regression ($L_2$) | Regularized linear model to handle multicollinearity among seasonal weather features without overfitting. |
| **2. Tree Ensemble** | Random Forest Regressor | Non-linear ensemble (100–300 trees, max depth 4–6, min samples leaf 5) to capture non-linear agro-climatic thresholds. |
| **3. Gradient Boosting** | XGBoost / LightGBM | Gradient boosted decision trees with shrinkage ($\eta = 0.05$, max depth 3–4). |
| **4. Recurrent Deep Learning** | Low-Capacity LSTM | 1-layer LSTM (32 units, Dropout 0.3) taking 3-year sequential history $[t-2, t-1, t]$ of seasonal climate and lagged yields. |

### Evaluation Protocol & Metrics
* **Chronological Split:** Train (1997–2017), Validation (2018–2020), Test (2021–2023).
* **Metrics:**
  1. **Mean Absolute Error (MAE):** Average magnitude of error in $t/ha$.
  2. **Root Mean Squared Error (RMSE):** Sensitivity to large outliers and extreme harvest failures.
  3. **Coefficient of Determination ($R^2$):** Proportion of variance explained on out-of-sample future years.
  4. **Mean Absolute Percentage Error (MAPE):** Relative error percentage across districts.

---

## 8. Unresolved Questions & Data Quality Items Requiring User Confirmation

1. **Typographical Corruption in Row 622 (`Thiruvarur`, 1998):**
   * `Kharif Humidity` is currently `67087.0`. Will you approve replacing this single value with `67.09` (the apparent correct decimal value) or imputing it via district-year interpolation during data preprocessing?
2. **Chennai District Exclusion:**
   * Given that Chennai is a non-agricultural urban district with 21 missing years out of 27 and negligible rice acreage, should Chennai be permanently filtered out of model training and validation?
3. **Krishnagiri Pre-2004 Imputation:**
   * For the 4 missing years (2001–2004) before Krishnagiri's bifurcation from Dharmapuri, should we impute values using Dharmapuri's parent-district records, or simply allow the model to begin Krishnagiri sequences in 2005?
4. **Zaid Season Temporal Lookahead:**
   * For annual rice yield modeling, do you want to keep the Zaid (summer) features for an *end-of-season hindcast*, or exclude Zaid features to create a *mid-season / pre-harvest forecast* available immediately after the Rabi harvest?
