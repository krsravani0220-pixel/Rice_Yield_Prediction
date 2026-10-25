# Phase 2B: Modeling Strategy and Experiment Design
## Project: Spatio-Temporal Rice Yield Prediction Using Long Short-Term Memory (LSTM)
**Primary Study Region:** Tamil Nadu, India (30 Districts, 1997–2023)  
**Primary Dataset:** `DS_Final_1997_2023(1).xlsx`  
**Date of Strategy Document:** October 13, 2026  
**Document Status:** Methodological Plan & Experimental Specification (Read-Only Audit Phase; No Code Modified, No Models Trained)

---

## 1. Status of Verified Facts, Assumptions, and User-Provided Corrections

To preserve scientific rigor, all components of this modeling strategy are explicitly categorized by their epistemological status:

### A. Verified Facts (Directly inspected from project files)
1. **Workbook Grid:** `DS_Final_1997_2023(1).xlsx` contains exactly 810 rows and 26 columns in sheet `ML_Dataset`, covering 30 districts across 27 years (1997–2023) with zero duplicate district-year combinations.
2. **Missing Target Yield (25 rows):** Chennai is missing yield in 21 of 27 years (and records $0.0\text{ t/ha}$ in 2021). Krishnagiri is missing yield for 4 years (2001–2004) prior to its administrative separation from Dharmapuri district. The remaining 28 districts have 100% complete yield labels across all 27 years.
3. **Verified Physical Drought Disaster:** In district `Ramanathapuram` (Year 2017), the recorded yield is `0.0 t/ha` across an area of `121,849.0 ha`. This is verified against historical meteorological records as a genuine physical crop disaster caused by the catastrophic 2016–2017 Tamil Nadu drought (worst Northeast Monsoon failure in 140 years), not a missing data artifact.
4. **Formula Denominators & Monthly Spans:** Formula cells in Row 2 of `ML_Dataset` prove mathematically that:
   * `Kharif` features are calculated as the arithmetic mean of **4 months** (Denominator = 4: June, July, August, September).
   * `Zaid` features are calculated as the arithmetic mean of **3 months** (Denominator = 3: March, April, May).
   * `Rabi` features contain fractional fifths ($0.002, 0.004, 0.006, 0.008$), proving an arithmetic mean of **5 months** (Denominator = 5: October, November, December, January, February).
   * The sum $4 + 5 + 3 = 12\text{ months}$ accounts for the full agricultural calendar.
5. **Static District Predictors:** Columns `Soil_PH`, `P`, `K`, `Fertilizer`, and `Pesticide` have exactly 1 unique value per district across all 27 years. They represent static district-level lookup constants rather than annually measured dynamic values.
6. **XGBoost Environment Status:** Programmatic inspection confirmed that **XGBoost is NOT installed** in the active Python environment. Scikit-Learn's `GradientBoostingRegressor` and `HistGradientBoostingRegressor` are available natively.

### B. User-Provided Information Requiring External Confirmation
* **Thiruvarur 1998 Kharif Humidity:**
  * **Workbook Cell E624:** Contains the static numerical literal **`67087.0`** (an unpunctuated integer `67087`, not a formula).
  * **User-Provided Value:** The user has indicated that the intended corrected value is **`67.02%`**.
  * **Audit Finding:** The project repository does not contain the raw, unaggregated monthly NASA POWER API query files for 1998. Therefore, **`67.02%` is recorded as a user-provided correction requiring external source confirmation** (e.g., via re-querying the NASA POWER API coordinates for Thiruvarur). Antigravity does not claim to have independently verified `67.02%`.
  * **Integrity Rule:** The original workbook `DS_Final_1997_2023(1).xlsx` remains **completely unchanged**.

### C. Methodological Assumptions Requiring Validation
* **Single Annual Yield Target:** The target variable `Yield` aggregates all rice seasons (Kuruvai, Samba, Navarai) within a district into a single annual metric tonnes per hectare ($t/ha$) figure. Because Samba accounts for $>70\%$ of production, annual yield is heavily dominated by Samba performance, but the exact seasonal weighting is not explicitly recorded in the dataset.

---

## 2. Task 1: Definition of Two Distinct Experiment Tracks

To prevent conflation between retrospective benchmarking and actionable early forecasting, the evaluation must be divided into **two separate, unmerged experimental tracks**:

```
+--------------------------------------------------------------------------------------------------+
|                                    EXPERIMENT TRACK SEPARATION                                   |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|   TRACK A: END-OF-SEASON YIELD ESTIMATION (Retrospective Hindcasting)                            |
|   -------------------------------------------------------------------                            |
|   - Prediction Date: June 1 of year t+1 (After the completion of the full agricultural year).    |
|   - Objective: Benchmark upper-bound predictive capacity of ML/LSTM models against              |
|     official post-harvest crop cutting surveys.                                                  |
|   - Permitted Features: All 15 observed seasonal climate features (Kharif + Rabi + Zaid).        |
|                                                                                                  |
|   TRACK B: PRE-HARVEST YIELD FORECASTING (Actionable In-Season Forecasting)                      |
|   -------------------------------------------------------------------------                      |
|   - Prediction Date: December 31 of year t (Pre-Samba harvest window, prior to Pongal).          |
|   - Objective: Provide actionable yield forecasts for procurement and farmer advisories.         |
|   - Permitted Features: Strictly features available on Dec 31:                                   |
|       * Static district soil properties (pH, N, P, K, Fertilizer, Pesticide).                    |
|       * Kharif climate features (Jun–Sep: fully observed).                                       |
|       * Pre-sowing/Sown Area proxy (if declared pre-harvest).                                    |
|       * Historical lagged yields (Yield_{t-1}, Yield_{t-2}).                                     |
|       * FUTURE CLIMATE (Rabi ripening Jan–Feb, Zaid Mar–May): EXCLUDED from ground truth;       |
|         permitted ONLY if generated by an explicit time-series weather forecaster.               |
|                                                                                                  |
+--------------------------------------------------------------------------------------------------+
```

### Track A: End-of-Season Yield Estimation
* **Operational Nature:** Retrospective spatial estimation / survey verification (hindcast).
* **Execution Date:** June 1 of year $t+1$.
* **Feature Scope:** Full seasonal climate aggregates across all three periods:
  * Kharif (June–September)
  * Rabi (October–February)
  * Zaid (March–May)
  * Static soil attributes and pre-harvest area.
* **Justification:** Establishes the theoretical upper bound of accuracy achievable when complete seasonal weather trajectories are known. This tests whether LSTM captures complex, non-linear weather-yield relationships better than tree-based models when full meteorological data is present.

### Track B: Pre-Harvest Yield Forecasting
* **Operational Nature:** Genuine forward-looking decision-support forecast.
* **Execution Date:** **December 31 of year $t$** (mid-season Samba, 2–4 weeks prior to major harvest).
* **Feature Scope:**
  * Observed Kharif weather (June–September).
  * Observed early Rabi weather (October–December only).
  * Lagged historical yields ($Yield_{t-1}, Yield_{t-2}$).
  * Static soil features.
* **Strict Exclusion:** **Observed weather for January–February (Rabi maturation) and March–May (Zaid) is strictly forbidden.** If full seasonal vectors are required by a model architecture, these future values must be generated via an explicit forecaster (e.g., the `DistrictSeasonalForecaster` Exponential Smoothing / Moving Average model), with forecasting errors propagated naturally into the yield model.

---

## 3. Task 2: Downstream Data Cleaning Strategy

All cleaning procedures must be executed inside a reproducible Python pipeline (`src/preprocessing/pipeline.py`), leaving the raw Excel workbook untouched.

### 1. Thiruvarur 1998 Kharif Humidity Anomaly
* **Policy on Proposed 67.02%:**
  * If the user provides independent verification (e.g., raw NASA POWER query CSV or institutional data log), apply `67.02%` in the downstream cleaned pipeline dataset.
  * If unverified, the **scientifically defensible default** is to treat `67087.0` as an invalid domain violation ($> 100\%$), set it to `np.nan`, and impute it using the training-set median of Thiruvarur's historical Kharif humidity ($64.76\%$) or spatial KNN from adjacent Cauvery delta districts (Thanjavur, Nagapattinam).
  * Both approaches must be clearly documented with their respective rationales.

### 2. Chennai Exclusion
* **Policy:** Exclude Chennai completely from the primary agricultural dataset.
* **Justification:** Chennai is a dense urban district with 21 missing annual yield observations out of 27, negligible agricultural rice cultivation, and an isolated $0.0\text{ t/ha}$ entry in 2021 on 108 ha. Retaining Chennai injects substantial missingness and unrepresentative noise without providing agronomic value.
* **Preservation:** Chennai rows are preserved in the raw file; filtering occurs as Step 0 in the pipeline.

### 3. Krishnagiri Historical Sequence Handling
* **Policy:** Do not fabricate historical values or blindly copy Dharmapuri records into Krishnagiri's 2001–2004 slots.
* **Impact on LSTM Sequences:**
  * Krishnagiri's valid yield records begin in 2005.
  * When constructing sliding window sequences of length $T = 3$, Krishnagiri's first valid training sequence will predict Year 2008 (using inputs from 2005, 2006, and 2007).
  * This prevents artificial imputation from corrupting the spatial-temporal panel while maintaining historical integrity.

### 4. Soil Type Canonicalization
* Standardize `'coastal alluviam'` $\rightarrow$ `'coastal alluvium'` via string replacement in the pipeline to prevent duplicate category encoding.

### 5. Missing Target Handling
* **Strict Rule:** **Never impute missing target `Yield` values** (e.g., via mean or regression) merely to create complete training samples. Imputing targets creates synthetic ground-truth and inflates model evaluation metrics. Any row with missing `Yield` is filtered out of model fitting and evaluation.

### 6. Leakage-Free Preprocessing Architecture
* All scikit-learn transformers (`SimpleImputer`, `StandardScaler`, `OneHotEncoder`) must be **fitted strictly on the Training set (1997–2017)**.
* Validation (2018–2020) and Test (2021–2023) partitions must only be transformed using the parameters (medians, means, standard deviations, categorical vocabularies) learned from the training partition.

---

## 4. Task 3: Seasonal Feature Definitions & Agro-Ecological Alignment

### Verified Mathematical Definitions
* **Kharif (June–September, 4 months):** Arithmetic mean of monthly NASA POWER parameters. Corresponds to the Southwest Monsoon.
* **Rabi (October–February, 5 months):** Arithmetic mean of monthly parameters. Corresponds to the Northeast Monsoon and winter season.
* **Zaid (March–May, 3 months):** Arithmetic mean of monthly parameters. Corresponds to summer pre-monsoon heat.

### Agronomic Reconciliation with Tamil Nadu Rice Calendar
The calendar definitions used in `DS_Final_1997_2023(1).xlsx` reflect a generalized meteorological partition. In Tamil Nadu, rice is cultivated across three distinct seasons:

```
Tamil Nadu Rice Crop Calendar:
1. Kuruvai (Short Duration, 105-120 days):
   - Sown: June – July | Harvested: September – October
   - Matches: Kharif climate features.
2. Samba / Thaladi (Long Duration, 130-160 days) [MAIN CROP: >70% of Production]:
   - Sown: August – October | Harvested: January – February
   - Matches: Rabi climate features (Oct–Feb).
3. Navarai / Kodai (Summer Rice, 100-120 days):
   - Sown: December – February | Harvested: April – May
   - Matches: Late Rabi and Zaid climate features (Mar–May).
```

### Unresolved Agro-Ecological Questions
1. **Annual Yield vs. Seasonal Yield:** The target in `DS_Final_1997_2023(1).xlsx` is total annual rice yield. In districts where farmers double-crop (e.g., Kuruvai followed by Thaladi in Thanjavur), the annual yield is a weighted average of two distinct harvest cycles. The dataset does not provide seasonal yield disaggregation.
2. **Rainfed vs. Irrigated Heterogeneity:** Coastal delta districts (Thanjavur, Thiruvarur) rely heavily on canal irrigation from the Mettur Dam, while southern districts (Ramanathapuram, Sivagangai) are predominantly rainfed tanks. A uniform climate response function across all districts assumes identical vulnerability to rainfall deficit, which must be addressed via district-specific features.

---

## 5. Task 4: Fair Model Comparison & Baseline Architecture

To ensure a scientifically rigorous benchmark, all candidate models will be evaluated across both Track A and Track B under identical chronological splits and standardized feature sets.

### Model Candidates

| # | Model Identifier | Feature Modality | Algorithmic Justification |
| :-: | :--- | :--- | :--- |
| **1** | **Historical-Mean Baseline** | Historical Yield | Predicts district historical mean yield: $\hat{Y}_{i,t} = \frac{1}{t-1}\sum_{k=1}^{t-1} Y_{i,k}$. Establishes absolute performance floor. |
| **2** | **Persistence Baseline** | Historical Yield | Predicts previous year's yield: $\hat{Y}_{i,t} = Y_{i,t-1}$. Tests whether yield exhibits simple random walk behavior. |
| **3** | **Ridge Regression ($L_2$)** | Climate + Soil + Area | Regularized linear model. Prevents collinearity among 15 seasonal weather features; baseline for linear trends. |
| **4** | **Random Forest Regressor** | Climate + Soil + Area | Non-linear ensemble (150 trees, max depth 6, min samples leaf 4). Robust against feature scaling, captures non-linear thresholds. |
| **5** | **Gradient Boosting Regressor** | Climate + Soil + Area | Scikit-Learn `HistGradientBoostingRegressor` / `GradientBoostingRegressor` (learning rate 0.03, max depth 3). Strong gradient-boosted tabular baseline. *(XGBoost noted as uninstalled).* |
| **6** | **Low-Capacity LSTM** | Sequence of [Climate + Lagged Yield] | Recurrent neural network modeling a 3-year sliding sequence of seasonal climate features and historical yield. |

### Feature Allocation Matrix

| Model | Historical Yield ($Y_{t-1}$) | Dynamic Climate Features | Static District Features | Cultivated Area ($ha$) |
| :--- | :---: | :---: | :---: | :---: |
| Historical-Mean | Yes (Historical pool) | No | No | No |
| Persistence | Yes ($Y_{t-1}$) | No | No | No |
| Ridge Regression | Optional (Lag-1) | Yes (Track A: 15 / Track B: Pre-harvest) | Yes (One-hot / Scaled) | Yes |
| Random Forest | Optional (Lag-1) | Yes (Track A: 15 / Track B: Pre-harvest) | Yes (Categorical / Scaled) | Yes |
| Gradient Boosting | Optional (Lag-1) | Yes (Track A: 15 / Track B: Pre-harvest) | Yes (Categorical / Scaled) | Yes |
| Low-Capacity LSTM | Yes (Embedded in sequence) | Yes (Sequential time steps) | Yes (Concatenated at Dense layer) | Yes |

*Rule:* No model may access the contemporaneous yield $Y_{i,t}$ or any future yields $Y_{i,t+k}$.

---

## 6. Task 5: Temporal Validation & Sequence Construction Protocol

### Chronological Split Specifications
To reflect real-world forecasting where future data is completely unobserved, the dataset will be partitioned strictly across calendar years:

* **Training Set:** **1997 – 2017** (21 years, $\sim 77.8\%$ of data)
  * Total potential records (excluding Chennai): $29 \text{ districts} \times 21 \text{ years} = 609 \text{ records}$.
  * Valid records: 605 (accounting for Krishnagiri 2001–2004).
* **Validation Set:** **2018 – 2020** (3 years, $\sim 11.1\%$ of data)
  * Total records: $29 \times 3 = 87 \text{ records}$ (100% valid).
  * Used for: Early stopping of LSTM, hyperparameter tuning of tree models.
* **Test Set (Held-Out):** **2021 – 2023** (3 years, $\sim 11.1\%$ of data)
  * Total records: $29 \times 3 = 87 \text{ records}$ (100% valid).
  * Used for: Final out-of-sample evaluation.

### Sequence Construction Rules for LSTM
For each district $i$, temporal sequences are constructed independently to prevent cross-district contamination:

```
District i Sequence Structure (Lookback T = 3 years):
Input Sequence:   X_seq = [ (Climate_{i, t-3}, Yield_{i, t-3}), 
                            (Climate_{i, t-2}, Yield_{i, t-2}), 
                            (Climate_{i, t-1}, Yield_{i, t-1}) ]
Prediction Target: y_target = Yield_{i, t}
```

1. **Strict Temporal Ordering:** Every input observation in $X_{\text{seq}}$ occurs at time steps strictly prior to the target year $t$.
2. **Partition Boundaries:**
   * Sequences predicting target years $t \in [1997+T, 2017]$ belong to the **Training set**.
   * Sequences predicting target years $t \in [2018, 2020]$ belong to the **Validation set**.
   * Sequences predicting target years $t \in [2021, 2023]$ belong to the **Test set**.
3. **Handling Overlapping Windows:** While sliding windows share historical observations across consecutive years within a district, **they must never cross partition boundaries**. Test sequences may look back into validation years (e.g., predicting 2021 using 2018, 2019, 2020), but training loss and gradient backpropagation are strictly confined to the training set.
4. **Additional Robustness Check (Rolling-Origin Evaluation):**
   * Perform forward-chaining cross-validation across the final 5 years:
     * Fold 1: Train 1997–2018 $\rightarrow$ Test 2019
     * Fold 2: Train 1997–2019 $\rightarrow$ Test 2020
     * Fold 3: Train 1997–2020 $\rightarrow$ Test 2021
     * Fold 4: Train 1997–2021 $\rightarrow$ Test 2022
     * Fold 5: Train 1997–2022 $\rightarrow$ Test 2023

---

## 7. Task 6: LSTM Architecture Design & Small-Sample Regularization

### Statistical Constraints of the Dataset
* Number of agricultural districts: $D = 29$.
* Training years: $Y_{\text{train}} = 21$ (1997–2017).
* With lookback $T = 3$, the effective number of training sequences per district is $21 - 3 = 18$.
* Total training sequences across all districts:
  $$N_{\text{train\_seq}} \approx 28 \times 18 + 1 \times 10 \approx 514 \text{ samples}$$
* **Critical Modeling Reality:** 514 samples is a very small dataset for deep learning. An unconstrained LSTM will overfit within a few epochs. Therefore, the LSTM must be **strictly low-capacity and heavily regularized**.

### Recommended Low-Capacity Architecture

```
Layer (Type)                 Output Shape              Parameters / Notes
===================================================================================
Input Sequence               (Batch, 3, F_dynamic)     Lookback = 3 years
LSTM Layer                   (Batch, 24)               16 to 32 units (tanh/sigmoid)
Dropout Layer                (Batch, 24)               Dropout Rate = 0.4
-----------------------------------------------------------------------------------
Static District Input        (Batch, F_static)         Soil properties + District Embedding
Dense Projection (Static)    (Batch, 8)                Embedding / linear reduction
-----------------------------------------------------------------------------------
Concatenate Layer            (Batch, 32)               Merges LSTM output + Static features
Dense Hidden Layer           (Batch, 16)               ReLU activation
Dropout Layer                (Batch, 16)               Dropout Rate = 0.2
Dense Output Layer           (Batch, 1)                Linear activation (Yield in t/ha)
===================================================================================
```

### Hyperparameters and Regularization Protocol
* **Hidden Units:** 24 units (middle of the recommended 16–32 range).
* **Optimizer:** Adam with learning rate $\eta = 0.001$, gradient clipping (`clipnorm=1.0`).
* **Loss Function:** Huber Loss or Mean Squared Error (MSE). Huber loss is recommended to prevent extreme penalty on drought anomalies like Ramanathapuram 2017.
* **Early Stopping:** Monitor validation loss with `patience = 10` epochs, restoring the best model weights.
* **Reproducibility:** Fix global seeds across Python, NumPy, and PyTorch/TensorFlow (`seed = 42`).
* **Why Simpler Models May Outperform LSTM:** Tree ensembles (Random Forest, Gradient Boosting) do not require recurrent state estimation and can effectively partition tabular feature spaces with small sample sizes without vanishing or exploding gradients.

---

## 8. Task 7: Research Validity, Limitations, and Known Risks

### 1. Target Leakage Risks
* **Production Absence:** Confirmed absent in the raw file.
* **Area as a Predictor:** If total harvested area is finalized post-harvest, including final area in pre-harvest models could introduce minor leakage. Recommendation: evaluate models with and without `Area`.

### 2. Temporal Lookahead
* In Track A, using Zaid features (March–May) to estimate annual yield is valid only for retrospective survey benchmarking.
* In Track B, all post-December features must be strictly omitted.

### 3. Spatial Generalization Limits
* Models trained on pooled district data learn global relationships across Tamil Nadu. However, irrigation infrastructure varies dramatically between the canal-irrigated Cauvery Delta (Thanjavur) and rainfed southern districts (Ramanathapuram). A single global model without district-level embeddings will struggle to generalize across diverse agro-climatic zones.

### 4. Small-Sample Limitations
* 27 years of annual data provides only 27 temporal observations per district. Multi-decadal climate cycles (e.g., decadal drought cycles) cannot be reliably learned by deep sequence models from such a short historical baseline.

### 5. Additional Data Required for Stronger Validation
* **High-Resolution Satellite Remote Sensing:** Integrating multi-temporal Sentinel-2 / Landsat NDVI, EVI, and NDWI indices at the peak vegetative stage (November–December for Samba) would provide real-time, field-scale biophysical signals independent of macro-climate reanalysis.
* **Ground-Truth Field Plot Data:** District-level aggregates mask substantial intra-district yield variance. Plot-level ground truth (as explored in SICKLE) is required to validate precision agricultural decision support.

---

## 9. Evaluation Metrics & Reporting Standards

All models across both Track A and Track B will be evaluated using standard regression metrics expressed in physical agronomic units:

1. **Mean Absolute Error (MAE):**
   $$\text{MAE} = \frac{1}{n} \sum_{i=1}^n |y_i - \hat{y}_i| \quad (\text{expressed in tonnes per hectare, } t/ha)$$
2. **Root Mean Squared Error (RMSE):**
   $$\text{RMSE} = \sqrt{\frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2} \quad (\text{penalizes large harvest failures, } t/ha)$$
3. **Coefficient of Determination ($R^2$):**
   $$R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2} \quad (\text{measured strictly out-of-sample on held-out years})$$
4. **Mean Absolute Percentage Error (MAPE):**
   $$\text{MAPE} = \frac{100\%}{n} \sum_{i=1}^n \left| \frac{y_i - \hat{y}_i}{y_i} \right| \quad (\text{calculated for non-zero yields})$$

---

## 10. Summary of Key Decisions Requiring Confirmation

Before proceeding with future experimental code execution:
1. **User Approval for Downstream Humidity Correction:** Confirm whether the user formally approves applying `67.02%` in downstream pipeline data with the documentation that it is a user-provided correction requiring external source validation.
2. **Inclusion of Area in Pre-Harvest Track B:** Confirm whether cultivated `Area` should be retained as an input feature in Track B under the assumption of pre-sowing acreage, or omitted entirely to test a pure climate-driven model.
3. **Execution of Baseline Suite:** Confirm approval to benchmark the five candidate models (Historical Mean, Persistence, Ridge, Random Forest, Gradient Boosting) alongside the low-capacity LSTM under the chronological split (Train: 1997–2017, Val: 2018–2020, Test: 2021–2023).
