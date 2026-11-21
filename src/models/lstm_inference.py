"""
LSTM Inference Engine for Tamil Nadu Rice Yield Prediction
Integrates Multi-Year Temporal Sequences [T-2, T-1, T] with Live Copernicus Sentinel-2 Features.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False
    torch = None
    class _DummyNN:
        Module = object
    nn = _DummyNN()

import joblib

logger = logging.getLogger("LSTMInference")

# 1. PyTorch Architecture Components
class Attention(nn.Module):
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.attn = nn.Linear(hidden_dim, 1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # x: (batch, seq_len, hidden_dim)
        scores = self.attn(x)
        weights = torch.softmax(scores, dim=1)
        context = torch.sum(weights * x, dim=1)
        return context, weights


class BiLSTMAttentionYieldModel(nn.Module):
    def __init__(self, input_dim: int = 35, hidden_dim: int = 64, num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.attention = Attention(hidden_dim * 2)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)
        context, _ = self.attention(lstm_out)
        return self.fc(context).squeeze(-1)


class LSTMYieldInference:
    """
    Production inference service executing the trained Bidirectional LSTM
    with Multi-Head Temporal Attention for rice yield prediction.
    """
    def __init__(self, models_dir: Optional[str] = None):
        if models_dir is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            models_dir = os.path.join(project_root, "models")
        self.models_dir = models_dir

        self.config_path = os.path.join(models_dir, "lstm_config.json")
        self.model_path = os.path.join(models_dir, "lstm_yield_model.pt")
        self.scaler_path = os.path.join(models_dir, "lstm_scaler.joblib")
        self.imputer_path = os.path.join(models_dir, "lstm_imputer.joblib")

        self.is_ready = False
        self.config = {}
        self.model = None
        self.scaler = None
        self.imputer = None
        self.feature_names = []

        self._load_artifacts()
        self._load_historical_cache()

    def _load_artifacts(self):
        """Loads model weights, scaler, imputer and config."""
        if not (os.path.exists(self.config_path) and os.path.exists(self.model_path) and
                os.path.exists(self.scaler_path) and os.path.exists(self.imputer_path)):
            logger.warning("LSTM artifacts not fully present in %s", self.models_dir)
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.feature_names = self.config.get("features", {}).get("feature_names", [])
        arch = self.config.get("architecture", {})
        input_dim = arch.get("input_dim", 35)
        hidden_dim = arch.get("hidden_dim", 64)
        num_layers = arch.get("num_layers", 2)
        dropout = arch.get("dropout", 0.2)

        self.model = BiLSTMAttentionYieldModel(
            input_dim=input_dim,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            dropout=dropout
        )
        state_dict = torch.load(self.model_path, map_location=torch.device("cpu"))
        self.model.load_state_dict(state_dict)
        self.model.eval()

        self.scaler = joblib.load(self.scaler_path)
        self.imputer = joblib.load(self.imputer_path)
        self.is_ready = True
        logger.info("LSTM Model successfully loaded and ready for inference.")

    def _load_historical_cache(self):
        """Pre-indexes historical records for fast multi-year sequence construction."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        hist_path = os.path.join(project_root, "data/processed/rice_yield_processed.csv")
        sat_path = os.path.join(project_root, "outputs/data/satellite_yield_training_dataset.csv")

        self.history_records = {}
        self.district_climatology = {}

        if os.path.exists(hist_path):
            df_h = pd.read_csv(hist_path)
            weather_cols = self.config.get("features", {}).get("weather_features_15", [])
            soil_cols = self.config.get("features", {}).get("soil_inputs_features_7", [])
            sat_cols = self.config.get("features", {}).get("satellite_features_12", [])

            df_s = pd.read_csv(sat_path) if os.path.exists(sat_path) else None
            if df_s is not None and sat_cols:
                self.district_climatology = df_s.groupby("District")[sat_cols].mean().to_dict("index")
                sat_map = {}
                for _, r in df_s.iterrows():
                    sat_map[(r["District"], int(r["Year"]))] = {c: float(r[c]) for c in sat_cols}
            else:
                sat_map = {}

            yield_map = {}
            for _, r in df_h.iterrows():
                yield_map[(r["District"], int(r["Year"]))] = float(r["Yield"]) if not pd.isna(r["Yield"]) else np.nan

            for _, r in df_h.iterrows():
                d = r["District"]
                yr = int(r["Year"])
                y = float(r["Yield"]) if not pd.isna(r["Yield"]) else np.nan
                lag_y = yield_map.get((d, yr - 1), y if not np.isnan(y) else 3.5)

                if (d, yr) in sat_map:
                    s_vals = sat_map[(d, yr)]
                else:
                    s_vals = self.district_climatology.get(d, {c: 0.35 for c in sat_cols})

                row = {}
                for c in weather_cols + soil_cols:
                    row[c] = float(r[c]) if c in r and not pd.isna(r[c]) else np.nan
                for c in sat_cols:
                    row[c] = float(s_vals.get(c, 0.35))
                row["Yield_Lag1"] = float(lag_y)
                row["Yield"] = y
                self.history_records[(d, yr)] = row

    def build_temporal_sequence(
        self,
        district: str,
        current_year: int,
        live_satellite_indices: Dict[str, float],
        weather_override: Optional[Dict[str, float]] = None,
        soil_override: Optional[Dict[str, float]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Builds the 3-year temporal sequence [T-2, T-1, T] for a given district.
        Raises ValueError if historical sequence observations are insufficient.
        """
        from src.satellite.district_registry import get_district_profile
        prof = get_district_profile(district)
        if not prof:
            raise ValueError(f"District '{district}' not found in Tamil Nadu registry.")

        weather_cols = self.config.get("features", {}).get("weather_features_15", [])
        soil_cols = self.config.get("features", {}).get("soil_inputs_features_7", [])
        sat_cols = self.config.get("features", {}).get("satellite_features_12", [])

        # Step T-2 (e.g. 2022) and Step T-1 (e.g. 2023)
        y_t2 = current_year - 2
        y_t1 = current_year - 1

        # Fallback to closest available years if requested future year
        avail_years = [k[1] for k in self.history_records.keys() if k[0] == district]
        lookup_dist = district
        if not avail_years:
            parent = prof.get("parent_district", "Thanjavur")
            avail_years = [k[1] for k in self.history_records.keys() if k[0] == parent]
            lookup_dist = parent
            if not avail_years:
                lookup_dist = "Thanjavur"
                avail_years = [k[1] for k in self.history_records.keys() if k[0] == lookup_dist]

        max_avail = max(avail_years)
        if y_t1 > max_avail:
            # Shift anchor to latest known years for past steps
            hist_t1 = max_avail
            hist_t2 = max_avail - 1
        else:
            hist_t1 = y_t1
            hist_t2 = y_t2

        if (lookup_dist, hist_t2) not in self.history_records or (lookup_dist, hist_t1) not in self.history_records:
            # Fall back to latest two years for lookup_dist
            sorted_y = sorted(avail_years)
            if len(sorted_y) >= 2:
                hist_t2, hist_t1 = sorted_y[-2], sorted_y[-1]
            else:
                raise ValueError(
                    f"Insufficient historical sequence for {district} (mapped to {lookup_dist}). Requires verified observations."
                )

        r0 = self.history_records[(lookup_dist, hist_t2)]
        r1 = self.history_records[(lookup_dist, hist_t1)]

        # Construct Step T (current live year)
        # Weather & soil from district baseline or provided override
        r2 = {}
        # Weather
        default_weather = {
            'Kharif Temperature': 29.5, 'Kharif Rainfall': 120.0, 'Kharif Humidity': 72.0, 'Kharif Wind_Speed': 10.0, 'Kharif Soil_Moisture': 0.28,
            'Rabi Temperature': 26.0, 'Rabi Rainfall': 180.0, 'Rabi Humidity': 80.0, 'Rabi Wind_Speed': 9.0, 'Rabi Soil_Moisture': 0.32,
            'Zaid Temperature': 32.0, 'Zaid Rainfall': 40.0, 'Zaid Humidity': 65.0, 'Zaid Wind_Speed': 11.0, 'Zaid Soil_Moisture': 0.20
        }
        for wc in weather_cols:
            if weather_override and wc in weather_override:
                r2[wc] = float(weather_override[wc])
            elif wc in default_weather:
                r2[wc] = float(default_weather[wc])
            else:
                r2[wc] = float(r1.get(wc, 25.0))

        # Soil & Inputs
        for sc in soil_cols:
            if soil_override and sc in soil_override:
                r2[sc] = float(soil_override[sc])
            elif sc == "Soil_PH":
                r2[sc] = float(prof.get("soil_ph", 7.2))
            elif sc == "N":
                r2[sc] = float(prof.get("n", 280.0))
            elif sc == "P":
                r2[sc] = float(prof.get("p", 18.0))
            elif sc == "K":
                r2[sc] = float(prof.get("k", 200.0))
            elif sc == "Fertilizer":
                r2[sc] = float(prof.get("fertilizer", 160.0))
            elif sc == "Pesticide":
                r2[sc] = float(prof.get("pesticide", 2.2))
            elif sc == "Area":
                r2[sc] = float(prof.get("area", 50000.0))
            else:
                r2[sc] = float(r1.get(sc, 100.0))

        # Live Satellite Indices (NDVI, NDRE, EVI, NDWI)
        # Map live indices across seasons using district seasonal climatology proportions
        live_ndvi = float(live_satellite_indices.get("ndvi_mean", 0.38))
        live_ndre = float(live_satellite_indices.get("ndre_mean", live_ndvi * 0.72)) if live_satellite_indices.get("ndre_mean") is not None else live_ndvi * 0.72
        live_evi = float(live_satellite_indices.get("evi_mean", live_ndvi * 0.85))
        live_ndwi = float(live_satellite_indices.get("ndwi_mean", 0.05))

        for sc in sat_cols:
            if "NDVI" in sc:
                r2[sc] = live_ndvi
            elif "NDRE" in sc:
                r2[sc] = live_ndre
            elif "EVI" in sc:
                r2[sc] = live_evi
            elif "NDWI" in sc:
                r2[sc] = live_ndwi
            else:
                r2[sc] = 0.35

        # Yield lag is previous year's yield
        r2["Yield_Lag1"] = float(r1.get("Yield", 3.5))

        f0 = [r0[c] for c in self.feature_names]
        f1 = [r1[c] for c in self.feature_names]
        f2 = [r2[c] for c in self.feature_names]

        seq = np.array([f0, f1, f2], dtype=np.float32)

        meta = {
            "district": district,
            "sequence_years": [hist_t2, hist_t1, current_year],
            "feature_count": len(self.feature_names),
            "step_T_live_satellite": {
                "ndvi": live_ndvi,
                "ndre": live_ndre,
                "evi": live_evi,
                "ndwi": live_ndwi
            },
            "yield_lag_t1": r2["Yield_Lag1"]
        }
        return seq, meta

    def predict_yield_from_sequence(self, sequence: np.ndarray) -> float:
        """
        Executes inference for a 3-year sequence array of shape (3, 35) or (1, 3, 35).
        """
        if not self.is_ready:
            raise RuntimeError("LSTM Inference Engine is not initialized with valid model artifacts.")

        if sequence.ndim == 2:
            sequence = np.expand_dims(sequence, axis=0) # (1, 3, 35)

        B, T, F = sequence.shape
        flat = sequence.reshape(-1, F)
        imputed = self.imputer.transform(flat)
        scaled = self.scaler.transform(imputed).reshape(B, T, F).astype(np.float32)

        with torch.no_grad():
            tensor_in = torch.tensor(scaled, dtype=torch.float32)
            pred = self.model(tensor_in).item()

        # Sensible agronomic bounds (Tamil Nadu yield ranges 0.8 - 6.5 t/ha)
        pred = max(0.8, min(6.5, float(pred)))
        return round(pred, 2)

    def predict_district_live(
        self,
        district: str,
        live_satellite_indices: Dict[str, float],
        current_year: int = 2024
    ) -> Dict[str, Any]:
        """
        Full prediction pipeline for a district given live Copernicus satellite observations.
        """
        seq, meta = self.build_temporal_sequence(
            district=district,
            current_year=current_year,
            live_satellite_indices=live_satellite_indices
        )
        predicted_yield = self.predict_yield_from_sequence(seq)

        return {
            "district": district,
            "predicted_yield_t_ha": predicted_yield,
            "model_name": "Bidirectional LSTM with Temporal Attention + Sentinel-2 Level-2A",
            "model_type": "LSTM_Temporal_Sequence",
            "sequence_length": 3,
            "sequence_years": meta["sequence_years"],
            "features_used_count": meta["feature_count"],
            "live_indices_integrated": meta["step_T_live_satellite"],
            "yield_lag_t1": meta["yield_lag_t1"]
        }


# Singleton instance
_lstm_instance = None

def get_lstm_inference() -> LSTMYieldInference:
    global _lstm_instance
    if _lstm_instance is None or not _lstm_instance.is_ready:
        _lstm_instance = LSTMYieldInference()
    return _lstm_instance
