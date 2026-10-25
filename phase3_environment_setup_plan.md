# SICKLE Phase 3 Environment Setup Plan

**Project:** Satellite-Based Rice Yield Prediction (Phase 3)  
**Target Architecture:** `[S2]_unet3d_season` (WACV 2024 SICKLE Model)  
**Date:** October 12, 2026  
**Status:** STEP 1 complete. Python 3.11 is not currently installed; waiting for user permission to install.

---

## 1. Python 3.11 Availability Check (Step 1)

As instructed, the system Python launcher was queried to inspect all registered Python runtimes:

```powershell
py -0p
```

**Output:**
```text
 -V:3.14 *        C:\Users\K R Sravani\AppData\Local\Programs\Python\Python314\python.exe
```

A direct check for Python 3.11 was also performed:
```powershell
py -3.11 --version
```

**Output:**
```text
No suitable Python runtime found
```

### Result:
- **Python 3.11 is NOT installed** on this machine. Only Python 3.14 is currently present.
- **Safety Directive Enforced:** Per prompt instructions (*"If Python 3.11 is unavailable, STOP and report that it must be installed. Do not install Python without permission."*), no automated runtime installations were triggered.
- **Identified Installation Package:** Windows Package Manager (`winget`) has the official Python 3.11 release available:
  - Package ID: `Python.Python.3.11`
  - Version: `3.11.9`
  - Source: `winget`

---

## 2. Status of Isolated Virtual Environment (Step 2)

- **Target Directory:** `venv_phase3_satellite`
- **Creation Status:** **Deferred.**  
  Because `py -3.11` is not yet available, `py -3.11 -m venv venv_phase3_satellite` cannot execute until Python 3.11 is installed.
- **Existing Environment Check:** `Test-Path "venv_phase3_satellite"` returned `False` (no preexisting environment was found or overwritten).

---

## 3. Required Dependencies & Compatible Versions (Step 3)

Inspection of the official SICKLE repository ([`scratch/sickle_repo/requirements.txt`](file:///c:/Users/K%20R%20Sravani/.gemini/antigravity/brain/d936d2d0-78ff-4d6d-8b19-d619bafb239b/scratch/sickle_repo/requirements.txt)), architecture definitions ([`models/pastis_unet3d.py`](file:///c:/Users/K%20R%20Sravani/.gemini/antigravity/brain/d936d2d0-78ff-4d6d-8b19-d619bafb239b/scratch/sickle_repo/models/pastis_unet3d.py)), and checkpoint configuration ([`conf.json`](file:///c:/Users/K%20R%20Sravani/OneDrive/Desktop/RICE_YIELD_PREDICTION/weights/runs/wacv_2024/crop_yield/[S2]_unet3d_season/conf.json)) yielded the following dependency matrix:

| Package | SICKLE Benchmark Version | Recommended Compatible Version (Python 3.11) | Purpose / Role in Phase 3 |
| :--- | :--- | :--- | :--- |
| **`torch`** | `~=1.13.0` | `2.2.2+cpu` or `2.3.1+cpu` | Neural network execution and weight deserialization |
| **`torchvision`** | `~=0.14.0` | `0.17.2+cpu` or `0.18.1+cpu` | Paired image transformations |
| **`torchmetrics`** | `~=0.11.0` | `0.11.4` | Metric calculation (`RMSELoss`, `MAE`, `MAPE`) |
| **`torchnet`** | `~=0.0.4` | `0.0.4` | Evaluation loss meter (`AverageValueMeter`) |
| **`albumentations`** | `~=1.3.0` | `1.3.1` | Multi-spectral image resizing to $32 \times 32$ |
| **`rasterio`** | `~=1.3.4` | `>=1.3.4, <1.5.0` | Reading 6-band GeoTIFF mask files |
| **`numpy`** | `~=1.23.0` | `>=1.24.0, <2.0.0` | Array manipulation (pinned `<2.0.0` to preserve C-ABI) |
| **`pandas`** | `>=1.5.0` | `>=1.5.0, <2.2.0` | Reading `sickle_dataset_tabular.csv` metadata |
| **`tqdm`** | `~=4.64.1` | `>=4.64.1` | Progress bar tracking |
| **`opencv-python`** | `~=4.5.5` | `>=4.6.0` | Fast nearest-neighbor spatial interpolation |

### CPU Inference Support
- **Full CPU Compatibility Verified:**
  - Neither `pastis_unet3d.py` nor `model_utils.py` contains hardcoded CUDA function calls or GPU-only kernels.
  - SICKLE uses standard PyTorch 3D convolutional modules (`nn.Conv3d`, `nn.ConvTranspose3d`, `nn.GroupNorm`), which run natively on CPU.
  - The spatial tensor dimension for one SICKLE plot is compact: $1 \times 12 \times T_{\text{season}} \times 32 \times 32$ (approx 1–2 MB in memory).
  - Forward inference on a modern CPU will execute in **under 1 second per plot**. GPU/CUDA acceleration is not required for evaluation.

---

## 4. Proposed Installation Commands (Once Python 3.11 is Authorized)

Once the user approves installing Python 3.11, the end-to-end setup will be executed cleanly using the following non-destructive sequence:

### Command Sequence:

```powershell
# 1. Install official Python 3.11 via Windows Package Manager
winget install --id Python.Python.3.11 -e --source winget --accept-source-agreements --accept-package-agreements

# 2. Create isolated virtual environment from project root
py -3.11 -m venv venv_phase3_satellite

# 3. Upgrade pip within the virtual environment
.\venv_phase3_satellite\Scripts\python.exe -m pip install --upgrade pip

# 4. Install PyTorch CPU-only wheels (lightweight, ~180 MB instead of ~2.5 GB CUDA bundle)
.\venv_phase3_satellite\Scripts\pip.exe install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 5. Install exact supporting dependencies with NumPy 1.x ABI pin
.\venv_phase3_satellite\Scripts\pip.exe install "numpy<2.0.0" "torchmetrics~=0.11.0" torchnet albumentations~=1.3.0 rasterio opencv-python pandas tqdm
```

---

## 5. Potential Compatibility Risks and Mitigation

1. **NumPy 2.0 ABI Conflict:**  
   *Risk:* NumPy released version 2.0 with breaking C-API changes. Packages compiled against older NumPy headers (like `rasterio` or `torchvision`) can crash with `_ARRAY_API` attribute errors.  
   *Mitigation:* Explicitly constrain `numpy<2.0.0` in the virtual environment.
2. **Global Environment Isolation:**  
   *Risk:* Modifying Phase 1 or Phase 2 dependencies or global site-packages.  
   *Mitigation:* All packages will reside strictly within `venv_phase3_satellite/Lib/site-packages/`. No changes will touch system Python 3.14, Phase 1, or Phase 2.
3. **PowerShell Script Execution Policy:**  
   *Risk:* Direct execution of `Activate.ps1` may be restricted by Windows execution policies (`Restricted`).  
   *Mitigation:* Use direct binary invocations (`.\venv_phase3_satellite\Scripts\python.exe`) or invoke `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` if needed during activation.

---

## Summary & Next Step

- **Python 3.11 is required and currently missing.**
- **Awaiting User Permission:** Please confirm if you would like me to proceed with installing Python 3.11 via `winget` and creating `venv_phase3_satellite`.
