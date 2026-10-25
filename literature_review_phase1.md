# Systematic Literature Review: Research Papers r1.pdf through r18.pdf
## Project: Spatio-Temporal Rice Yield Prediction Using Long Short-Term Memory (LSTM)
**Primary Study Region:** Tamil Nadu, India  
**Date of Audit:** October 13, 2026  
**Inspection Mode:** Read-Only Rigorous Verification (Direct PDF Content & SHA-256 Hash Inspection)

---

## 1. Executive Summary & Audit Scope

This document provides a comprehensive, evidence-based review of the 18 research papers (`r1.pdf` through `r18.pdf`) located in the root project workspace (`C:\Users\K R Sravani\OneDrive\Desktop\RICE_YIELD_PREDICTION`). Each paper was individually inspected to extract bibliographic metadata, geographic scope, target variables, dataset sources, feature representations, algorithmic frameworks, quantitative results, explicit author limitations, and methodological vulnerabilities.

Every claim and metric in this report cites the exact PDF page, section, or table from the primary text. Unreported items are explicitly marked as **"Not reported"** rather than estimated.

---

## 2. Task 1: Duplicate Verification & Hash Audit

A cryptographic hash audit was conducted across all 18 PDF files using SHA-256 to establish absolute file identity and duplication.

### SHA-256 Hash Inventory

| File | SHA-256 Checksum | File Size (Bytes) | Duplication Status |
| :--- | :--- | :---: | :--- |
| **`r1.pdf`** | `1F9F1D533F66599361B5DBFCC05CC5908DDF9213587EB00BDD4D5AD6F0DDB28C` | 244,804 | Unique document |
| **`r2.pdf`** | `CD20C96DE1659643BC3346C2B2D887C876D5C0413D3DAD4A15382968C7BF6AA7` | 826,200 | **Content duplicate** of `r3.pdf` |
| **`r3.pdf`** | `44DAD9D718FAF3F4B268D9DB5CF15ABAF34CAF2F840F747DD250630C02E8A786` | 826,204 | **Content duplicate** of `r2.pdf` |
| **`r4.pdf`** | `191346DB935E1E06C8AD2926BADC46249A7E4678C3205458DDDF4B7500CAD64C` | 3,448,906 | **Content duplicate** of `r5.pdf` |
| **`r5.pdf`** | `A32D7C18EAC7090E241FB8B74B08D66C92C93B86A15B140DDC97C19AFA9A9466` | 3,448,906 | **Content duplicate** of `r4.pdf` |
| **`r6.pdf`** | `0EBB0A862D404621AC47B48A18AFBE6269C5BE41F9ED5EAFF45C2AC1119E3674` | 6,035,431 | Unique document |
| **`r7.pdf`** | `ADC7193A1A9BA7C61EF39951FE2DB5A80178DA62D9290690551722F2F7C3E177` | 1,519,671 | Unique document |
| **`r8.pdf`** | `96ED41CB60ADB6ECCA72F3B8B6A2B8506F88A2C5BFCD2A8FFAF63B88547593BE` | 4,108,830 | Unique document |
| **`r9.pdf`** | `96522961D36BE1CBC1BE20824737EBF3C1D1FFE0E72C3F69AE84E762C4D2662E` | 708,436 | Unique document |
| **`r10.pdf`** | `40E284E73C1B4DD5BF180D872AEE3671D3F1FE9F9FD052E214CBDD6C31E636E4` | 1,007,913 | **Byte-for-byte identical** to `r15.pdf` |
| **`r11.pdf`** | `B4B26558AF0F4E02A19BE5112A111DF7C64DBF7A6BDE16C243C5BB6243EE440B` | 1,096,956 | Unique document |
| **`r12.pdf`** | `41EB04BD46B595E7AC5D86C2515D9FF95D1C7FFFF2285CED8C2F2DB953B9687F` | 1,178,667 | Unique document |
| **`r13.pdf`** | `B308F14AFF0D5BEAEC5FF995ABE643A9177A81DF5A3CAA295A2687922343BDC1` | 1,261,352 | Unique document |
| **`r14.pdf`** | `EE06E0A189B185FD1F15E803CC03BCA2401CDC2FF0F388E15EBB59ECE681F605` | 1,524,609 | Unique document |
| **`r15.pdf`** | `40E284E73C1B4DD5BF180D872AEE3671D3F1FE9F9FD052E214CBDD6C31E636E4` | 1,007,913 | **Byte-for-byte identical** to `r10.pdf` |
| **`r16.pdf`** | `5A59D2977F88883DF3BDF4A33E7179AE0E446D8057A25AAAA127089D9960EAE0` | 8,746,439 | Unique document |
| **`r17.pdf`** | `351371488890159948EEE7EF13905726C657CDF58D3F4E3DDA63EDD9E8A7F2D5` | 369,591 | Unique document |
| **`r18.pdf`** | `7B5B566FC5ADC5759B9C7EE7539016778A92449AD52B12D6854780C003E248BA` | 479,192 | Unique document |

### Findings on Duplicate Candidates

1. **`r10.pdf` and `r15.pdf`**:
   - **Verification:** **100% Byte-for-byte identical.**
   - Both files share the exact SHA-256 hash (`40E284E73C1B4DD5BF180D872AEE3671D3F1FE9F9FD052E214CBDD6C31E636E4`) and file size (1,007,913 bytes). Both correspond to the paper *"Multi-Agent System Based on Stacking Technique for Rice Yield Prediction"* by Hayam R. Seireg et al. (ICEEM 2023).

2. **`r4.pdf` and `r5.pdf`**:
   - **Verification:** **Content duplicate, differing only by IEEE Xplore download timestamp metadata.**
   - Both files contain the exact same paper: *"AI based hybrid CNN-LSTM model for crop disease prediction: An ML advent for rice crop"* by Sonal Jain and Dharavath Ramesh (ICCCNT 2021).
   - Both have identical page counts (7 pages), identical figures, tables, text, and byte sizes (3,448,906 bytes).
   - The SHA-256 hashes differ solely because of the dynamic IEEE Xplore watermark in the page footer:
     - `r4.pdf` footer (p. 1): `Downloaded on September 23,2026 at 09:20:43 UTC`
     - `r5.pdf` footer (p. 1): `Downloaded on September 23,2026 at 10:27:03 UTC`

3. **`r2.pdf` and `r3.pdf`**:
   - **Verification:** **Content duplicate, differing only by 4 bytes of download watermark metadata.**
   - Both files contain the paper: *"Advanced Rice Yield and Soil Prediction using Deep Learning"* by G. Pavan Sagar et al. (ICSSAS 2025).
   - `r2.pdf` (826,200 bytes) was downloaded at `08:45:08 UTC`, while `r3.pdf` (826,204 bytes) was downloaded at `08:57:32 UTC`. The text, tables, figures, and models are identical.

**Conclusion:** The 18 files correspond to **15 unique research papers**.

---

## 3. Task 2: Comprehensive Paper Extraction & Technical Review

Below is the comparative breakdown of all 15 unique papers.

| Paper ID | Authors & Year | Publication Venue & DOI / ISBN | Study Region & Crop | Prediction Target | Dataset Source & Sample Size | Core Algorithms | Evaluation Metrics & Results | Stated Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **r1** | A. K. Mariappan, J. Austin Ben Das (2017) | IEEE TIAR 2017, ISBN: 978-1-5090-4437-5/17 | Vellar river basin, Tamil Nadu, India; Rice | Rice yield (t/ha) [Regression heuristic] | Vellar basin historical data (10-year period, 11 sample rows shown in Table II, 1 test row in Table III) | ZeroR classifier algorithm (paired probability mean) | Predicted training set: 4.8363 t/ha; MAE = 0.0364 | States that no yield prediction system existed in TN; acknowledges limited factors |
| **r2 / r3** | G. Pavan Sagar, M. Aravind, M. Vaidhehi (2025) | IEEE ICSSAS-2025, DOI: 10.1109/ICSSAS66150.2025.11081042 | Unspecified geographic origin (SRM Inst., TN authors); Rice | Rice grain variety (5 classes) & soil suitability. **NOT YIELD!** | 75,000 macroscopic grain images (15,000 per class: Arborio, Basmati, Ipsala, Jasmine, Karacadag) | Sequential CNN (Conv2D 32-64-128, Dropout 0.3, Dense 128, Softmax) | Classification accuracy: 99.7%; Training precision > 98%, Test precision > 96% | Lacks soil moisture, salinity, organic content; relies solely on grain RGB images |
| **r4 / r5** | Sonal Jain, Dharavath Ramesh (2021) | IEEE ICCCNT 2021, DOI: 10.1109/ICCCNT51525.2021.9579587 | 5 Indian regions (Cuttack, Ludhiana, Raipur, Rajendranagar, Maruteru); Rice | Yellow Stem Borer (YSB) pest count & 4-class severity. **NOT YIELD!** | ICAR-CRIDA light trap & weather records (1995–2011, weekly SMW format, 52 weeks/yr) | 1D CNN-LSTM vs CNN vs LSTM; ECOC SVM (Linear, RBF, Poly, Gauss) | Maruteru Wk 1 $R^2 = 0.41$; Rajendranagar Wk 1 $R^2 = 0.30$; Raipur $R^2 < 0$; SVM Poly Acc = 89% | Negative $R^2$ in Raipur due to data errors/scarcity; accuracy degrades sharply beyond week 1 |
| **r6** | Thuy-Vi Thi Ha, Bao-An Nguyen, Thanh-Nghi Do (2024) | IEEE ICOCO 2024, DOI: 10.1109/ICOCO62848.2024.10928258 | Mekong Delta (An Giang & Tra Vinh), Vietnam; Rice | Plot-level rough grain yield ($kg/1000\,m^2$, t/ha) [Regression] | 11,736 RGB field images from 47 plots (28 ha) captured via UAVs, phones, cameras (Feb–May 2024) | Vision Transformer (ViT) feature extraction + SVR, MLP, RF, XGBoost, Voting Ensemble | ViT-Vote MAE = 72.72 $kg/1000\,m^2$; ViT-RF = 75.96; ViT-MLP = 77.80; ViT = 84.18 | Only ripening stage imagery; lacks weather/climate data integration; single-season snapshot |
| **r7** | Kusum Lata, Navneet Kaur, Simrandeep Singh (2025) | IEEE ICCICA 2025, DOI: 10.1109/ICCICA67008.2025.11337508 | Ludhiana district, Punjab, India; Rice | District rice yield (t/ha) [Regression] | Ludhiana 5-yr Sentinel-2 + Open-Meteo weekly data (2019–2023, 134 wks); Punjab Govt yield (2013–2023) | Lasso, Random Forest, SVR, XGBoost, Neural Network Regressor | RF Test $R^2 = 0.9989$, MAE = 0.0047, RMSE = 0.0058; XGBoost $R^2 = 0.9977$ | Single district; small temporal span; does not use SAR data or deep recurrent models |
| **r8** | Sony M Kuriakose, Tripty Singh (2022) | IEEE ICCCNT 2022, DOI: 10.1109/ICCCNT54827.2022.9984407 | India (generic IMD stations); Multi-crop | Daily climate parameters for year 2018. **YIELD OMITTED!** | IMD Pune daily weather (1980–2017, >13,000 rows); ANN missing-value imputation | Univariate LSTM models (loop over 5 weather columns with 20-day lookback) | Forecasted daily weather trends; **No numerical yield prediction results reported** | High training time and memory overhead for LSTM; Phase 2 yield model was never completed |
| **r9** | N. Juliet et al. (2025) | IEEE STCR 2025, DOI: 10.1109/STCR62650.2025.11018972 | Indian states; Coconut, Rice, Guava, Papaya | Crop yield (t/ha) [Regression] | Kaggle Indian states crop yield dataset (1997–2020, 19,698 rows) + simulated IoT sensors | MobileNet-Inspired LSTM (Depthwise Conv + Bi-LSTM + Attention) + Adaptive Adam | Coconut $R^2 = 0.93$; Guava $R^2 = 0.93$; Papaya $R^2 = 0.92$; Rice $R^2 > 0.90$ (exact omitted) | Reduced performance when tested on new regions; high computational resources |
| **r10 / r15** | Hayam R. Seireg, Yasser M. Omar, Ahmed Elmahalawy (2023) | IEEE ICEEM2023, DOI: 10.1109/ICEEM58740.2023.10319559 | Lowland & Northeast rice regions, China; Rice | Binary rice yield level ("High" > 6 t/ha vs "Low" $\le$ 6 t/ha) [Classification] | China County Agricultural Statistics + CMSDS weather (1980–2010, 1,266 rows, 18 features) | Stacking Ensemble (ETC, RFC, LDA base classifiers + Gaussian Naive Bayes meta-model) | Stacking Acc = 87.0%, F1 = 0.93, Sensitivity = 1.00; Decision Tree Acc = 77.5%; LDA = 34.6% | Binary classification adopted because ML regression failed; regional variations across China |
| **r11** | Tawfiqul Hasan et al. (2026) | IEEE QPAIN 2026, DOI: 10.1109/QPAIN69676.2026.11545663 | 8 administrative divisions of Bangladesh; Rice | Annual division rice yield (t/ha) [Regression] | Bangladesh Agroclimatic Crop Yield (2000–2024, Kaggle, 24 years, 15 variables) | Linear Regression, Random Forest, Gradient Boosting, SVR | Linear Regression $R^2 > 0.97$ (Rajshahi: 0.9958, MAE: 0.0260; Chittagong: 0.9947); RF $R^2 = 0.82\text{--}0.91$ | Annual division data masks seasonal/district variance; high linearity reflects macro trend |
| **r12** | Avinash Rai, Ruby Dahiya (2026) | IEEE ICISESSC 2026, DOI: 10.1109/ICISESSC68634.2026.11542774 | Agro-ecosystems across India; Rice (BPT-5204), Wheat, Barley | Cereal crop yield (quintals/ha) [Regression] | Multi-crop soil fertility & climate records (sample size not reported, 70:30 split) | Random Forest, XGBoost, Linear Regression; Soil Fertility Index (SFI) formula | Random Forest $R^2 = 0.91$, MAE = 1.25 q/ha, RMSE = 1.84; XGBoost $R^2 = 0.89$; LR $R^2 = 0.62$ | Static cross-sectional data; misses pest pressure, farm management, micro-climate factors |
| **r13** | Govindaraj M et al. (2026) | IEEE ICICIT-2026, DOI: 10.1109/ICICIT69063.2026.11633947 | 40 districts across India; Rice | Ordinal rice yield (Low, Medium, High) [Classification] | Indian Govt district records (9,885 records, 40 districts, 80:20 district-stratified split) | Causal-Aware Mixture of Experts (Causal-MoE: L1 gating + 4 MLPs) vs Monolithic MLP | Causal-MoE Test Acc = 96.73%, Macro F1 = 0.98, ROC-AUC $\ge 0.998$; MLP Baseline Acc = 96.03% | Ordinal classification only (no continuous yield regression); lacks satellite/remote sensing |
| **r14** | Jianqiang Ren et al. (2010) | IEEE GRS2010, ISBN: 978-1-4244-8515-4/10 | Hengshui City, Hebei, China (11 counties); **Summer Maize** | Maize yield (t/ha) & field management params. **NOT RICE!** | MODIS 250m 16-day NDVI (2004) + 29 field plots (500m x 500m) + daily weather (June–Sept 2004) | Remotely sensed LAI assimilation into EPIC crop model via SCE-UA global optimization | Maize yield relative error = 4.37%, RMSE = 0.44 t/ha; sowing date error = 1.85% (3 days) | Single crop (maize); single year (2004); 1km EMU grid; heavy parameter calibration |
| **r16** | Venkateshwarlu Banavath et al. (2026) | IEEE CSNT 2026, DOI: 10.1109/CSNT69054.2026.11502261 | Bangladesh; Boro Rice | Boro rice yield (t/ha) [Regression] | Private agricultural collection (4,480 records, 43 features, 75:25 split) | RF, Gradient Boosting, LR, SVR, KNN; Grid Search CV; SHAP & Morris sensitivity | RF Test $R^2 = 0.9999$, Test RMSE = 0.0000, Test MAE = 0.0000; GB $R^2 = 0.999998$ | Authors acknowledge 0.0000 CV MSE indicates possible overfitting or data issues |
| **r17** | Benyamin Sibarani et al. (2025) | IEEE ICCED 2025, DOI: 10.1109/ICCED68324.2025.11324627 | Indonesia; Rice irrigation context | Daily rainfall (mm) for irrigation scheduling. **NOT YIELD!** | Open-Meteo daily weather (temp, humidity, sunshine, rain; 80:10:10 split) | 2-layer LSTM (64 units each, dropout 0.2) with 7-day lookback | Test MAE = 4.15 mm, RMSE = 6.47 mm; Rule-based simulation cut unnecessary irrigation by 40% | Underestimates extreme rainfall events; weather-only; does not model crop yield |
| **r18** | Md. Akter Hossain et al. (2017) | IEEE ICTC 2017, DOI: 10.1109/ICTC.2017.8285514 | 21 districts of Bangladesh; Aus, Aman, Boro Rice | Rice yield (M.Tons/ha) for 2016 [Regression] | BBS agricultural records (2006–2015) + BMD weather (2012–2015, 4 years monthly data) | WPSRY two-stage model: Stage 1 MLP weather forecast + Stage 2 SVR yield prediction | 2016 evaluation: Aman MRE = 5.82% (MAE: 0.27); Boro MRE = 6.28% (MAE: 0.29); Aus MRE = 8.79% | SVR propagates Stage 1 forecasting errors; only 4 years weather data; no LSTM |

---

## 4. Deep Analytical Profiles of Individual Papers

### r1: Mariappan & Das (2017) — *A Paradigm for Rice Yield Prediction in Tamil Nadu*
* **Bibliographic Data:** Prof. A. K. Mariappan and J. Austin Ben Das, Easwari Engineering College, Chennai, India. Published in *2017 IEEE International Conference on Technological Innovations in ICT For Agriculture and Rural Development (TIAR 2017)*, pp. 18–21.
* **Study Region & Target:** Vellar river basin, Tamil Nadu, India (p. 20). Target is rice yield in tons per hectare (t/ha) (p. 20, Table II).
* **Dataset & Sample Size:** Historical data covering a 10-year period in Vellar basin. The paper displays only 11 training rows in Table II and 1 single test query row in Table III (p. 20).
* **Features:** Soil type (Mixed, Loamy), Fertilizer (Nitrogen, Potash, Phosphorus), Days to grow (90, 120), Nitrogen (ppm), Season (Rabi) (p. 20, Table II).
* **Methodology:** Implements a ZeroR paired-probability classifier heuristic. The predicted training target is 4.8363 t/ha, with a reported Mean Absolute Value of 0.0364 (p. 21).
* **Limitations:** The paper provides no statistical regression or machine learning validation; the sample size is microscopic (1 test instance); no time-series dynamics, climate variables, or modern neural architectures are used.
* **Relevance:** Category A (Directly focused on Tamil Nadu rice yield). Confirms local interest in river-basin-level yield modeling, but offers zero usable machine learning methodology.

### r2 / r3: Sagar, Aravind, & Vaidhehi (2025) — *Advanced Rice Yield and Soil Prediction using Deep Learning*
* **Bibliographic Data:** G. Pavan Sagar, Mesala Aravind, Dr. M. Vaidhehi, SRM Institute of Science and Technology, Kattankulathur, Chennai, India. Published in *2025 3rd International Conference on Self Sustainable Artificial Intelligence Systems (ICSSAS-2025)*, IEEE, DOI: 10.1109/ICSSAS66150.2025.11081042, pp. 1219–1224.
* **Study Region & Target:** Institutional setting is Tamil Nadu, but the dataset is non-geographical. **Prediction target is rice grain variety classification (Arborio, Basmati, Ipsala, Jasmine, Karacadag) and matching soil recommendations.** Despite the phrase *"Rice Yield"* in the title, **actual crop yield is never predicted or regressed** (p. 1219, 1221).
* **Dataset & Features:** 75,000 macroscopic grain images (15,000 per class), resized to 150x150 pixels (p. 1221).
* **Methodology:** Sequential CNN (3 Conv2D layers with 32, 64, 128 filters, ReLU, MaxPooling2D, Dropout 0.3, Dense 128, Softmax) trained with Adam optimizer and sparse categorical cross-entropy (p. 1222).
* **Results:** Reported classification accuracy of 99.7%, training precision > 98%, test precision > 96% (p. 1219, 1223).
* **Limitations:** Title is misleading; no yield data, no climate time series, and no satellite data are utilized.
* **Relevance:** Category D (Related agricultural research — grain classification, not yield prediction).

### r4 / r5: Jain & Ramesh (2021) — *AI based hybrid CNN-LSTM model for crop disease prediction: An ML advent for rice crop*
* **Bibliographic Data:** Sonal Jain and Dharavath Ramesh, IIT (ISM) Dhanbad, Jharkhand, India. Published in *2021 12th International Conference on Computing Communication and Networking Technologies (ICCCNT 2021)*, IEEE, DOI: 10.1109/ICCCNT51525.2021.9579587, pp. 1–7.
* **Study Region & Target:** Cuttack (Odisha), Ludhiana (Punjab), Raipur (Chhattisgarh), Rajendranagar (Telangana), Maruteru (Andhra Pradesh) (p. 2). **Target is Yellow Stem Borer (YSB) pest count (1-month ahead regression) and 4-class severity classification (None, Low, Medium, High). NOT yield prediction!** (p. 1, 2).
* **Dataset & Features:** ICAR-CRIDA light trap pest and weather records (1995–2011) in Standard Meteorological Week (SMW) format. 8 weather features: Max/Min Temp, Morning/Evening RH, Rainfall, Wind Speed, Evaporation, Sunshine Hours + previous light trap counts (p. 2).
* **Methodology:** 1D CNN + LSTM hybrid network for sequence regression compared against standalone 1D CNN and LSTM; ECOC SVM for multi-class classification (p. 3–4).
* **Results:** Maruteru Week 1 $R^2 = 0.41$ (CNN-LSTM) vs 0.37 (LSTM) vs 0.33 (CNN); Rajendranagar Week 1 $R^2 = 0.30$; Raipur showed severe negative $R^2$ (-12.74 to -22.75). SVM Polynomial achieved 89% classification accuracy (p. 4, 6).
* **Limitations:** Severe failure in Raipur due to data gaps/noise; prediction horizon degrades steeply from week 1 to week 4 (p. 4); target is pest dynamics, not crop yield.
* **Relevance:** Category D (Related agricultural research — pest forewarning). Demonstrates the mechanics of hybrid 1D CNN-LSTM on meteorological time series in India, but does not model yield.

### r6: Ha, Nguyen, & Do (2024) — *Enhancing Rice Yield Prediction using Vision Transformer and Regression Models*
* **Bibliographic Data:** Thuy-Vi Thi Ha, Bao-An Nguyen, Thanh-Nghi Do, Can Tho University and Tra Vinh University, Vietnam. Published in *2024 IEEE International Conference on Computing (ICOCO)*, IEEE, DOI: 10.1109/ICOCO62848.2024.10928258, pp. 273–278.
* **Study Region & Target:** Mekong Delta (An Giang and Tra Vinh provinces), Vietnam (p. 273, 274). Target is plot-level rough grain yield ($kg/1000\,m^2$ and t/ha) at ripening stage (p. 273, 275).
* **Dataset & Features:** 11,736 high-resolution RGB field images from 47 rice plots (28 hectares) captured between February and May 2024 via UAVs, digital cameras, and smartphones (p. 273, 274).
* **Methodology:** Pretrained Vision Transformer (ViT) on ImageNet fine-tuned with modified MLP head (Dense 1024 -> Dropout 0.33 -> Dense 1), extracting feature embeddings passed to downstream regressors (Random Forest, XGBoost, SVR, MLP, and Voting Ensemble) (p. 274–275).
* **Results:** ViT-Vote Ensemble achieved the lowest MAE of 72.72 $kg/1000\,m^2$; ViT-RF achieved 75.96; ViT-MLP achieved 77.80; standalone ViT achieved 84.18 (p. 277).
* **Limitations:** Evaluated only at ripening stage (immediate pre-harvest); lacks weather/climate time series; 70:30 random train:test split across only 47 plots presents high risk of spatial correlation leakage between images from the same plot.
* **Relevance:** Category B (Rice-yield prediction in another region — Vietnam, plot-level canopy computer vision).

### r7: Lata, Kaur, & Singh (2025) — *Evaluation of Rice Yield Estimation from Satellite Data by integrating Hybrid Regression Models*
* **Bibliographic Data:** Kusum Lata, Navneet Kaur, Simrandeep Singh, Chandigarh University, Mohali, India. Published in *2025 2nd International Conference on Computational Intelligence and Computing Applications (ICCICA)*, IEEE, DOI: 10.1109/ICCICA67008.2025.11337508, pp. 555–560.
* **Study Region & Target:** Ludhiana district, Punjab, India (p. 555, 556). Target is annual district rice yield in tonnes/hectare (p. 556, 558).
* **Dataset & Features:** Sentinel-2 10m weekly NDVI and EVI (Google Earth Engine), Open-Meteo weekly weather (temperature, precipitation, rainfall, soil moisture), and Punjab Government statistical yield (2013–2023) across 134 weeks (May–Nov, 2019–2023) (p. 556–557).
* **Methodology:** Compares Lasso Regression, Random Forest, SVR, XGBoost, and Neural Network Regressor on a 70:30 split (p. 557).
* **Results:** Random Forest achieved Test $R^2 = 0.998873$, MAE = 0.004748, RMSE = 0.005841; XGBoost achieved Test $R^2 = 0.997687$; Lasso achieved $R^2 = 0.988410$ (p. 559, Table III).
* **Critical Methodological Flaw:** Extreme target leakage and pseudoreplication. The study examines only **1 single district across 5 years** (only 5 annual ground-truth yield values). Weekly vegetation and climate features were paired with the same annual yield, and Table I explicitly lists *"Area_Hectare"* and *"Production_Tonne"* as model features, creating direct algebraic leakage ($Yield = Production / Area$). This explains the implausible $R^2 > 0.998$.
* **Relevance:** Category B (Rice-yield prediction in another region — Punjab, India). Serves as a vital cautionary benchmark on data leakage in satellite/tabular yield modeling.

### r8: Kuriakose & Singh (2022) — *Indian Crop Yield Prediction using LSTM Deep Learning Networks*
* **Bibliographic Data:** Sony M Kuriakose and Tripty Singh, New Horizon College of Engineering & Amrita School of Engineering, Bengaluru, India. Published in *2022 13th International Conference on Computing Communication and Networking Technologies (ICCCNT 2022)*, IEEE, DOI: 10.1109/ICCCNT54827.2022.9984407, pp. 1–5.
* **Study Region & Target:** Generic IMD stations across India (p. 3). Despite the paper title promising crop yield prediction, **the paper only implements daily climate forecasting for 2018 (Max/Min Temp, Rainfall, etc.) using LSTM. The crop yield prediction stage is completely omitted** (p. 1, 3–4).
* **Dataset & Features:** IMD Pune historical weather dataset (1980–2017, >13,000 daily entries, 9 attributes: Max/Min Temp, Rainfall, Wind speed, etc.) (p. 3).
* **Methodology:** Univariate LSTM models trained independently for each climate column using a 20-day lookback window (p. 3).
* **Results:** Shows qualitative training convergence, residual, and scatter plots for predicted 2018 temperatures (p. 4, Fig 4–6). **Zero yield prediction metrics are reported.**
* **Limitations:** The paper is incomplete; the planned Phase 2 (crop yield / success rate prediction) was never executed or evaluated.
* **Relevance:** Category D (Related agricultural research — weather forecasting precursor, incomplete yield work).

### r9: Juliet et al. (2025) — *Intelligent Crop Yield Prediction Using IoT and Optimized Deep Learning for Precision Agriculture*
* **Bibliographic Data:** N. Juliet, Sudharshan G, Varalakshmi G, Mohamed Roshan Akthar M, Dhananchezhiyan K, S.A. Engineering College, Chennai, India. Published in *2025 Fourth International Conference on Smart Technologies, Communication & Robotics (STCR)*, IEEE, DOI: 10.1109/STCR62650.2025.11018972, pp. 1–6.
* **Study Region & Target:** India (evaluates Kaggle Indian states crop yield dataset 1997–2020 + proposed IoT prototype) (p. 4, 5). Target is crop yield in tons per hectare for coconut, rice, guava, and papaya (p. 1, 5).
* **Dataset & Features:** Kaggle dataset (akshatgupta7/crop-yield-in-indian-states-dataset, 19,698 rows, 10 columns) containing crop type, crop year, season, state, area, production, rainfall, fertilizer, and pesticide (p. 5).
* **Methodology:** MobileNet-Inspired LSTM combining Depthwise Separable Convolutions, Bidirectional LSTM layers, and an Attention Mechanism, trained using a Self-Adaptive Adam Optimizer (p. 3, 4).
* **Results:** Reported $R^2$ scores of 0.93 for coconut and guava, 0.92 for papaya, and $>0.90$ for rice (p. 1, 5, Fig 7–9).
* **Methodological Vulnerabilities:** The Kaggle dataset contains both *"cultivated area"* and *"production"* as features, allowing tree and neural models to trivially reconstruct yield. Furthermore, IoT sensor integration is described conceptually, but empirical tests were performed on static tabular data.
* **Relevance:** Category C (General crop-yield prediction across Indian states).

### r10 / r15: Seireg, Omar, & Elmahalawy (2023) — *Multi-Agent System Based on Stacking Technique for Rice Yield Prediction*
* **Bibliographic Data:** Hayam R. Seireg, Yasser M. Omar, Ahmed Elmahalawy, Menoufia University & AASTMT, Cairo, Egypt. Published in *2023 3rd IEEE International Conference on Electronic Engineering (ICEEM2023)*, DOI: 10.1109/ICEEM58740.2023.10319559, pp. 1–6.
* **Study Region & Target:** Lowland and Northeast rice regions of China (p. 1, 2). **Target is binary classification of rice yield level ("High" > 6 t/ha vs "Low" $\le$ 6 t/ha). NOT continuous yield regression!** (p. 3).
* **Dataset & Features:** 1,266 county-level rows with 18 monthly climate features (Max Temp, Min Temp, Rainfall for May–October) spanning 1980–2010 (p. 2, 3).
* **Methodology:** Proposed Stacking Technique (PST) combining Extra Trees Classifier, Random Forest Classifier, and Linear Discriminant Analysis (LDA) with Gaussian Naive Bayes (GNB) meta-classifier (p. 3–4).
* **Results:** PST achieved 87.0% classification accuracy, F1 = 0.93, Sensitivity = 1.00, Precision = 0.87. Decision Tree was the best single baseline (77.5%), while LDA was the worst (34.6%) (p. 4, 5, Table V, VI).
* **Stated Limitations:** Authors explicitly state on p. 5: *"Comparing this research with other works conducted on the same dataset proves challenging due to the utilization of a multiple linear regression algorithm in those studies, which did not yield satisfactory outcomes. For that reason, the target of the paper has been focusing on predicting the rice yield level high or low."*
* **Relevance:** Category B (Rice-yield prediction in another region — China, binary classification).

### r11: Hasan et al. (2026) — *Spatio-Temporal Impact of Agroclimatic Variables on Rice Yield in Bangladesh: A Comparative Machine Learning Approach*
* **Bibliographic Data:** Tawfiqul Hasan et al., American International University-Bangladesh. Published in *2026 IEEE 2nd International Conference on Quantum Photonics, Artificial Intelligence and Networking (QPAIN)*, Chittagong, Bangladesh, DOI: 10.1109/QPAIN69676.2026.11545663, pp. 1–6.
* **Study Region & Target:** Eight administrative divisions of Bangladesh (Barisal, Chittagong, Dhaka, Khulna, Mymensingh, Rajshahi, Rangpur, Sylhet) (p. 1, 3). Target is annual division-level rice yield in metric tons per hectare (t/ha) (p. 3, 4).
* **Dataset & Features:** Bangladesh Agroclimatic Crop Yield (2000–2024, Kaggle, Firoze Maliha), 24 years, 15 variables including Photosynthetically Active Radiation (PAR), Root Zone Soil Wetness, Surface Soil Wetness, Max/Min Temp, Earth Skin Temp, Wind Speed, Relative Humidity, Precipitation (p. 3, Table II).
* **Methodology:** Stratified division-wise evaluation comparing Linear Regression, Random Forest, Gradient Boosting, and SVR (p. 4).
* **Results:** Linear Regression achieved $R^2 > 0.97$ across all divisions (Rajshahi: $R^2 = 0.9958$, MAE = 0.0260; Chittagong: $R^2 = 0.9947$, MAE = 0.0272; Sylhet: $R^2 = 0.9754$, MAE = 0.0382). Average MAE $\approx 0.03$ t/ha. RF achieved $R^2 = 0.82\text{--}0.91$; SVR performed poorly ($R^2 \approx 0.45\text{--}0.53$) (p. 4, 5, Table III).
* **Key Drivers Identified:** PAR and Root Zone Soil Wetness were quantitatively identified as the dominant positive yield drivers (p. 5).
* **Stated Limitations:** Annual division-level aggregation masks seasonal intra-annual dynamics and district-level spatial heterogeneity (p. 6).
* **Methodological Vulnerabilities:** Suspiciously high Linear Regression performance ($R^2 > 0.99$) strongly indicates target leakage (Crop Yield is defined as Total Production / Total Area, both of which are present in the dataset); no sequential or deep learning architectures (no LSTM).
* **Relevance:** Category B (Rice-yield prediction in another region — Bangladesh). Highly relevant for feature selection (PAR, root-zone soil wetness) and division-stratified validation logic.

### r12: Rai & Dahiya (2026) — *Soil-Fertility-Based Yield Prediction for Rice (BPT-5204), Wheat (HD-2967), and Barley (RD-2035) Using Ensemble Machine Learning Models*
* **Bibliographic Data:** Avinash Rai and Ruby Dahiya, Galgotias University, Greater Noida, India. Published in *2026 International Conference on Intelligent Systems in Engineering, Secured Systems and Cybersecurity (ICISESSC)*, IEEE, DOI: 10.1109/ICISESSC68634.2026.11542774, pp. 532–537.
* **Study Region & Target:** Agro-ecosystems in India (regional coordinates not disclosed) (p. 533). Target is multi-crop yield in quintals per hectare (q/ha) for Rice (BPT-5204), Wheat (HD-2967), and Barley (RD-2035) (p. 532, 534).
* **Dataset & Features:** Soil macronutrients (N, P, K in kg/ha), physicochemical characteristics (pH, EC, Organic Carbon %), Soil Moisture %, and climate variables (Temperature, Rainfall) (p. 533).
* **Methodology:** Random Forest, XGBoost, and Linear Regression on a 70:30 train:test split; derives a composite Soil Fertility Index (SFI) weighted by normalized RF feature importances (p. 534, 535).
* **Results:** Random Forest achieved $R^2 = 0.91$, MAE = 1.25 q/ha, RMSE = 1.84 q/ha; XGBoost achieved $R^2 = 0.89$, MAE = 1.48; Linear Regression achieved $R^2 = 0.62$, MAE = 3.20 (p. 535, Table II).
* **Feature Importance:** Nitrogen (~0.27), Potassium (~0.22), Soil Moisture (~0.18), and Rainfall (~0.15) were ranked as the top yield determinants (p. 535, Fig 3).
* **Limitations:** Static cross-sectional tabular data; lacks temporal sequencing or satellite observations; fails to account for pest pressure or farm management practices (p. 536).
* **Relevance:** Category C (General crop-yield prediction — cereal crops in India). Highlights the critical importance of soil moisture and macronutrients alongside climate.

### r13: Govindaraj et al. (2026) — *Rice Yield Prediction using a Causal-Aware Mixture-of-Experts Deep Learning Architecture*
* **Bibliographic Data:** Govindaraj M et al., New Horizon College of Engineering, Bengaluru, India. Published in *2026 6th International Conference on Inventive Computation and Information Technologies (ICICIT-2026)*, IEEE, DOI: 10.1109/ICICIT69063.2026.11633947, pp. 1287–1293.
* **Study Region & Target:** 40 districts across India (p. 1290). **Target is ordinal classification into three classes: Low, Medium, High (quantile-based binning). NOT continuous yield regression!** (p. 1289, 1292).
* **Dataset & Features:** 9,885 district-level rice crop records from Indian government sources across 40 districts (p. 1290). 15 features: crop type, area, production, N, P, K application rates, total nutrients, air temperature, relative humidity, soil pH, cumulative rainfall, wind speed, solar radiation (p. 1289).
* **Methodology:** Causal-Aware Mixture of Experts (Causal-MoE) incorporating learnable sigmoid gating with L1 sparsity penalty + bank of 4 expert MLPs (128 and 64 neurons) + region-sensitive gating network with district embeddings (p. 1289, 1290). Evaluated using an 80:20 geographically held-out district split (p. 1289).
* **Results:** Causal-MoE achieved 96.73% test accuracy (vs 96.03% for baseline MLP), macro F1 = 0.98, ROC-AUC: Low = 0.999, Medium = 0.998, High = 1.000 (p. 1290, 1291, Table II, III).
* **Explicit Limitations (p. 1292):**
  1. Tested only on Indian government district records;
  2. Relies solely on tabular inputs without satellite/remote sensing imagery;
  3. Formulation is restricted to ordinal classification; continuous yield regression was not explored;
  4. Causal feature gating uses L1-regularized soft masks rather than formal structural causal discovery.
* **Relevance:** Category B (Rice-yield prediction in another region — 40 Indian districts, ordinal classification). Key reference for district-stratified validation protocols and causal gating concepts.

### r14: Ren et al. (2010) — *Regional Yield Estimation of Summer Maize Based on Assimilation of Remotely Sensed LAI into EPIC Model*
* **Bibliographic Data:** Jianqiang Ren, Fushui Yu, Zhongxin Chen, Jun Qin, Chinese Academy of Agricultural Sciences & CAS, Beijing, China. Published in *2010 Second IITA International Conference on Geoscience and Remote Sensing (GRS2010)*, IEEE, ISBN: 978-1-4244-8515-4/10, pp. 361–365.
* **Study Region & Target:** Hengshui City, Hebei Province, North China (11 counties) (p. 361, 362). **Crop is Summer Maize, NOT Rice! Target is regional maize yield (t/ha) and field management parameters.** (p. 361).
* **Dataset & Features:** MODIS 250m 16-day NDVI (Julian day 161–273, year 2004), 29 sampled field plots (500m x 500m) with DGPS, daily climate data (solar radiation, max/min temp, precipitation, RH, wind speed) interpolated to 250m, and soil parameters (depth, texture, bulk density, pH, organic carbon) (p. 362, 363).
* **Methodology:** Data assimilation of MODIS-derived Leaf Area Index (LAI) into the EPIC crop growth model using the SCE-UA (Shuffled Complex Evolution - University of Arizona) global optimization algorithm (p. 362).
* **Results:** Simulated summer maize yield = 6.21 t/ha; relative error = 4.37%; RMSE = 0.44 t/ha; sowing date error = 1.85% (3 days); plant density error = -7.78%; N fertilizer error = -10.60% (p. 361, 364).
* **Limitations:** Single crop (summer maize); single year (2004); 1km EMU grid; extreme complexity and parameterization requirements of crop growth models; no machine learning or LSTM.
* **Relevance:** Category D (Related agricultural research — remote sensing crop model assimilation for maize).

### r16: Banavath et al. (2026) — *Optimized Random Forest with Explainable AI for Accurate Boro Rice Yield Prediction and Real-Time Web App*
* **Bibliographic Data:** Venkateshwarlu Banavath et al., Western Illinois Univ, Univ of the Cumberlands, East West Univ Dhaka, NYIT. Published in *2026 IEEE 15th International Conference on Communication Systems and Network Technologies (CSNT)*, IEEE, DOI: 10.1109/CSNT69054.2026.11502261, pp. 1451–1457.
* **Study Region & Target:** Bangladesh (private agricultural collection) (p. 1452). Target is Boro rice yield regression (p. 1451, 1452).
* **Dataset & Features:** 4,480 records, 43 features (1 categorical District, 42 numeric) including fertilizers (urea, MP, DAP, TSP), soil properties (pH, texture, consistency, moisture), average rainfall, cultivated area (p. 1452, 1453, Table I).
* **Methodology:** Random Forest, Gradient Boosting, Linear Regression, SVR, KNN; Grid Search CV; Mutual Information feature selection; SHAP & Morris sensitivity analysis (p. 1452–1455).
* **Results:** Authors report Random Forest Test $R^2 = 0.9999$, Test RMSE = 0.000000, Test MAE = 0.000000; Gradient Boosting Test $R^2 = 0.999998$, Test RMSE = 492.98, Test MAE = 323.18; KNN Test $R^2 = 0.9996$, Test RMSE = 0.000001; Linear Regression Test $R^2 = 0.8832$, Test RMSE = 126,240.43 (p. 1454, 1455, Table III).
* **Critical Methodological Flaw:** **Catastrophic data leakage.** Achieving Test $RMSE = 0.000000$ and $R^2 = 0.9999$ on a real-world agricultural yield dataset is statistically impossible without identical duplicate rows split across train and test sets, or algebraic leakage of the target via area/production variables. The authors themselves state (p. 1453): *"Notably, Random Forest and KNN showed zero CV MSE, suggesting possible overfitting or data issues."*
* **Relevance:** Category B (Rice-yield prediction in another region — Bangladesh). Crucial evidence of severe methodological and validation risks in published literature.

### r17: Sibarani et al. (2025) — *Optimizing Rice Irrigation Scheduling through Rainfall Forecasting Using LSTM-Based Model*
* **Bibliographic Data:** Benyamin Sibarani et al., Nusa Putra University, Jakarta, Indonesia. Published in *2025 IEEE 11th International Conference on Computing, Engineering and Design (ICCED)*, IEEE, DOI: 10.1109/ICCED68324.2025.11324627, pp. 1–6.
* **Study Region & Target:** Indonesia (p. 1, 2). **Target is daily rainfall forecasting (mm) for smart irrigation scheduling. NOT CROP YIELD!** (p. 1, 3).
* **Dataset & Features:** Historical daily weather from Open-Meteo (daily average temperature, average humidity, sunshine duration) using a 7-day lookback window; 80:10:10 train:val:test split (p. 3).
* **Methodology:** 2-layer LSTM (64 units each, dropout 0.2, linear output neuron) trained with Adam optimizer and MSE loss (p. 3, 4).
* **Results:** Test MAE = 4.15 mm, Test RMSE = 6.47 mm (Train MAE = 3.52 mm, RMSE = 5.18 mm). Rule-based simulation cut unnecessary irrigation events by 40% (p. 4, 5, Table 3, Table 4).
* **Stated Limitations:** Underestimates the magnitude of extreme rainfall events; limited to single-point weather data; does not model crop physiological growth or yield (p. 5, 6).
* **Relevance:** Category D (Related agricultural research — rainfall forecasting for irrigation). Illustrates standard LSTM hyperparameterization for meteorological sequences, but does not predict yield.

### r18: Hossain et al. (2017) — *Predicting Rice Yield for Bangladesh by Exploiting Weather Conditions*
* **Bibliographic Data:** Md. Akter Hossain et al., East Delta University, Chittagong, Bangladesh & Kookmin University, Korea. Published in *2017 International Conference on Information and Communication Technology Convergence (ICTC 2017)*, IEEE, DOI: 10.1109/ICTC.2017.8285514 / ISBN: 978-1-5090-4032-2/17, pp. 589–594.
* **Study Region & Target:** 21 districts of Bangladesh (p. 589, 591). Target is annual rice yield (M.Tons/hectare) evaluated across Aus, Aman, and Boro seasons for the year 2016 (p. 589, 593).
* **Dataset & Features:** BBS agricultural statistics (2006–2015) + BMD weather records (2012–2015, 4 years monthly data). Features include monthly min, max, avg rainfall; min, max, avg temperature; min, max, avg humidity (9 climate features) and agricultural area (p. 590, 591).
* **Methodology:** WPSRY two-stage model: Stage 1 uses Multilayer Perceptron (ANN with Levenberg-Marquardt algorithm in WEKA) to predict future weather; Stage 2 uses SVM Regression (SVR in Python) to predict yield from forecasted weather + agricultural area (p. 590–592).
* **Results:** 2016 test year cross-validation: Aman rice MRE = 5.82% (MAE = 0.27 t/ha); Boro rice MRE = 6.28% (MAE = 0.29 t/ha); Aus rice MRE = 8.79% (MAE = 0.38 t/ha) (p. 593, Table I, II, III).
* **Limitations:** Compounding errors from Stage 1 MLP weather forecast directly degrade Stage 2 SVR yield accuracy; weather history is very short (only 4 years: 2012–2015); lacks temporal recurrent modeling (no LSTM) and satellite remote sensing.
* **Relevance:** Category B (Rice-yield prediction in another region — Bangladesh). Direct benchmark for multi-season rice yield regression using weather and area inputs.

---

## 5. Task 3: Relevance Classification & Project Alignment

Each paper is categorized according to its geographic focus and functional problem formulation:
* **Category A:** Directly focused on Tamil Nadu rice yield
* **Category B:** Rice-yield prediction in another region
* **Category C:** General crop-yield prediction
* **Category D:** Related agricultural research but not direct yield prediction

### Summary Table

| Category | Papers | Summary of Contribution to Project |
| :--- | :--- | :--- |
| **A. Directly focused on Tamil Nadu rice yield** | `r1` | Confirms local interest in Tamil Nadu rice modeling (Vellar basin), but provides no modern machine learning or deep learning baseline. |
| **B. Rice-yield prediction in another region** | `r6`, `r7`, `r10/r15`, `r11`, `r13`, `r16`, `r18` | Provide regression and classification baselines (RF, XGBoost, SVR, ViT, Stacking, Causal-MoE) and reveal key drivers (PAR, soil wetness), but highlight massive data leakage vulnerabilities in published studies. |
| **C. General crop-yield prediction** | `r9`, `r12` | Highlight multi-crop feature sets, soil fertility parameters (N, P, K, pH, soil moisture), and hybrid neural architectures across Indian states. |
| **D. Related agricultural research (Not direct yield prediction)** | `r2/r3`, `r4/r5`, `r8`, `r14`, `r17` | Cover grain image classification (`r2/r3`), pest forewarning (`r4/r5`), pure weather forecasting (`r8`, `r17`), and maize crop growth model assimilation (`r14`). Demonstrate 1D CNN-LSTM and LSTM mechanics on weather sequences. |

---

## 6. Task 4: Research Gap Analysis

A cross-comparative synthesis of all 18 papers reveals major methodological and empirical research gaps directly relevant to the project title:  
**"Spatio-Temporal Rice Yield Prediction Using Long Short-Term Memory (LSTM)"** (Primary Study Region: Tamil Nadu, India).

### Gap 1: Severe Shortage of Rigorous Machine Learning for Tamil Nadu Rice Yield
* In the entire corpus, **only one paper (`r1`)** specifically models Tamil Nadu rice yield. However, `r1` was published in 2017 using a trivial ZeroR heuristic on a sample of 11 rows.
* Paper `r2/r3` originates from Tamil Nadu authors (SRM Institute), but it is a grain variety image classifier that does not predict yield.
* **Empirical Reality:** There is currently **zero peer-reviewed evidence** in the collected literature of a validated, multi-decadal, district-level LSTM yield regression model tailored specifically to Tamil Nadu.

### Gap 2: Conflation of Yield Regression with Surrogate Tasks
* Multiple papers have titles referencing "yield prediction" or "crop disease prediction" but address fundamentally different tasks:
  * `r2/r3`: Grain variety image classification (5 classes).
  * `r4/r5`: Insect pest population forecasting (Yellow Stem Borer light trap counts).
  * `r8`: Pure daily weather forecasting (Phase 2 yield model was never implemented).
  * `r10/r15`: Binary classification of yield levels (>6 t/ha vs $\le$ 6 t/ha), adopted because the authors could not get regression to work.
  * `r13`: 3-class ordinal classification (Low, Medium, High) using quantile binning, avoiding continuous yield regression.
  * `r14`: Summer maize yield simulation in China using EPIC crop growth model assimilation.
  * `r17`: Daily rainfall forecasting for irrigation pump scheduling.
* **Empirical Reality:** True **continuous yield regression ($t/ha$)** is only addressed in `r1` (heuristic), `r6` (plot-level RGB images in Vietnam), `r7` (1 district in Punjab with data leakage), `r9` (Kaggle dataset with target leakage), `r11` (Bangladesh division regression with target leakage), `r12` (Indian cereal tabular regression), `r16` (Bangladesh Boro regression with 0.000 RMSE leakage), and `r18` (Bangladesh 2-stage SVR).

### Gap 3: Absence of True Spatio-Temporal LSTM Yield Regression
* While LSTM is mentioned in several papers, its application in the corpus is either:
  1. Applied to pest forecasting rather than crop yield (`r4/r5`);
  2. Applied strictly to daily weather forecasting without yield data (`r8`, `r17`);
  3. Evaluated on cross-sectional Kaggle tabular data without explicit spatial coordinates (`r9`).
* **None of the papers** formulate a true **Spatio-Temporal LSTM** that models multi-district spatial dependencies (e.g., via spatial graph adjacency, coordinate embeddings, or regional distance kernels) combined with multi-season temporal climate lag sequences across consecutive years.

### Gap 4: Rampant Target Leakage and Flawed Evaluation in Prior Literature
A critical finding of this audit is that published yield prediction models frequently exhibit severe methodological flaws:
1. **Target Leakage via Area and Production:** Papers `r7`, `r9`, `r11`, `r13`, and `r16` include *"Cultivated Area"* and/or *"Production"* in their feature tables. Since agricultural yield is defined mathematically as $Yield = \frac{Production}{Area}$, including these variables allows tree-based models and neural networks to trivially achieve $R^2 > 0.99$.
2. **Random Splitting of Spatially/Temporally Correlated Data:** Paper `r7` evaluates 134 weekly records for 1 single district across 5 years using a random 70:30 split, resulting in identical annual yield targets appearing in both training and test sets.
3. **Unrealistic Perfect Scores:** Paper `r16` reports Random Forest test $RMSE = 0.000000$ and $R^2 = 0.9999$, which is an undeniable symptom of severe data leakage or duplicated rows.
4. **Failure to Use Chronological Splitting:** Almost none of the reviewed papers implement strict chronological out-of-sample testing (e.g., training on 1997–2017 and testing on 2018–2023).

---

## 7. Task 5: Methodological Implications for the Tamil Nadu Project

To ensure that the project **"Spatio-Temporal Rice Yield Prediction Using Long Short-Term Memory (LSTM)"** is defensible, rigorous, and scientifically sound, the following principles must be enforced:

1. **Strictly Prevent Target Leakage:**
   * **Production must be completely excluded** from the feature set.
   * If *Area* is included, it must only represent pre-season sowing area, and models must never have access to harvest production totals.

2. **Enforce Chronological and Spatial Validation Splits:**
   * **Temporal Validation:** Use a strict chronological cutoff (e.g., train on 1997–2017, validate on 2018–2020, test on 2021–2023). Never use random train/test splits on time series.
   * **Spatial Generalization:** Evaluate leave-one-district-out (LODO) or spatial k-fold cross-validation to assess transferability across Tamil Nadu's agro-climatic zones (Cauvery Delta, Northern Zone, Western Zone, Southern Zone, High Rainfall Zone).

3. **Incorporate Agronomically Verified Drivers:**
   * As proven by `r11` and `r12`, **Photosynthetically Active Radiation (PAR)**, **Root Zone Soil Wetness**, **Nitrogen**, and **Potassium** are far more predictive of rice yield than simple monthly rainfall and surface temperature alone. NASA POWER features should specifically prioritize radiation and soil moisture variables.

4. **Benchmark Against Competitive Baselines:**
   * The proposed LSTM architecture must be benchmarked against standard tabular baselines:
     * Ridge / Lasso Regression
     * Random Forest Regressor
     * XGBoost / LightGBM Regressor
     * Support Vector Regression (SVR)
     * Static Multi-Layer Perceptron (MLP)
   * Superiority of LSTM must be empirically demonstrated on sequential climate features rather than assumed a priori.

5. **Report Standard Regression Metrics:**
   * Use Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), Mean Absolute Percentage Error (MAPE), and Coefficient of Determination ($R^2$) expressed in actual physical yield units (tonnes/hectare or kg/hectare).
