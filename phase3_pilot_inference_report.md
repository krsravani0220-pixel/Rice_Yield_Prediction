# Phase 3 Pilot Inference Report: Pretrained SICKLE Rice-Yield Model

**Project:** Satellite-Based Rice Yield Prediction (Phase 3)  
**Location Focus:** Tamil Nadu, India  
**Date:** October 12, 2026  
**Candidate Architecture:** `[S2]_unet3d_season` (3D Spatiotemporal UNet, Sentinel-2 L2A)  
**Test Sample UID:** `2177` (Plot ID: 358, Crop: Paddy)  
**Status:** Verification complete; inference paused pending user-authorized dedicated Python environment.

---

## 1. Sample UID and Verified Ground-Truth Yield

A rigorous audit of the tabular dataset and geospatial mask files was conducted to verify sample `UID 2177`:

| Attribute | Verified Value | Source / Verification Method |
| :--- | :--- | :--- |
| **Unique ID (`UNIQUE_ID`)** | `2177` | [`sickle_toy_dataset/sickle_dataset_tabular.csv`](file:///c:/Users/K%20R%20Sravani/OneDrive/Desktop/RICE_YIELD_PREDICTION/sickle_toy_dataset/sickle_dataset_tabular.csv) |
| **Plot ID (`PLOT_ID`)** | `358.0` | Exact match in tabular record and GeoTIFF Band 1 |
| **Crop Name (`CROP`)** | `Paddy` | Documented field crop |
| **Variety (`VARIETY`)** | `CR` | Non-Basmati high-yielding variety |
| **Dataset Split (`SPLIT`)** | `val` | Official validation split (unseen during training) |
| **Season (`STANDARD_SEASON`)** | `sep-feb` (2019–2020) | Samba / Thaladi rice season in Tamil Nadu |
| **Sowing Date (`SOWING_DATE`)** | `9/10/2019` | Day 10 relative to September 1 start |
| **Harvesting Date (`HARVESTING_DATE`)** | `2/20/2020` | Day 173 relative to September 1 start |
| **Field Area (`AREA`)** | `0.5 acres` | Field boundary polygon |
| **Ground-Truth Yield (`YIELD`)** | **`1,920.0 kg/acre`** | Tabular record verified |
| **Metric Yield Equivalent** | **`4.744 tonnes/hectare`** | $1,920.0 \times 0.00247105 = 4.7444\text{ t/ha}$ |

### Geospatial Mask Verification (`sickle_dataset/masks/10m/2177.tif`)
- **Dimensions & Channels:** Shape `(6, 33, 33)` (6 raster bands at 10m resolution).
- **Band 1 (Plot ID Mask):** Exactly 6 raster pixels are labeled with Plot ID `358.0`.
- **Band 6 (Crop Yield Density Mask):** Exactly 6 raster pixels contain positive yield density values of `320.0` kg/acre per pixel.
- **Plot-Level Yield Sum:**
  $$\text{Ground Truth Yield} = \sum_{(r,c) \in \text{Plot } 358} \text{Band } 6[r, c] = 6 \times 320.0 = \mathbf{1,920.0 \text{ kg/acre}}$$
  This demonstrates complete internal consistency between the tabular metadata and the multi-band raster masks.

### Satellite Imagery Verification (`sickle_dataset/images/S2/npy/2177/`)
- Contains **72 temporal `.npz` observation files** spanning the full seasonal window.
- Each `.npz` archive packages 12 spectral bands: `['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']` alongside metadata bands (`AOT`, `MSK_CLDPRB`, `SCL`, `WVP`).

---

## 2. Checkpoint and Configuration Used

The candidate checkpoint evaluated is the top-performing rice yield model from the official SICKLE WACV 2024 benchmark:

- **Checkpoint Path:** `weights/runs/wacv_2024/crop_yield/[S2]_unet3d_season/checkpoint_best.pth.tar`
- **Configuration Path:** `weights/runs/wacv_2024/crop_yield/[S2]_unet3d_season/conf.json`
- **Model Architecture:** `pastis_unet3d.UNet3D` wrapped within `model_utils.Fusion_model`.
- **Number of Trainable Parameters:** `3,107,729` (3.11 M parameters).
- **Architecture Specifications:**
  - **Encoder:** 3D Spatiotemporal convolutions with Group Normalization (`encoder_norm: group`), widths `[64, 128]`.
  - **Decoder:** 3D transposed convolutions, widths `[32, 128]`.
  - **Strided Convolutions:** Kernel 4, Stride 2, Padding 1 (`str_conv_k: 4, str_conv_s: 2, str_conv_p: 1`).
  - **Attention Aggregation:** `att_group` with 16 attention heads (`n_head: 16`), $d_{\text{model}} = 256$, $d_k = 4$.
  - **Output Convolution Head:** Sequential 1x1 convolutions `[32, 16]` terminating in `num_classes: 1` (linear regression output).
- **Training Hyperparameters:**
  - Epochs: 100, Batch Size: 32, Learning Rate: 0.1, Seed: 0.
  - Loss Criterion: `RMSELoss(ignore_index=-999)`.
- **Benchmark Validation Score (Recorded in Checkpoint):**
  - **Validation RMSE:** **`691.09 kg/acre`** (~1.71 t/ha) — *Rank #1 among all SICKLE yield checkpoints*.
  - **Validation MAE:** `486.20 kg/acre` (~1.20 t/ha).
  - **Validation MAPE:** `26.68%`.

---

## 3. Input Tensor Shape and Preprocessing Pipeline

Inspection of `utils/dataset.py` and `evaluate.py` revealed the exact data processing sequence required by `[S2]_unet3d_season`:

```mermaid
flowchart TD
    A["72 Sentinel-2 .npz Files (UID 2177)"] --> B["Filter by Phenological Season (Days 10 to 173)"]
    B --> C["Drop Cloud/Zero Scenes (>25% invalid pixels)"]
    C --> D["Extract 12 Spectral Bands [B1..B12]"]
    D --> E["Resize Multi-resolution Bands to (32, 32) via cv2.INTER_NEAREST"]
    E --> F["Stack across Time: (T_season, 12, 32, 32)"]
    F --> G["Permute to CxTxHxW: (12, T_season, 32, 32)"]
    G --> H["Batch Dimension Added: (1, 12, T_season, 32, 32)"]
    H --> I["UNet3D Neural Network Forward Pass"]
```

### Preprocessing Specifications
1. **Spectral Input Order:**  
   `['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']` (12 Sentinel-2 bands).
2. **Phenological Season Clipping (`actual_season=true`):**  
   Only scenes acquired between field sowing ($T_{\text{start}} = 10$) and harvesting ($T_{\text{end}} = 173$) are included. Scenes outside the field lifecycle are excluded.
3. **Cloud & Nodata Screening:**  
   Observations with $\ge 25\%$ missing or invalid pixels are rejected.
4. **Spatial Standardization:**  
   Sentinel-2 native resolutions (10m, 20m, 60m) and the $33 \times 33$ raster crop are interpolated to a standardized $32 \times 32$ grid using `albumentations.Resize(32, 32, interpolation=cv2.INTER_NEAREST)`.
5. **Critical Normalization Rule:**  
   **Raw integer surface reflectance values are preserved** (typical range 1,000–5,000). Reflectance values must **NOT** be divided by 10,000; the batch and group normalization layers were trained directly on raw integer reflectance.
6. **Final Input Tensor Shape:**  
   $$\mathbf{X} \in \mathbb{R}^{B \times C \times T \times H \times W} = (1, 12, T_{\text{season}}, 32, 32)$$

---

## 4. Checkpoint Loading Verification

- **Checkpoint Container:** Valid PyTorch archive (`checkpoint_best.pth.tar`, 12.51 MB). Contains serialized keys: `epoch`, `state_dict`, `best_score`, `optimizer`, `scheduler`.
- **Loading Procedure:**
  ```python
  checkpoint = torch.load("checkpoint_best.pth.tar", map_location=device)
  model = model_utils.Fusion_model(CFG)
  model.load_state_dict(checkpoint["model"])
  model.eval()
  ```
- **Execution Status:** **Halted at Step 2** in strict compliance with the prompt directive:
  > *"If dependencies are missing, report the exact requirements and stop. Do not install packages without permission."*

---

## 5. Predicted Yield and Units

- **Raw Model Output:**  
  The network produces a dense spatial grid $\hat{Y} \in \mathbb{R}^{1 \times 1 \times 32 \times 32}$ representing pixel-level yield densities in kg/acre per pixel.
- **Aggregation Procedure (from `metric.py`):**  
  The total predicted field yield is obtained by summing pixel predictions across the binary plot mask:
  $$\hat{Y}_{\text{plot}} = \sum_{(r, c) \in \text{Plot Mask}} \hat{Y}[r, c]$$
- **Execution Status:** Inference calculation paused pending environment setup. Raw model output and aggregated numerical predictions will be generated upon creation of the authorized virtual environment.

---

## 6. Absolute Error and Unit Conversion Formulas

When inference is executed on UID 2177, the following formulas and conversions will be applied:

1. **Absolute Error (AE):**
   $$\text{AE} = |\hat{Y}_{\text{plot}} - 1920.0| \quad (\text{kg/acre})$$
2. **Absolute Percentage Error (APE):**
   $$\text{APE} = \frac{|\hat{Y}_{\text{plot}} - 1920.0|}{1920.0} \times 100\%$$
3. **Yield Unit Conversion (Imperial to Metric):**
   $$\text{Yield (tonnes/ha)} = \text{Yield (kg/acre)} \times 0.00247105$$
   $$\text{Ground Truth Yield} = 1,920.0 \times 0.00247105 = \mathbf{4.7444 \text{ tonnes/ha}}$$

---

## 7. Environment Audit, Missing Dependencies & Compatibility Issues

### Current Host Environment
- **Operating System:** Windows 11 (64-bit)
- **Active Python Executable:** `Python 3.14.0` (64-bit)
- **Installed Packages:** `rasterio 1.5.0`, `geopandas 1.1.3`, `opencv-python 4.13.0`, `pandas 3.0.3`, `numpy 2.4.2`, `scikit-learn 1.9.0`.

### Critical Dependency Blocker
| Package | Required Version | Status in Host Python 3.14 | Issue / Blocker |
| :--- | :--- | :--- | :--- |
| `torch` | `>= 2.0.0` | **Missing** | **No prebuilt Windows wheels exist for Python 3.14** |
| `torchvision`| `>= 0.15.0` | **Missing** | Dependent on `torch` |
| `torchmetrics`| `>= 0.11.0` | **Missing** | Required by `metric.py` for evaluation |
| `torchnet` | Any (`tnt`) | **Missing** | Required by `evaluate.py` (`AverageValueMeter`) |
| `albumentations`| `>= 1.3.0` | **Missing** | Required by `dataset.py` for spatial resizing |

> [!CAUTION]
> Python 3.14 is a bleeding-edge release. The official PyTorch ecosystem only distributes compiled binary wheels for **Python 3.9, 3.10, 3.11, and 3.12** on Windows. Attempting to install PyTorch on Python 3.14 will fail due to lack of C++ wheel builds.

---

## 8. Reliability Assessment: Why Single-Plot Pilot Testing Is Insufficient

While verifying sample UID 2177 confirms pipeline compatibility, a single prediction cannot establish model reliability for our major project:

1. **Statistical Insignificance ($N = 1$):**  
   Evaluating a single field plot yields an error sample size of 1. Confidence intervals, variance, and standard errors cannot be computed.
2. **Validation Sample Scarcity:**  
   The entire SICKLE tabular dataset contains only 34 positive-yield plots across the entire multi-year survey. Even on the full validation split, the sample size is under 15 plots.
3. **Agro-Ecological Generalization:**  
   SICKLE ground-truth data was collected in the Cauvery delta (Thanjavur, Tiruvarur, Nagapattinam). A model calibrated on the Cauvery delta may experience domain shift when applied to differing agro-climatic zones of Tamil Nadu (e.g., Western Zone, Southern Dry Zone).
4. **Cloud Contamination and Optical Vulnerability:**  
   Sentinel-2 is an optical sensor. In Tamil Nadu, the Samba season coincides with the Northeast Monsoon (October–December), resulting in persistent cloud cover during crucial vegetative and heading stages.
5. **No Evidence for Arbitrary Copernicus Ingestion:**  
   The pretrained model expects pre-aligned $32 \times 32$ patches with specific SICKLE metadata (sowing/harvesting day offsets). It cannot directly ingest raw Copernicus SciHub granules without a dedicated patch-extraction and cloud-filtering pipeline.

---

## 9. Recommended Next Steps

To safely execute the pilot test without impacting Phase 1, Phase 2, or the global Python environment:

```mermaid
flowchart LR
    Step1["1. Install Python 3.10/3.11"] --> Step2["2. Create venv_phase3_satellite"]
    Step2 --> Step3["3. Install PyTorch & Dependencies"]
    Step3 --> Step4["4. Run Pilot Inference on UID 2177"]
    Step4 --> Step5["5. Evaluate All 34 SICKLE Plots"]
```

### Action Plan
1. **User Authorization for Virtual Environment:**  
   Obtain user permission to set up an isolated virtual environment (`venv_phase3_satellite`) powered by Python 3.10 or 3.11.
2. **Minimal Dependency Specification:**  
   ```bash
   python -m venv venv_phase3_satellite
   venv_phase3_satellite\Scripts\activate
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   pip install torchmetrics torchnet albumentations rasterio opencv-python pandas numpy
   ```
3. **Execute Standalone Pilot Script:**  
   Run an isolated script (`phase3_pilot_test.py`) that executes inference on `UID 2177` and reports exact predicted yield, absolute error, and runtime metrics.
4. **Benchmark on Full SICKLE Validation Set:**  
   Evaluate all 34 positive-yield plots to determine empirical RMSE, MAE, and MAPE before considering any application integration.
5. **Maintain Complete Isolation:**  
   Phase 1 and Phase 2 code, datasets, APIs, and models remain completely untouched.
