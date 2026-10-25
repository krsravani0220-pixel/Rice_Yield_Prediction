"""
Controlled LSTM Optimization Experiments for Tamil Nadu Rice Yield Prediction.

PHASE 1 AUDIT DEFECT CORRECTIONS:
1. Climatology computed strictly on training partition (Year <= 2020). Zero exposure of 2021-2023.
2. Missing lag fallback uses training district historical mean, never the current year's yield.
3. Satellite indicator feature ('is_satellite_observed') explicitly added.
4. District boundaries strictly enforced per-district.
5. Imputation and StandardScaler fit strictly on training set.
6. Hyperparameter and architecture selection performed strictly on Validation Set (Year 2021).
   Final Test Set (2022-2023) held out strictly for final benchmark comparison.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(project_root)

# Set global seeds
torch.manual_seed(42)
np.random.seed(42)

print("=" * 80)
print("PHASE 2: CONTROLLED LSTM REPRODUCIBLE EXPERIMENT SUITE")
print("=" * 80)

# 1. Load Data
df_hist = pd.read_csv("data/processed/rice_yield_processed.csv")
df_sat = pd.read_csv("outputs/data/satellite_yield_training_dataset.csv")

# Exclude Chennai
df_hist = df_hist[df_hist["District"] != "Chennai"].copy()
df_sat = df_sat[df_sat["District"] != "Chennai"].copy()

# Feature Columns
weather_cols = [
    'Kharif Temperature', 'Kharif Rainfall', 'Kharif Humidity', 'Kharif Wind_Speed', 'Kharif Soil_Moisture',
    'Rabi Temperature', 'Rabi Rainfall', 'Rabi Humidity', 'Rabi Wind_Speed', 'Rabi Soil_Moisture',
    'Zaid Temperature', 'Zaid Rainfall', 'Zaid Humidity', 'Zaid Wind_Speed', 'Zaid Soil_Moisture'
]
soil_inputs_cols = ['Soil_PH', 'N', 'P', 'K', 'Fertilizer', 'Pesticide', 'Area']
satellite_cols = [
    'Kharif_NDVI_mean', 'Kharif_NDRE_mean', 'Kharif_EVI_mean', 'Kharif_NDWI_mean',
    'Rabi_NDVI_mean', 'Rabi_NDRE_mean', 'Rabi_EVI_mean', 'Rabi_NDWI_mean',
    'Zaid_NDVI_mean', 'Zaid_NDRE_mean', 'Zaid_EVI_mean', 'Zaid_NDWI_mean'
]

# Strict Anti-Leakage Satellite Climatology (Year <= 2020 ONLY)
sat_train_df = df_sat[df_sat["Year"] <= 2020]
sat_climatology = sat_train_df.groupby("District")[satellite_cols].mean().to_dict("index")

# District historical mean yields for train partition (Year <= 2020)
dist_train_mean_yield = df_hist[df_hist["Year"] <= 2020].groupby("District")["Yield"].mean().to_dict()
global_train_mean_yield = float(df_hist[df_hist["Year"] <= 2020]["Yield"].mean())

# Build Yield Lag Lookup
yield_lookup = {}
for _, r in df_hist.iterrows():
    yield_lookup[(r["District"], int(r["Year"]))] = float(r["Yield"]) if not pd.isna(r["Yield"]) else np.nan

# Build Satellite Lookup (2015-2023)
sat_lookup = {}
for _, r in df_sat.iterrows():
    sat_lookup[(r["District"], int(r["Year"]))] = {c: float(r[c]) for c in satellite_cols}

# Build Unified Records
feature_names = weather_cols + soil_inputs_cols + satellite_cols + ["is_satellite_observed", "Yield_Lag1"]
records_dict = {}

for _, r in df_hist.iterrows():
    d = r["District"]
    yr = int(r["Year"])
    y = float(r["Yield"]) if not pd.isna(r["Yield"]) else np.nan

    # Anti-leakage lag: NEVER use current y as fallback
    fallback_mean = dist_train_mean_yield.get(d, global_train_mean_yield)
    lag_y = yield_lookup.get((d, yr - 1), fallback_mean)
    if np.isnan(lag_y):
        lag_y = fallback_mean

    if (d, yr) in sat_lookup:
        sat_vals = sat_lookup[(d, yr)]
        is_sat_obs = 1.0
    else:
        sat_vals = sat_climatology.get(d, {c: 0.35 for c in satellite_cols})
        is_sat_obs = 0.0

    row_feat = {}
    for c in weather_cols + soil_inputs_cols:
        row_feat[c] = float(r[c]) if c in r and not pd.isna(r[c]) else np.nan
    for c in satellite_cols:
        row_feat[c] = float(sat_vals.get(c, 0.35))
    row_feat["is_satellite_observed"] = is_sat_obs
    row_feat["Yield_Lag1"] = float(lag_y)
    row_feat["Yield"] = y

    records_dict[(d, yr)] = row_feat


def build_sequences_for_window(window_size=3):
    districts = sorted(df_hist["District"].unique())
    all_years = sorted(df_hist["Year"].unique())

    seqs, tgts, metas = [], [], []
    for d in districts:
        for yr in all_years:
            # Check all years in window: [yr - window_size + 1, ..., yr]
            needed_years = [yr - (window_size - 1) + step for step in range(window_size)]
            if all((d, y_req) in records_dict for y_req in needed_years):
                rows = [records_dict[(d, y_req)] for y_req in needed_years]
                y_target = rows[-1]["Yield"]
                if np.isnan(y_target):
                    continue

                feat_seq = []
                for row in rows:
                    feat_seq.append([row[c] for c in feature_names])

                seqs.append(np.array(feat_seq, dtype=np.float32))
                tgts.append(float(y_target))
                metas.append((d, yr))

    seqs = np.array(seqs)
    tgts = np.array(tgts, dtype=np.float32)

    # Chronological Splits
    train_mask = [m[1] <= 2020 for m in metas]
    val_mask = [m[1] == 2021 for m in metas]
    test_mask = [m[1] in [2022, 2023] for m in metas]

    X_tr_raw, y_tr = seqs[train_mask], tgts[train_mask]
    X_va_raw, y_va = seqs[val_mask], tgts[val_mask]
    X_te_raw, y_te = seqs[test_mask], tgts[test_mask]
    test_meta = [m for i, m in enumerate(metas) if test_mask[i]]

    # Preprocessing strictly on train split
    N_tr, T_s, F_d = X_tr_raw.shape
    imp = SimpleImputer(strategy='median')
    scl = StandardScaler()

    X_tr_flat = imp.fit_transform(X_tr_raw.reshape(-1, F_d))
    scl.fit(X_tr_flat)

    X_tr = scl.transform(X_tr_flat).reshape(N_tr, T_s, F_d).astype(np.float32)
    X_va = scl.transform(imp.transform(X_va_raw.reshape(-1, F_d))).reshape(len(X_va_raw), T_s, F_d).astype(np.float32)
    X_te = scl.transform(imp.transform(X_te_raw.reshape(-1, F_d))).reshape(len(X_te_raw), T_s, F_d).astype(np.float32)

    return (X_tr, y_tr), (X_va, y_va), (X_te, y_te), test_meta, F_d, imp, scl


class SeqDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
    def __len__(self):
        return len(self.X)
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


# Model Architecture Definitions
class Attention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.attn = nn.Linear(hidden_dim, 1)
    def forward(self, x):
        scores = self.attn(x)
        weights = torch.softmax(scores, dim=1)
        context = torch.sum(weights * x, dim=1)
        return context, weights


# Arch 1: Baseline Attention-BiLSTM (2 layers, hidden=64, BatchNorm)
class BaselineAttentionBiLSTM(nn.Module):
    def __init__(self, input_dim=36, hidden_dim=64, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=2, batch_first=True, bidirectional=True, dropout=dropout)
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
    def forward(self, x):
        out, _ = self.lstm(x)
        ctx, _ = self.attention(out)
        return self.fc(ctx).squeeze(-1)


# Arch 2: Simple Unidirectional LSTM (No attention, compact, final step hidden state)
class SimpleUniLSTM(nn.Module):
    def __init__(self, input_dim=36, hidden_dim=32, num_layers=1, dropout=0.1):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, dropout=dropout if num_layers > 1 else 0.0)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(16, 1)
        )
    def forward(self, x):
        out, _ = self.lstm(x)
        # Use final timestep output
        last_step = out[:, -1, :]
        return self.fc(last_step).squeeze(-1)


# Arch 3: Compact Attention BiLSTM with LayerNorm (No BatchNorm instability)
class CompactLayerNormAttentionBiLSTM(nn.Module):
    def __init__(self, input_dim=36, hidden_dim=32, dropout=0.15):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=1, batch_first=True, bidirectional=True)
        self.attention = Attention(hidden_dim * 2)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),
            nn.LayerNorm(32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1)
        )
    def forward(self, x):
        out, _ = self.lstm(x)
        ctx, _ = self.attention(out)
        return self.fc(ctx).squeeze(-1)


# Arch 4: Residual Lag-Skip LSTM (Predicts delta over previous year's yield)
class ResidualSkipLSTM(nn.Module):
    def __init__(self, input_dim=36, hidden_dim=32, dropout=0.15, lag_feature_idx=-1):
        super().__init__()
        self.lag_idx = lag_feature_idx
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=1, batch_first=True, bidirectional=False)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(16, 1)
        )
    def forward(self, x):
        out, _ = self.lstm(x)
        last_h = out[:, -1, :]
        delta = self.fc(last_h).squeeze(-1)
        # unscaled lag is in raw, but in scaled x, delta modulates
        return delta


# Trainer with Early Stopping strictly on Validation Set (Year 2021)
def train_and_evaluate_model(
    model,
    train_data,
    val_data,
    test_data,
    lr=0.002,
    weight_decay=1e-4,
    epochs=120,
    patience=25,
    is_residual=False
):
    X_train, y_train = train_data
    X_val, y_val = val_data
    X_test, y_test = test_data

    train_loader = DataLoader(SeqDataset(X_train, y_train), batch_size=32, shuffle=True)
    val_loader = DataLoader(SeqDataset(X_val, y_val), batch_size=32, shuffle=False)

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=10, min_lr=1e-5)
    criterion = nn.SmoothL1Loss()

    best_val_loss = float('inf')
    best_weights = None
    patience_counter = 0

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for bx, by in train_loader:
            optimizer.zero_grad()
            pred = model(bx)
            loss = criterion(pred, by)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            total_loss += loss.item() * len(by)

        train_loss = total_loss / len(X_train)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for bx, by in val_loader:
                pred = model(bx)
                val_loss += criterion(pred, by).item() * len(by)
        val_loss = val_loss / len(X_val)

        scheduler.step(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_weights = {k: v.clone() for k, v in model.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                break

    model.load_state_dict(best_weights)
    model.eval()

    with torch.no_grad():
        val_preds = model(torch.tensor(X_val)).numpy()
        test_preds = model(torch.tensor(X_test)).numpy()

    val_mae = float(mean_absolute_error(y_val, val_preds))
    val_rmse = float(np.sqrt(mean_squared_error(y_val, val_preds)))
    val_r2 = float(r2_score(y_val, val_preds))

    test_mae = float(mean_absolute_error(y_test, test_preds))
    test_rmse = float(np.sqrt(mean_squared_error(y_test, test_preds)))
    test_r2 = float(r2_score(y_test, test_preds))

    return {
        "best_val_smooth_l1": float(best_val_loss),
        "val_mae": val_mae,
        "val_rmse": val_rmse,
        "val_r2": val_r2,
        "test_mae": test_mae,
        "test_rmse": test_rmse,
        "test_r2": test_r2,
        "test_preds": test_preds,
        "best_weights": best_weights,
        "stopped_epoch": epoch
    }


# RUN EXPERIMENTS
print("\n" + "=" * 80)
print("EXPERIMENT 1: VARYING ARCHITECTURE (Window W=3, Fixed lr=0.002, Early Stopping on Val 2021)")
print("=" * 80)

(X_tr3, y_tr3), (X_va3, y_va3), (X_te3, y_te3), test_meta3, F_dim, imp3, scl3 = build_sequences_for_window(window_size=3)
print(f"Dataset Split (W=3): Train={len(X_tr3)} (1999-2020), Val={len(X_va3)} (2021), Test={len(X_te3)} (2022-2023)")

architectures = {
    "Baseline_Attention_BiLSTM (2L, h=64, BatchNorm)": BaselineAttentionBiLSTM(input_dim=F_dim, hidden_dim=64, dropout=0.2),
    "Simple_UniLSTM_1L (1L, h=32, No Attention, Final Step)": SimpleUniLSTM(input_dim=F_dim, hidden_dim=32, num_layers=1, dropout=0.1),
    "Simple_UniLSTM_2L (2L, h=32, No Attention, Dropout=0.2)": SimpleUniLSTM(input_dim=F_dim, hidden_dim=32, num_layers=2, dropout=0.2),
    "Compact_Attention_BiLSTM_LayerNorm (1L, h=32, LayerNorm)": CompactLayerNormAttentionBiLSTM(input_dim=F_dim, hidden_dim=32, dropout=0.15)
}

exp1_results = {}
for name, m in architectures.items():
    torch.manual_seed(42)
    np.random.seed(42)
    res = train_and_evaluate_model(m, (X_tr3, y_tr3), (X_va3, y_va3), (X_te3, y_te3), lr=0.002, epochs=150, patience=25)
    exp1_results[name] = res
    print(f"\nModel: {name}")
    print(f"  Stopped Epoch: {res['stopped_epoch']}")
    print(f"  Val MAE:  {res['val_mae']:.4f} t/ha | Val RMSE:  {res['val_rmse']:.4f} t/ha | Val R2:  {res['val_r2']:.4f}")
    print(f"  Test MAE: {res['test_mae']:.4f} t/ha | Test RMSE: {res['test_rmse']:.4f} t/ha | Test R2: {res['test_r2']:.4f}")


print("\n" + "=" * 80)
print("EXPERIMENT 2: VARYING TEMPORAL WINDOW (W = 2, 3, 4, 5) using Simple_UniLSTM")
print("=" * 80)

window_results = {}
for w in [2, 3, 4, 5]:
    torch.manual_seed(42)
    np.random.seed(42)
    (X_trW, y_trW), (X_vaW, y_vaW), (X_teW, y_teW), metaW, Fw, _, _ = build_sequences_for_window(window_size=w)
    m = SimpleUniLSTM(input_dim=Fw, hidden_dim=32, num_layers=1, dropout=0.1)
    res = train_and_evaluate_model(m, (X_trW, y_trW), (X_vaW, y_vaW), (X_teW, y_teW), lr=0.002, epochs=150, patience=25)
    window_results[f"Window_W={w}"] = {
        "train_samples": len(X_trW),
        "val_samples": len(X_vaW),
        "test_samples": len(X_teW),
        "val_mae": res["val_mae"],
        "val_rmse": res["val_rmse"],
        "val_r2": res["val_r2"],
        "test_mae": res["test_mae"],
        "test_rmse": res["test_rmse"],
        "test_r2": res["test_r2"],
        "stopped_epoch": res["stopped_epoch"]
    }
    print(f"\nWindow W={w} (Train N={len(X_trW)}, Val N={len(X_vaW)}, Test N={len(X_teW)}):")
    print(f"  Val MAE:  {res['val_mae']:.4f} t/ha | Val RMSE:  {res['val_rmse']:.4f} t/ha | Val R2:  {res['val_r2']:.4f}")
    print(f"  Test MAE: {res['test_mae']:.4f} t/ha | Test RMSE: {res['test_rmse']:.4f} t/ha | Test R2: {res['test_r2']:.4f}")


print("\n" + "=" * 80)
print("EXPERIMENT 3: HYPERPARAMETER TUNING (Learning Rates & Dropout) on Top Architectures")
print("=" * 80)

hparam_results = {}
for lr in [0.001, 0.002, 0.004]:
    for drop in [0.05, 0.15, 0.25]:
        torch.manual_seed(42)
        np.random.seed(42)
        # Test on Window W=2 which had maximal training sample count and lowest sequence lag distortion
        (X_tr2, y_tr2), (X_va2, y_va2), (X_te2, y_te2), meta2, F2, _, _ = build_sequences_for_window(window_size=2)
        m = SimpleUniLSTM(input_dim=F2, hidden_dim=32, num_layers=1, dropout=drop)
        res = train_and_evaluate_model(m, (X_tr2, y_tr2), (X_va2, y_va2), (X_te2, y_te2), lr=lr, epochs=150, patience=25)
        cfg_name = f"UniLSTM_W=2_lr={lr}_drop={drop}"
        hparam_results[cfg_name] = res
        print(f"{cfg_name:<32} | Val MAE: {res['val_mae']:.4f} | Val R2: {res['val_r2']:.4f} | Test MAE: {res['test_mae']:.4f} | Test R2: {res['test_r2']:.4f}")

# Save full experiment findings to json
exp_summary = {
    "audit_defects_addressed": [
        "1. Satellite climatology strictly computed on Year <= 2020 (train split only).",
        "2. Missing lag yield fallback uses district historical training mean, preventing current-year target leakage.",
        "3. Introduced 'is_satellite_observed' indicator feature.",
        "4. Strict chronological early stopping on Validation 2021 without test set feedback."
    ],
    "architectures_evaluated": {k: {m: v for m, v in exp1_results[k].items() if m != 'best_weights' and m != 'test_preds'} for k in exp1_results},
    "windows_evaluated": window_results,
    "hparams_evaluated": {k: {m: v for m, v in hparam_results[k].items() if m != 'best_weights' and m != 'test_preds'} for k in hparam_results}
}

with open("outputs/metrics/controlled_lstm_experiments_report.json", "w", encoding="utf-8") as f:
    json.dump(exp_summary, f, indent=2)

print("\nSaved full experiment metrics to outputs/metrics/controlled_lstm_experiments_report.json")
print("=" * 80)
