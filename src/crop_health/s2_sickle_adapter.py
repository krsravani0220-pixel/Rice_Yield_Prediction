"""
Sentinel-2 to SICKLE Preprocessing and Inference Adapter
=========================================================
Connects Copernicus Sentinel-2 Level-2A satellite imagery to the pretrained
SICKLE [S2]_unet3d rice classification model.

Project: Spatio-Temporal Rice Yield Prediction Using LSTM
Target Region: Tamil Nadu (30 Districts)

Key Capabilities:
1. Automated Sentinel-2 SAFE product discovery and band indexing (12 required bands + SCL).
2. Memory-efficient 32x32 windowed spatial patch extraction across multi-resolution bands (10m, 20m, 60m).
3. Bilinear spatial alignment to a common 10m UTM coordinate grid.
4. Cloud, shadow, and invalid pixel masking via the Scene Classification Layer (SCL) with zero-padding (pad_value=0).
5. Chronological multi-temporal sequence collation and temporal sequence validation.
6. Direct inference using the pretrained SICKLE UNet3D checkpoint without retraining.
7. Paddy probability mapping and binary rice classification output generation.
"""

import os
import re
import glob
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Generator, Any

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.windows import Window, bounds as window_bounds, from_bounds
import torch
import torch.nn as nn


# Canonical 12-band sequence required by SICKLE UNet3D checkpoint
SICKLE_S2_BANDS = [
    'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B9', 'B11', 'B12'
]

# File search patterns for each spectral band within L2A SAFE directory
BAND_FILE_PATTERNS = {
    'B1': ['*_B01_20m.jp2', '*_B01_60m.jp2', '*_B01.jp2'],
    'B2': ['*_B02_10m.jp2', '*_B02_20m.jp2', '*_B02.jp2'],
    'B3': ['*_B03_10m.jp2', '*_B03_20m.jp2', '*_B03.jp2'],
    'B4': ['*_B04_10m.jp2', '*_B04_20m.jp2', '*_B04.jp2'],
    'B5': ['*_B05_20m.jp2', '*_B05_60m.jp2', '*_B05.jp2'],
    'B6': ['*_B06_20m.jp2', '*_B06_60m.jp2', '*_B06.jp2'],
    'B7': ['*_B07_20m.jp2', '*_B07_60m.jp2', '*_B07.jp2'],
    'B8': ['*_B08_10m.jp2', '*_B08.jp2'],
    'B8A': ['*_B8A_20m.jp2', '*_B8A_60m.jp2', '*_B8A.jp2'],
    'B9': ['*_B09_60m.jp2', '*_B09.jp2'],
    'B11': ['*_B11_20m.jp2', '*_B11_60m.jp2', '*_B11.jp2'],
    'B12': ['*_B12_20m.jp2', '*_B12_60m.jp2', '*_B12.jp2'],
}

SCL_FILE_PATTERNS = ['*_SCL_20m.jp2', '*_SCL_60m.jp2', '*_SCL.jp2']

# SCL classes considered invalid (cloud, shadow, cirrus, no data, saturated)
# 0: NO_DATA, 1: SATURATED/DEFECTIVE, 2: CAST_SHADOWS, 3: CLOUD_SHADOWS,
# 8: CLOUD_MEDIUM_PROB, 9: CLOUD_HIGH_PROB, 10: THIN_CIRRUS, 11: SNOW
INVALID_SCL_CLASSES = {0, 1, 2, 3, 8, 9, 10, 11}


class InsufficientTemporalObservationsError(ValueError):
    """Raised when the temporal sequence length T is insufficient for 3D CNN inference."""
    pass


# -------------------------------------------------------------------------
# 1. SICKLE UNet3D Model Architecture Definition
# -------------------------------------------------------------------------

def conv_block(in_dim: int, middle_dim: int, out_dim: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Conv3d(in_dim, middle_dim, kernel_size=3, stride=1, padding=1),
        nn.BatchNorm3d(middle_dim),
        nn.LeakyReLU(inplace=True),
        nn.Conv3d(middle_dim, out_dim, kernel_size=3, stride=1, padding=1),
        nn.BatchNorm3d(out_dim),
        nn.LeakyReLU(inplace=True),
    )


def center_in(in_dim: int, out_dim: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Conv3d(in_dim, out_dim, kernel_size=3, stride=1, padding=1),
        nn.BatchNorm3d(out_dim),
        nn.LeakyReLU(inplace=True)
    )


def center_out(in_dim: int, out_dim: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Conv3d(in_dim, in_dim, kernel_size=3, stride=1, padding=1),
        nn.BatchNorm3d(in_dim),
        nn.LeakyReLU(inplace=True),
        nn.ConvTranspose3d(in_dim, out_dim, kernel_size=3, stride=2, padding=1, output_padding=1)
    )


def up_conv_block(in_dim: int, out_dim: int) -> nn.Sequential:
    return nn.Sequential(
        nn.ConvTranspose3d(in_dim, out_dim, kernel_size=3, stride=2, padding=1, output_padding=1),
        nn.BatchNorm3d(out_dim),
        nn.LeakyReLU(inplace=True),
    )


class UNet3D(nn.Module):
    """
    Spatio-Temporal 3D U-Net feature extractor for multi-temporal optical imagery.
    Input: (B, C=12, T, H=32, W=32)
    Output: (B, 16, H=32, W=32) feature representations.
    """
    def __init__(self, in_channel: int = 12, n_classes: int = 16, feats: int = 8, pad_value: float = 0.0):
        super().__init__()
        self.pad_value = pad_value
        self.en3 = conv_block(in_channel, feats * 4, feats * 4)
        self.pool_3 = nn.MaxPool3d(kernel_size=2, stride=2, padding=0)
        self.en4 = conv_block(feats * 4, feats * 8, feats * 8)
        self.pool_4 = nn.MaxPool3d(kernel_size=2, stride=2, padding=0)
        self.center_in = center_in(feats * 8, feats * 16)
        self.center_out = center_out(feats * 16, feats * 8)
        self.dc4 = conv_block(feats * 16, feats * 8, feats * 8)
        self.trans3 = up_conv_block(feats * 8, feats * 4)
        self.dc3 = conv_block(feats * 8, feats * 4, feats * 2)
        self.final = nn.Conv3d(feats * 2, n_classes, kernel_size=3, stride=1, padding=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Input x: (B, T, C, H, W) -> permute to (B, C, T, H, W)
        out = x.permute(0, 2, 1, 3, 4)
        en3 = self.en3(out)
        pool_3 = self.pool_3(en3)
        en4 = self.en4(pool_3)
        pool_4 = self.pool_4(en4)
        c_in = self.center_in(pool_4)
        c_out = self.center_out(c_in)
        concat4 = torch.cat([c_out, en4[:, :, :c_out.shape[2], :, :]], dim=1)
        dc4 = self.dc4(concat4)
        trans3 = self.trans3(dc4)
        concat3 = torch.cat([trans3, en3[:, :, :trans3.shape[2], :, :]], dim=1)
        dc3 = self.dc3(concat3)
        final = self.final(dc3)
        final = final.permute(0, 1, 3, 4, 2)
        out = final.mean(dim=-1)  # Temporal average pooling -> (B, 16, H, W)
        return out


class S2CropTypeModel(nn.Module):
    """
    Complete SICKLE Rice / Crop Classification Model.
    Wraps UNet3D base model with conv_final binary classification head.
    Classes: Channel 0 = Paddy Rice, Channel 1 = Non-Paddy.
    """
    def __init__(self, in_channel: int = 12, n_classes: int = 2):
        super().__init__()
        self.model = UNet3D(in_channel=in_channel, n_classes=16)
        self.models = nn.ModuleDict({'S2': UNet3D(in_channel=in_channel, n_classes=16)})
        self.conv_final = nn.Conv2d(16, n_classes, kernel_size=3, stride=1, padding=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.models['S2'](x)
        logits = self.conv_final(feat)
        return logits


def normalize_path(path: str) -> str:
    """
    Normalizes path for cross-platform compatibility, adding the Windows extended
    path prefix ('\\\\?\\') if running on Windows and path exceeds 240 chars.
    """
    if not path:
        return path
    abs_path = os.path.abspath(path)
    if os.name == 'nt' and not abs_path.startswith('\\\\?\\'):
        if len(abs_path) >= 240:
            return '\\\\?\\' + abs_path
    return abs_path


# -------------------------------------------------------------------------
# 2. Sentinel-2 L2A SAFE Product Parser
# -------------------------------------------------------------------------

class Sentinel2SAFEProduct:
    """
    Parses and indexes a local Sentinel-2 Level-2A .SAFE product.
    Discovers all 12 spectral bands and the Scene Classification Layer (SCL).
    """
    def __init__(self, safe_path: str):
        self.safe_path = normalize_path(safe_path)
        if not os.path.isdir(self.safe_path):
            raise FileNotFoundError(f"Sentinel-2 SAFE directory not found: {self.safe_path}")
        
        self.folder_name = os.path.basename(os.path.abspath(safe_path))
        self.acquisition_date = self._parse_acquisition_date()
        self.band_paths = self._discover_spectral_bands()
        self.scl_path = self._discover_scl()
        
        # Determine reference 10m profile (using B04 Red or B02 Blue)
        self.ref_band = 'B4' if 'B4' in self.band_paths else 'B2'
        if self.ref_band not in self.band_paths:
            raise FileNotFoundError("Could not find reference 10m band (B04 or B02) in SAFE product.")
            
        with rasterio.open(self.band_paths[self.ref_band]) as src:
            self.crs = src.crs
            self.transform = src.transform
            self.width = src.width
            self.height = src.height
            self.bounds = src.bounds

    def _parse_acquisition_date(self) -> datetime:
        """Extract acquisition timestamp from SAFE folder name (e.g., S2B_MSIL2A_20200403T050649_...)."""
        match = re.search(r'_(\d{8}T\d{6})_', self.folder_name)
        if match:
            return datetime.strptime(match.group(1), "%Y%m%dT%H%M%S")
        match_date = re.search(r'_(\d{8})T', self.folder_name)
        if match_date:
            return datetime.strptime(match_date.group(1), "%Y%m%d")
        return datetime.fromtimestamp(os.path.getmtime(self.safe_path))

    def _discover_spectral_bands(self) -> Dict[str, str]:
        """Discover paths for all 12 required SICKLE spectral bands."""
        discovered = {}
        for band_name, patterns in BAND_FILE_PATTERNS.items():
            for pat in patterns:
                matches = glob.glob(os.path.join(self.safe_path, '**', pat), recursive=True)
                if matches:
                    discovered[band_name] = normalize_path(matches[0])
                    break
        return discovered

    def _discover_scl(self) -> Optional[str]:
        """Discover path for the Scene Classification Layer (SCL)."""
        for pat in SCL_FILE_PATTERNS:
            matches = glob.glob(os.path.join(self.safe_path, '**', pat), recursive=True)
            if matches:
                return normalize_path(matches[0])
        return None

    def check_completeness(self) -> Tuple[bool, List[str]]:
        """Verify whether all 12 bands and SCL are present."""
        missing = [b for b in SICKLE_S2_BANDS if b not in self.band_paths]
        if not self.scl_path:
            missing.append('SCL')
        return len(missing) == 0, missing

    def get_summary(self) -> Dict[str, Any]:
        complete, missing = self.check_completeness()
        return {
            'safe_path': self.safe_path,
            'folder_name': self.folder_name,
            'acquisition_date': self.acquisition_date.strftime("%Y-%m-%d %H:%M:%S"),
            'is_complete': complete,
            'missing_bands': missing,
            'grid_shape': (self.height, self.width),
            'crs': str(self.crs),
            'bounds': {
                'left': self.bounds.left,
                'bottom': self.bounds.bottom,
                'right': self.bounds.right,
                'top': self.bounds.top,
            }
        }


# -------------------------------------------------------------------------
# 3. Patch Extractor & Spatial-Spectral Grid Normalizer
# -------------------------------------------------------------------------

class S2PatchExtractor:
    """
    Extracts memory-efficient 32x32 pixel patches from Sentinel-2 SAFE products.
    Resamples all 12 bands to a unified 10m grid and applies SCL cloud/shadow masking.
    """
    def __init__(self, patch_size: int = 32):
        self.patch_size = patch_size

    def extract_patch(
        self,
        product: Sentinel2SAFEProduct,
        row_offset: int,
        col_offset: int,
        apply_mask: bool = True
    ) -> Dict[str, Any]:
        """
        Extracts a single 32x32 patch at 10m resolution starting at (row_offset, col_offset).
        
        Returns:
            Dict containing:
                - 'data': np.ndarray of shape (12, 32, 32), dtype float32 (reflectance DN 0..10000)
                - 'scl': np.ndarray of shape (32, 32), dtype uint8
                - 'invalid_mask': np.ndarray of shape (32, 32), dtype bool (True where masked)
                - 'bounds': tuple of (minx, miny, maxx, maxy)
                - 'date': datetime acquisition date
                - 'row_offset': int
                - 'col_offset': int
        """
        ref_window = Window(col_offset, row_offset, self.patch_size, self.patch_size)
        patch_bounds = window_bounds(ref_window, product.transform)

        patch_channels = np.zeros((12, self.patch_size, self.patch_size), dtype=np.float32)

        # Read all 12 spectral bands aligned to patch_bounds
        for idx, band_name in enumerate(SICKLE_S2_BANDS):
            band_path = product.band_paths.get(band_name)
            if not band_path or not os.path.exists(band_path):
                raise FileNotFoundError(f"Required band {band_name} missing for product {product.folder_name}")

            with rasterio.open(band_path) as band_src:
                band_win = from_bounds(*patch_bounds, band_src.transform)
                # Resample non-10m bands (20m, 60m) to (32, 32) via bilinear interpolation
                band_arr = band_src.read(
                    1,
                    window=band_win,
                    out_shape=(self.patch_size, self.patch_size),
                    resampling=Resampling.bilinear
                ).astype(np.float32)
                patch_channels[idx] = band_arr

        # Read SCL layer aligned to patch_bounds
        if product.scl_path and os.path.exists(product.scl_path):
            with rasterio.open(product.scl_path) as scl_src:
                scl_win = from_bounds(*patch_bounds, scl_src.transform)
                scl_arr = scl_src.read(
                    1,
                    window=scl_win,
                    out_shape=(self.patch_size, self.patch_size),
                    resampling=Resampling.nearest
                ).astype(np.uint8)
        else:
            scl_arr = np.zeros((self.patch_size, self.patch_size), dtype=np.uint8)

        # Identify cloud, shadow, defective, and no-data pixels
        invalid_scl = np.isin(scl_arr, list(INVALID_SCL_CLASSES))
        zero_refl = (patch_channels <= 0).all(axis=0)
        invalid_mask = invalid_scl | zero_refl

        # SICKLE pad_value is 0.0; set invalid pixels to 0.0
        if apply_mask:
            for b_idx in range(12):
                patch_channels[b_idx, invalid_mask] = 0.0

        return {
            'data': patch_channels,
            'scl': scl_arr,
            'invalid_mask': invalid_mask,
            'bounds': patch_bounds,
            'date': product.acquisition_date,
            'row_offset': row_offset,
            'col_offset': col_offset
        }

    def generate_patch_grid(
        self,
        product: Sentinel2SAFEProduct,
        stride: int = 32,
        max_patches: Optional[int] = None
    ) -> Generator[Tuple[int, int], None, None]:
        """Yields (row_offset, col_offset) pairs spanning the full 10m scene."""
        count = 0
        for r in range(0, product.height - self.patch_size + 1, stride):
            for c in range(0, product.width - self.patch_size + 1, stride):
                yield r, c
                count += 1
                if max_patches and count >= max_patches:
                    return


# -------------------------------------------------------------------------
# 4. Multi-Temporal Sequence Collation and Validation
# -------------------------------------------------------------------------

class MultiTemporalSequenceCollator:
    """
    Collates multiple temporal observations for a given spatial patch into the
    exact tensor format expected by SICKLE UNet3D: (1, T, 12, 32, 32).
    Enforces structural and agronomic temporal constraints.
    """
    MIN_THEORETICAL_DATES = 4   # Minimum dates required for two 3D pooling operations
    MIN_AGRONOMIC_DATES = 13    # Minimum seasonal observations for reliable rice phenology

    @classmethod
    def validate_temporal_sequence(cls, num_dates: int, strict_agronomic: bool = False) -> None:
        """
        Validates whether temporal sequence length T is sufficient for UNet3D.
        Raises InsufficientTemporalObservationsError if T < MIN_THEORETICAL_DATES.
        """
        if num_dates < cls.MIN_THEORETICAL_DATES:
            msg = (
                f"Insufficient temporal observations: received T={num_dates} date(s). "
                f"SICKLE UNet3D employs two 3D pooling layers (kernel=2, stride=2) across time, "
                f"which mathematically requires at least T={cls.MIN_THEORETICAL_DATES} dates to avoid "
                f"temporal collapse (T=1 collapses to 0 after pooling). "
                f"Furthermore, rice phenological classification requires T>={cls.MIN_AGRONOMIC_DATES} "
                f"observations across the 120-150 day crop cycle (transplanting/flooding, tillering, "
                f"panicle initiation, and ripening). Single-date inference is structurally invalid "
                f"and must not be executed."
            )
            raise InsufficientTemporalObservationsError(msg)
        
        if strict_agronomic and num_dates < cls.MIN_AGRONOMIC_DATES:
            msg = (
                f"Sub-optimal seasonal coverage: received T={num_dates} dates, which satisfies "
                f"the mathematical 3D CNN requirement (T>={cls.MIN_THEORETICAL_DATES}), but falls below "
                f"the recommended SICKLE benchmark sequence length (T>={cls.MIN_AGRONOMIC_DATES}) "
                f"for distinguishing paddy rice from other crops."
            )
            raise InsufficientTemporalObservationsError(msg)

    @classmethod
    def collate_patches(
        cls,
        patches: List[Dict[str, Any]],
        strict_agronomic: bool = False
    ) -> Tuple[torch.Tensor, List[datetime]]:
        """
        Sorts temporal patches chronologically and stacks into a model input tensor.
        
        Returns:
            tensor: torch.Tensor of shape (1, T, 12, 32, 32), dtype torch.float32
            dates: List of sorted acquisition datetimes
        """
        cls.validate_temporal_sequence(len(patches), strict_agronomic=strict_agronomic)

        # Sort chronologically by date
        sorted_patches = sorted(patches, key=lambda p: p['date'])
        dates = [p['date'] for p in sorted_patches]

        # Stack into (T, 12, 32, 32)
        stacked_arrays = [p['data'] for p in sorted_patches]
        sequence_np = np.stack(stacked_arrays, axis=0)  # Shape (T, 12, 32, 32)

        tensor = torch.tensor(sequence_np, dtype=torch.float32).unsqueeze(0)  # Shape (1, T, 12, 32, 32)
        return tensor, dates


# -------------------------------------------------------------------------
# 5. SICKLE Pretrained Inference Pipeline
# -------------------------------------------------------------------------

class SICKLEInferencePipeline:
    """
    Manages pretrained SICKLE model weights, executes evaluation,
    and produces paddy-probability maps and binary classifications.
    """
    def __init__(self, checkpoint_path: str, device: str = 'cpu'):
        self.device = torch.device(device)
        self.checkpoint_path = os.path.abspath(checkpoint_path)
        if not os.path.exists(self.checkpoint_path):
            raise FileNotFoundError(f"Checkpoint file not found: {self.checkpoint_path}")

        self.model = S2CropTypeModel(in_channel=12, n_classes=2).to(self.device)
        self._load_weights()
        self.model.eval()

    def _load_weights(self) -> None:
        """Load pretrained checkpoint into model architecture without retraining."""
        ckpt = torch.load(self.checkpoint_path, map_location=self.device, weights_only=False)
        state_dict = ckpt['model'] if 'model' in ckpt else ckpt
        self.model.load_state_dict(state_dict)

    def predict_patch(
        self,
        input_tensor: torch.Tensor,
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Runs model forward pass on a multi-temporal patch tensor.
        
        Args:
            input_tensor: Tensor of shape (1, T, 12, 32, 32)
            threshold: Probability threshold for paddy classification (default: 0.5)
            
        Returns:
            Dict containing:
                - 'paddy_probability': np.ndarray of shape (32, 32), range [0.0, 1.0]
                - 'non_paddy_probability': np.ndarray of shape (32, 32), range [0.0, 1.0]
                - 'binary_mask': np.ndarray of shape (32, 32), uint8 (1 = paddy, 0 = non-paddy)
                - 'paddy_pixel_count': int
                - 'paddy_area_percentage': float
        """
        if input_tensor.dim() != 5:
            raise ValueError(f"Expected 5D input tensor (1, T, C, H, W), got {input_tensor.shape}")

        MultiTemporalSequenceCollator.validate_temporal_sequence(input_tensor.shape[1])

        tensor = input_tensor.to(self.device)
        with torch.no_grad():
            logits = self.model(tensor)  # (1, 2, 32, 32)
            probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()  # (2, 32, 32)

        paddy_prob = probs[0]       # Channel 0: Paddy Rice
        non_paddy_prob = probs[1]   # Channel 1: Non-Paddy
        binary_mask = (paddy_prob >= threshold).astype(np.uint8)

        total_pixels = paddy_prob.size
        paddy_count = int(np.sum(binary_mask))
        paddy_pct = float(paddy_count / total_pixels * 100.0)

        return {
            'paddy_probability': paddy_prob,
            'non_paddy_probability': non_paddy_prob,
            'binary_mask': binary_mask,
            'paddy_pixel_count': paddy_count,
            'paddy_area_percentage': paddy_pct
        }


# -------------------------------------------------------------------------
# 6. SICKLE Pretrained Yield Regression Model and Pipeline
# -------------------------------------------------------------------------

class S2YieldModel(nn.Module):
    """
    Complete SICKLE Rice Yield Continuous Regression Model ([S2]_unet3d_season).
    Wraps UNet3D base architecture with a 1x1 conv continuous regression head (conv_final).
    Outputs dense pixel-level yield density (kg/acre per 10m pixel).
    """
    def __init__(self, in_channel: int = 12):
        super().__init__()
        self.model = UNet3D(in_channel=in_channel, n_classes=16)
        self.models = nn.ModuleDict({'S2': UNet3D(in_channel=in_channel, n_classes=16)})
        self.conv_final = nn.Conv2d(16, 1, kernel_size=3, stride=1, padding=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.models['S2'](x)
        return self.conv_final(feat)


class SICKLEYieldInferencePipeline:
    """
    Manages pretrained SICKLE yield regression model weights ([S2]_unet3d_season),
    executes spatio-temporal inference, and aggregates plot-level yield predictions.
    """
    KG_ACRE_TO_TONNES_HA = 0.00247105

    def __init__(self, checkpoint_path: str, device: str = 'cpu'):
        self.device = torch.device(device)
        self.checkpoint_path = os.path.abspath(checkpoint_path)
        if not os.path.exists(self.checkpoint_path):
            raise FileNotFoundError(f"Checkpoint file not found: {self.checkpoint_path}")

        self.model = S2YieldModel(in_channel=12).to(self.device)
        self._load_weights()
        self.model.eval()

    def _load_weights(self) -> None:
        """Load pretrained yield regression weights into model without retraining."""
        ckpt = torch.load(self.checkpoint_path, map_location=self.device, weights_only=False)
        state_dict = ckpt['model'] if 'model' in ckpt else ckpt
        self.model.load_state_dict(state_dict)

    def predict_patch(
        self,
        input_tensor: torch.Tensor,
        plot_mask: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Runs model forward pass on multi-temporal patch tensor (1, T, 12, 32, 32).
        Returns predicted yield density grid and aggregated plot yield.
        """
        if input_tensor.dim() != 5:
            raise ValueError(f"Expected 5D input tensor (1, T, C, H, W), got {input_tensor.shape}")

        MultiTemporalSequenceCollator.validate_temporal_sequence(input_tensor.shape[1])

        tensor = input_tensor.to(self.device)
        with torch.no_grad():
            density_grid = self.model(tensor).squeeze().cpu().numpy()  # (32, 32)

        # Enforce non-negative physical yield density
        density_grid = np.clip(density_grid, 0.0, None)

        if plot_mask is not None:
            if plot_mask.shape != (32, 32):
                import cv2
                plot_mask = cv2.resize(plot_mask.astype(np.uint8), (32, 32), interpolation=cv2.INTER_NEAREST)
            mask_bool = plot_mask > 0
            plot_pixels = int(np.sum(mask_bool))
            if plot_pixels > 0:
                plot_yield_kg = float(np.sum(density_grid[mask_bool]))
                mean_density = float(np.mean(density_grid[mask_bool]))
            else:
                plot_yield_kg = float(np.sum(density_grid))
                mean_density = float(np.mean(density_grid))
        else:
            plot_pixels = density_grid.size
            plot_yield_kg = float(np.sum(density_grid))
            mean_density = float(np.mean(density_grid))

        plot_yield_tha = round(plot_yield_kg * self.KG_ACRE_TO_TONNES_HA, 3)

        return {
            'yield_density_map': density_grid,
            'mean_density_kg_per_px': round(mean_density, 2),
            'plot_pixels': plot_pixels,
            'predicted_yield_kg_acre': round(plot_yield_kg, 1),
            'predicted_yield_tonnes_ha': plot_yield_tha,
            'unit': 'tonnes/ha'
        }
