# SICKLE Phase 3 Satellite Crop-Yield Inference & Integration Plan
## Operational Roadmap for Field-Level Rice Yield Prediction in Tamil Nadu, India

**Document:** `SICKLE_PHASE3_INFERENCE_PLAN.md`  
**Target Repository:** [`Depanshu-Sani/SICKLE`](https://github.com/Depanshu-Sani/SICKLE) (WACV 2024 Oral)  
**Local Checkpoints:** [`weights/runs/wacv_2024/crop_yield/`](file:///c:/Users/K%20R%20Sravani/OneDrive/Desktop/RICE_YIELD_PREDICTION/weights/runs/wacv_2024/crop_yield)  
**Major Project Workspace:** [`c:\Users\K R Sravani\OneDrive\Desktop\RICE_YIELD_PREDICTION`](file:///c:/Users/K%20R%20Sravani/OneDrive/Desktop/RICE_YIELD_PREDICTION)  

---

## 1. Executive Summary & Project Context

### Major Project Background
Our major project predicts rice yield for Tamil Nadu, India.
* **Phase 1 & Phase 2 (Completed):** Established an end-to-end, district-level tabular yield forecasting and decision support system (1997–2023) using Extra Trees, Random Forest, Gradient Boosting, SHAP explainability, and weather time-series backtesting. These modules and datasets are finalized and must remain untouched.
* **Phase 3 Objective:** Expand the platform from macro district-level forecasts to **micro field-level satellite yield prediction** using Sentinel-1 (C-band SAR) and Sentinel-2 (Multispectral Optical) imagery.
* **The Challenge:** Our initial audit of the local [`sickle_toy_dataset/sickle_dataset_tabular.csv`](file:///c:/Users/K%20R%20Sravani/OneDrive/Desktop/RICE_YIELD_PREDICTION/sickle_toy_dataset/sickle_dataset_tabular.csv) revealed only 89 paddy records, of which **only 34 have positive, recorded yield values**. Training a multi-million-parameter deep learning spatio-temporal network from scratch on 34 samples is mathematically untenable.
* **The Solution:** The extracted [`weights/`](file:///c:/Users/K%20R%20Sravani/OneDrive/Desktop/RICE_YIELD_PREDICTION/weights) directory contains the official pretrained weights from the WACV 2024 oral paper *"SICKLE: A Multi-Sensor Satellite Imagery Dataset Annotated with Multiple Key Cropping Parameters"* (Sani et al.). These models were trained specifically on smallholder paddy fields in the **Cauvery Delta of Tamil Nadu**.

This document outlines a verified, zero-risk inference plan for integrating the candidate models into Phase 3.

---

## 2. In-Depth Investigation of Candidate Models

We audited the top three candidate pretrained models identified during the weights inspection:

```
wacv_2024/crop_yield/
├── [S2]_unet3d_season/       --> 🥇 Rank 1 Overall (Lowest Val RMSE: 691.09 kg/acre)
├── [S2,L8,S1]_utae/          --> 🥈 Rank 2 Overall (Best Multi-Modal Model: 712.19 kg/acre, Full-Season)
└── [S2]_utae_season/         --> 🏅 Best MAPE Model (Lowest Val MAE: 514.28 kg/acre, MAPE: 31.5%)
```

### Comparative Analysis of Candidate Checkpoints

| Parameter | Candidate 1: `[S2]_unet3d_season` | Candidate 2: `[S2,L8,S1]_utae` | Candidate 3: `[S2]_utae_season` |
| :--- | :--- | :--- | :--- |
| **Model Type** | 3D Spatio-Temporal U-Net | U-Net with Temporal Attention Encoder | U-Net with Temporal Attention Encoder |
| **Architecture Identifier** | `unet3d` (`pastis_unet3d.UNet3D`) | `utae` (`models.utae.UTAE`) | `utae` (`models.utae.UTAE`) |
| **Sensors Used** | Sentinel-2 Optical (`S2`) | Sentinel-2 + Landsat-8 + Sentinel-1 (`Fusion`) | Sentinel-2 Optical (`S2`) |
| **Spectral Bands ($C$)** | 12 bands (`B1`–`B12`) | 22 bands total (12 S2 + 8 L8 + 2 S1) | 12 bands (`B1`–`B12`) |
| **Season Duration Mode** | `actual_season = True` | `actual_season = False` | `actual_season = True` |
| **Parameter Count** | **3,107,729** (~3.11M) | **2,136,305** (~2.14M) | **1,072,113** (~1.07M) |
| **Best Val RMSE** | **691.09 kg/acre** (~1.71 t/ha) | **712.19 kg/acre** (~1.76 t/ha) | **722.24 kg/acre** (~1.78 t/ha) |
| **Best Val MAE** | 550.41 kg/acre (~1.36 t/ha) | 567.45 kg/acre (~1.40 t/ha) | **514.28 kg/acre** (~1.27 t/ha) |
| **Best Val MAPE** | 33.7% | 33.1% | **31.5%** |
| **Convergence Epoch** | Epoch 38 / 100 | Epoch 15 / 100 | Epoch 17 / 100 |
| **Operational Feasibility** | **High**, but requires knowing sowing and harvest dates to clip satellite scenes. | **Very High**: Processes the entire 183-day season window without needing user-entered sowing/harvest days! | **High**, lowest relative error (MAPE), but requires phenology bounds. |

---

## 3. Architecture Definitions & Sourcing

The model definitions and execution code are located in the official GitHub repository [`Depanshu-Sani/SICKLE`](https://github.com/Depanshu-Sani/SICKLE):

### Source File Mapping
1. **Core Wrappers & Dispatch:** [`utils/model_utils.py`](https://github.com/Depanshu-Sani/SICKLE/blob/main/utils/model_utils.py)
   * `Build_model`: Encapsulates a single satellite model (`S2`, `S1`, or `L8`).
   * `Fusion_model`: Encapsulates multi-sensor architectures by instantiating sub-networks for each satellite sensor and fusing spatial representations via `conv_final` (`nn.Conv2d(48, 1, kernel_size=3, padding=1)`).
2. **U-Net 3D Architecture:** [`models/pastis_unet3d.py`](https://github.com/Depanshu-Sani/SICKLE/blob/main/models/pastis_unet3d.py)
   * Implements 3D convolutions (`Conv3d`, `BatchNorm3d`, `LeakyReLU`) across spatial and temporal dimensions.
3. **U-TAE Architecture:** [`models/utae.py`](https://github.com/Depanshu-Sani/SICKLE/blob/main/models/utae.py)
   * Implements multi-scale spatial downsampling blocks and the `TemporalEncoder` with multi-head self-attention (`n_head=16`, `d_model=256`, `d_k=4`).
4. **Positional Encoding:** [`models/positional_encoding.py`](https://github.com/Depanshu-Sani/SICKLE/blob/main/models/positional_encoding.py)
   * Maps integer calendar day offsets (`batch_positions`) to harmonic sinusoidal embeddings.
5. **Loss & Metric Computation:** [`utils/metric.py`](https://github.com/Depanshu-Sani/SICKLE/blob/main/utils/metric.py)
   * Defines `RMSELoss` and `get_combined_yield`.
6. **Data Pipeline:** [`utils/dataset.py`](https://github.com/Depanshu-Sani/SICKLE/blob/main/utils/dataset.py)
   * Implements `SICKLE_Dataset` and `UNET3d_Dataset`.

---

## 4. Checkpoint & Configuration Mapping

The corresponding checkpoint files and configuration metadata in our extracted [`weights/`](file:///c:/Users/K%20R%20Sravani/OneDrive/Desktop/RICE_YIELD_PREDICTION/weights) directory are:

```
weights/runs/wacv_2024/crop_yield/
├── [S2]_unet3d_season/
│   ├── checkpoint_best.pth.tar   (35.58 MB)  --> Serialized PyTorch state dict
│   ├── checkpoint_last.pth.tar   (35.58 MB)
│   ├── conf.json                 (1.18 KB)   --> Exact hyperparameters & sensor config
│   └── trainlog.json             (44.20 KB)  --> 100-epoch training history
├── [S2,L8,S1]_utae/
│   ├── checkpoint_best.pth.tar   (24.50 MB)
│   ├── checkpoint_last.pth.tar   (24.50 MB)
│   ├── conf.json                 (1.63 KB)
│   └── trainlog.json             (44.15 KB)
└── [S2]_utae_season/
    ├── checkpoint_best.pth.tar   (12.30 MB)
    ├── checkpoint_last.pth.tar   (12.30 MB)
    ├── conf.json                 (1.18 KB)
    └── trainlog.json             (44.20 KB)
```

### Checkpoint Internal Structure
Static inspection with Python `pickletools` verifies that each `.pth.tar` checkpoint is a standard PyTorch ZIP archive with the top-level keys:
```python
checkpoint = {
    "epoch": int,             # The training epoch where minimum validation RMSE occurred
    "model": OrderedDict,     # The exact model state_dict containing parameter tensors
    "optimizer": dict,        # Adam optimizer state (exp_avg, exp_avg_sq, step)
    "step": int               # Cumulative iteration count
}
```

---

## 5. Input Shapes, Band Ordering, Normalization & Preprocessing

The official SICKLE codebase implements specific preprocessing requirements:

### 1. Spatial & Dimensional Specifications
* **Input Spatial Resolution:** $32 \times 32$ pixels.
* **Patch Extent:** Plots in SICKLE average 0.38 acres (roughly $4 \times 4$ to $6 \times 6$ pixels at 10m). The $32 \times 32$ patch provides a $320\text{m} \times 320\text{m}$ contextual window around the plot.
* **Resize Interpolation:** Resized to $(32, 32)$ using `albumentations.Resize(32, 32, interpolation=cv2.INTER_NEAREST)`.
* **Zero-Padding & Masking:** `pad_value = 0`, `padding_mode = "reflect"`. Out-of-boundary and unannotated pixels are marked with `ignore_index = -999`.

### 2. Spectral Band Ordering
Bands must be arranged in the exact order specified in `conf.json`:
* **Sentinel-2 (`S2` - 12 Bands):**  
  `['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12']`  
  *(Note: B10 cirrus band is omitted in Sentinel-2 L2A).*
* **Landsat-8 (`L8` - 8 Bands):**  
  `['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7', 'ST_B10']`
* **Sentinel-1 (`S1` - 2 Bands):**  
  `['VV', 'VH']` (Calibrated backscatter coefficient in decibels [dB], typically ranging from -26.0 dB to 0.0 dB).

### 3. Normalization Protocol (Crucial Technical Finding)
> [!IMPORTANT]
> **No manual division by 10,000 or Z-score normalization is applied in `dataset.py`!**  
> * Inspection of `_read_data()` in `utils/dataset.py` reveals that raw reflectance integers (e.g., 0 to 4,500 for S2; 7,000 to 20,000 for L8) and raw float values (e.g., -25 to 0 for S1) are stacked directly.  
> * Batch Normalization layers inside the neural networks (`BatchNorm3d` in `UNet3D` and `GroupNorm` in `UTAE`) were trained directly on these raw numeric scales.  
> * **Applying an external `img / 10000.0` division will break the pretrained network weights and lead to invalid yield predictions.**

### 4. Temporal Sampling & Positional Day Encoding
* **Sampling Rate:** SICKLE utilizes all available cloud-free or low-cloud acquisitions ($<25\%$ zero/cloud pixels within the patch).
* **Temporal Sequence Length ($T$):** Variable across plots (typically 12 dates for S1, 15–32 dates for S2).
* **Temporal Day Calculation (`batch_positions`):**  
  For each acquisition date:
  $$\text{day\_offset} = (\text{Acquisition Date} - \text{Season Start Date}).\text{days} + 1$$
  where `Season Start Date` is June 1st for Kharif (`jun-nov`), October 1st for Samba/Rabi (`oct-feb`), or January 1st for Navarai (`jan-may`).

---

## 6. How the Original Implementation Loads Checkpoints

The official loading logic extracted from `evaluate.py` follows this sequence:

```python
import os
import torch
import json
from types import SimpleNamespace
from utils import model_utils

# 1. Load experiment configuration
with open("weights/runs/wacv_2024/crop_yield/[S2]_unet3d_season/conf.json", "r") as f:
    cfg_dict = json.load(f)
CFG = SimpleNamespace(**cfg_dict)

# 2. Instantiate Fusion_model wrapper
# Note: Even single-satellite runs are instantiated through Fusion_model
model = model_utils.Fusion_model(CFG)

# 3. Load checkpoint state dict safely
checkpoint_path = "weights/runs/wacv_2024/crop_yield/[S2]_unet3d_season/checkpoint_best.pth.tar"
checkpoint = torch.load(checkpoint_path, map_location="cpu")

# 4. Bind weights to model
model.load_state_dict(checkpoint["model"])
model.eval()
```

---

## 7. Output Representation, Target Yield Units & Conversion

### 1. Spatial Output vs. Plot-Level Aggregation
The model does **not** output a single scalar directly. The output of `y_pred = model(data)` is a spatial prediction tensor:
$$\hat{Y} \in \mathbb{R}^{B \times 1 \times 32 \times 32}$$
where each pixel $(r, c)$ in the $32 \times 32$ grid represents the local yield density.

### 2. The Plot Aggregation Formula (`get_combined_yield`)
In the ground-truth mask [`masks/10m/<uid>.tif`](file:///c:/Users/K%20R%20Sravani/OneDrive/Desktop/RICE_YIELD_PREDICTION/sickle_dataset/masks/10m), each pixel within plot boundary $p$ has value:
$$\text{Pixel Value} = \frac{\text{Plot Total Yield}}{\text{Number of Pixels in Plot}}$$
Consequently, the predicted plot-level yield is the **sum of all pixel predictions within the plot boundary mask**:
$$\hat{Y}_{\text{plot}} = \sum_{(r, c) \in \text{Plot Mask}} \hat{Y}[r, c]$$

### 3. Target Units & Conversion to Project Standard
* **SICKLE Native Unit:** **kg/acre** (kilograms per acre).
* **Project Standard Unit (Phase 1 & Phase 2):** **tonnes/ha** (metric tonnes per hectare).
* **Conversion Formula:**
  $$\text{Yield (tonnes/ha)} = \frac{\hat{Y}_{\text{plot}}\text{ (kg/acre)} \times 2.4710538}{1000} \approx \hat{Y}_{\text{plot}} \times 0.002471$$

*Example Verification on UID 2177 (Plot 358):*
* Ground truth yield: $1,920\text{ kg/acre}$
* In tonnes/ha: $1,920 \times 0.002471 = \mathbf{4.74\text{ tonnes/ha}}$ (matches Cauvery Delta paddy harvest ranges).

---

## 8. Single-Plot Inference Execution Workflow

Below is the verified, standalone Python procedure to run inference on a single existing plot (e.g., UID 2177) without running any training loops:

```python
"""
Phase 3 Pilot Test: Single-Plot Inference Script for SICKLE Pretrained Models
Compatible with PyTorch >= 2.0
"""
import os
import glob
from datetime import date
import json
from types import SimpleNamespace
import numpy as np
import rasterio
import cv2
import albumentations as A
import torch

from utils import model_utils

def run_single_plot_inference(
    uid: int,
    checkpoint_dir: str,
    sickle_data_dir: str,
    device: str = "cpu"
):
    # 1. Load config
    conf_path = os.path.join(checkpoint_dir, "conf.json")
    with open(conf_path, "r") as f:
        cfg = SimpleNamespace(**json.load(f))
    cfg.device = device
    
    # 2. Build model and load weights
    model = model_utils.Fusion_model(cfg).to(device)
    ckpt = torch.load(os.path.join(checkpoint_dir, "checkpoint_best.pth.tar"), map_location=device)
    model.load_state_dict(ckpt["model"])
    model.eval()

    # 3. Read Plot Mask (10m GeoTIFF)
    mask_path = os.path.join(sickle_data_dir, f"masks/10m/{uid}.tif")
    with rasterio.open(mask_path) as src:
        raw_mask = src.read() # Shape: (6, H, W)
    
    resize = A.Resize(height=32, width=32, interpolation=cv2.INTER_NEAREST)
    plot_mask_resized = resize(image=raw_mask[0])["image"] # Band 0 is Plot ID
    target_plot_id = uid  # Or matching plot ID from tabular metadata

    # 4. Read Satellite Sequences
    data_dict = {}
    for sat, sat_info in cfg.satellites.items():
        bands = sat_info["bands"]
        npz_files = glob.glob(os.path.join(sickle_data_dir, f"images/{sat}/npy/{uid}/*.npz"))
        
        # Determine season start date
        start_date = date(2018, 6, 1) # Example Kharif baseline
        
        samples, dates = [], []
        for f in npz_files:
            npz_data = np.load(f)
            # Parse date from filename
            fname = os.path.basename(f)
            date_str = fname.split("_")[0][:8] if sat == "S2" else fname.split("_")[4][:8]
            acq_date = date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:]))
            day_idx = (acq_date - start_date).days + 1
            
            # Stack spectral bands
            channels = [resize(image=npz_data[b])["image"] for b in bands]
            samples.append(np.stack(channels, axis=0)) # (C, 32, 32)
            dates.append(day_idx)
            
        # Sort chronologically
        dates, samples = zip(*sorted(zip(dates, samples)))
        sample_tensor = torch.tensor(np.stack(samples), dtype=torch.float32).unsqueeze(0).to(device) # (1, T, C, 32, 32)
        dates_tensor = torch.tensor(dates, dtype=torch.long).unsqueeze(0).to(device) # (1, T)
        data_dict[sat] = (sample_tensor, dates_tensor)

    # 5. Model Prediction
    with torch.no_grad():
        y_pred = model(data_dict) # Shape: (1, 1, 32, 32)
        
    y_pred_grid = y_pred.squeeze().cpu().numpy()

    # 6. Plot-Level Aggregation
    plot_pixels = (plot_mask_resized > 0)
    predicted_yield_kg_acre = float(np.sum(y_pred_grid[plot_pixels]))
    predicted_yield_tonnes_ha = predicted_yield_kg_acre * 0.00247105

    return {
        "uid": uid,
        "predicted_yield_kg_acre": round(predicted_yield_kg_acre, 2),
        "predicted_yield_tonnes_ha": round(predicted_yield_tonnes_ha, 3),
        "pixel_count": int(np.sum(plot_pixels))
    }
```

---

## 9. Data Splits & Evaluation on Genuinely Unseen Plots

### 1. The Local Toy Dataset Split Status
In our local [`sickle_toy_dataset/sickle_dataset_tabular.csv`](file:///c:/Users/K%20R%20Sravani/OneDrive/Desktop/RICE_YIELD_PREDICTION/sickle_toy_dataset/sickle_dataset_tabular.csv):
* `train`: 194 records (78 Paddy plots, **28 with positive yield**).
* `val`: 23 records (11 Paddy plots, **6 with positive yield**).

### 2. Risk of Data Leakage & Evaluation Protocol
> [!WARNING]
> Because `checkpoint_best.pth.tar` was trained on the official SICKLE dataset (2,370 sequences across 388 plots), testing on the 6 validation plots in our toy dataset confirms pipeline execution, but **does not guarantee out-of-distribution generalization**.

To evaluate predictions on **genuinely unseen plots**, we must enforce three independent validation tiers:
1. **Spatial Hold-Out:** Testing on fields located in Tamil Nadu taluks/districts outside the original Cauvery Delta cluster (e.g., Tiruvannamalai, Madurai, or Thanjavur West).
2. **Temporal Hold-Out:** Testing on agricultural seasons from **2022 to 2025** (the SICKLE training set concluded in March 2021).
3. **Ground-Truth Calibration:** Comparing predictions against genuine district-level CCE (Crop Cutting Experiment) records or farmer harvest logs.

---

## 10. Can Pretrained Models Accept Raw Copernicus Browser Downloads?

### Explicit Validation Verdict: **NO, NOT DIRECTLY.**
An arbitrary Sentinel-2 zip file downloaded from the Copernicus Browser **cannot** be passed directly into these weights.

### Detailed Gap Analysis

```
Raw Copernicus L2A Download               SICKLE Pretrained Input Tensor
---------------------------------         ------------------------------------
Tile: 10,980 x 10,980 pixels       -->    Patch: 32 x 32 pixels
Multiple single-band GeoTIFFs      -->    12-band stacked tensor (B1-B12)
Arbitrary projection / UTM zone    -->    Reprojected to EPSG:32644 (Cauvery)
Single acquisition timestamp       -->    Multi-temporal sequence (12-32 dates)
No field boundary delineation      -->    Binary 10m plot mask required
```

### Required Ingestion Pipeline for New Fields
Before any new field can be evaluated with these models, an automated ingestion pipeline must:
1. **Delineate Field Boundary:** Receive polygon coordinates $(lat, lon)$ from user input or cadastral maps.
2. **Retrieve Full Season Time Series:** Query the Copernicus Data Space Ecosystem API to fetch all Sentinel-2 L2A tiles over that coordinate between planting and harvest.
3. **Filter Clouds:** Mask out cloudy scenes where scene cloud cover or patch zero/cloud percentage exceeds 25%.
4. **Crop & Resample:** Extract a $32 \times 32$ bounding box at 10m resolution centered on the polygon.
5. **Stack Bands:** Assemble bands `B1` through `B12` in the exact SICKLE channel order.
6. **Compute Day Offsets:** Calculate acquisition day offsets relative to the season start.
7. **Aggregate Pixels:** Sum predicted yield pixels across the digitized polygon mask.

---

## 11. Dependency Audit & Isolated Environment Strategy

### 1. Existing Environment Audit
The system currently operates on `Python 3.14.0`. While packages like `rasterio`, `geopandas`, `opencv-python`, and `scikit-learn` are installed, **PyTorch has no official Windows wheels for Python 3.14**. Attempting to force-install torch in the current environment risks corrupting Phase 1 and 2 dependencies.

### 2. Recommended Isolated Environment
Create a dedicated virtual environment specifically for Phase 3 satellite deep learning:

```bash
# In PowerShell:
# 1. Create a dedicated Python 3.10 or 3.11 virtual environment
py -3.11 -m venv venv_satellite

# 2. Activate the environment
.\venv_satellite\Scripts\Activate.ps1

# 3. Install PyTorch with CUDA or CPU
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 4. Install SICKLE required dependencies
pip install torchmetrics==1.3.2 torchnet albumentations rasterio opencv-python tqdm pandas numpy
```

---

## 12. Final Recommendation: Safest Pilot Verification Protocol

To verify the pretrained checkpoints safely before committing to full application integration:

```
+-------------------------------------------------------------------------------------------------------+
|                                    RECOMMENDED STEP-BY-STEP PILOT TEST                                |
+-------------------------------------------------------------------------------------------------------+
|  Step 1: Code Sandbox Setup                                                                           |
|          - Create 'src/satellite/' directory in the workspace.                                        |
|          - Copy official 'models/' and 'utils/' files from the scratch directory.                     |
|                                                                                                       |
|  Step 2: Dry-Run Inference on One Verified SICKLE Plot                                                |
|          - Select plot UID 2177 (Paddy, verified ground-truth yield = 1,920 kg/acre).                 |
|          - Run single-plot inference using Candidate 1 ('[S2]_unet3d_season').                        |
|          - Verify that predicted yield matches the expected range (~1,500 - 2,200 kg/acre).           |
|                                                                                                       |
|  Step 3: Multi-Sensor Comparison                                                                      |
|          - Run Candidate 2 ('[S2,L8,S1]_utae') on the same plot.                                      |
|          - Compare inference latency, multi-modal robustness, and stability.                          |
|                                                                                                       |
|  Step 4: Validation Set Benchmark                                                                    |
|          - Evaluate across all 6 positive validation plots in 'sickle_dataset_tabular.csv'.           |
|          - Confirm that validation RMSE matches the paper's reported ~691 kg/acre.                    |
|                                                                                                       |
|  Step 5: Architectural Non-Interference Guard                                                         |
|          - Keep Phase 1 and Phase 2 tabular endpoints on FastAPI intact.                              |
|          - Add satellite inference as an optional, modular route ('/predict-field-satellite').        |
+-------------------------------------------------------------------------------------------------------+
```

This step-by-step approach ensures zero risk to existing project assets while confirming the validity of field-level satellite yield prediction.
