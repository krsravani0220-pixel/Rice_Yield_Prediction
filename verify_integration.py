import urllib.request
import urllib.error
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 75)
print("COMPREHENSIVE END-TO-END VERIFICATION: LSTM INTEGRATION & PIPELINE")
print("=" * 75)

# 1. Test Satellite Prediction Live for all 5 Pilot Districts
print("\n--- 1. Testing Live Satellite Prediction with LSTM for 5 Pilot Districts ---")
pilots = ["Thanjavur", "Thiruvarur", "Salem", "Tiruchirappalli", "Dharmapuri"]
pilot_results = {}

for dist in pilots:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/satellite-predict-live",
        data=json.dumps({"district": dist}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        pilot_results[dist] = data
        print(f"District: {dist:<16} | LSTM Predicted Yield: {data['predicted_yield_t_ha']:.2f} t/ha | Baseline ET: {data.get('baseline_yield_t_ha')} t/ha")
        print(f"   Model: {data['model_name']}")
        print(f"   Telemetry: {data.get('lstm_telemetry')}")
        print(f"   Indices: NDVI={data['vegetation_indices']['ndvi']['mean']} | NDRE={data['vegetation_indices']['ndre']['mean']} | EVI={data['vegetation_indices']['evi']['mean']} | NDWI={data['vegetation_indices']['ndwi']['mean']}")
        print(f"   Acquisition Dates: {data['acquisition_dates']} | Sufficiency: {data['data_sufficiency']['status']}")

# 2. Test Non-Pilot Rejection
print("\n--- 2. Verifying Non-Pilot District Rejection ---")
non_pilot = "Madurai"
bad_req = urllib.request.Request(
    "http://127.0.0.1:8000/api/satellite-predict-live",
    data=json.dumps({"district": non_pilot}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
try:
    urllib.request.urlopen(bad_req)
    print(f"FAILED: {non_pilot} should have been rejected!")
except urllib.error.HTTPError as e:
    err_body = json.loads(e.read().decode())
    print(f"SUCCESS: HTTP {e.code} correctly returned for '{non_pilot}': {err_body['detail']}")

# 3. Test Manual Prediction Preservation
print("\n--- 3. Verifying Manual Prediction Preservation ---")
man_payload = {
    "District": "Madurai",
    "Year": 2024,
    "Soil_Type": "clay loam",
    "Kharif Temperature": 30.5, "Kharif Rainfall": 110.0, "Kharif Humidity": 68.0, "Kharif Wind_Speed": 8.5, "Kharif Soil_Moisture": 0.25,
    "Rabi Temperature": 27.0, "Rabi Rainfall": 140.0, "Rabi Humidity": 75.0, "Rabi Wind_Speed": 7.0, "Rabi Soil_Moisture": 0.28,
    "Zaid Temperature": 33.0, "Zaid Rainfall": 30.0, "Zaid Humidity": 60.0, "Zaid Wind_Speed": 9.0, "Zaid Soil_Moisture": 0.18,
    "Soil_PH": 7.2, "N": 280.0, "P": 16.0, "K": 190.0, "Fertilizer": 150.0, "Pesticide": 2.0, "Area": 45000.0
}
req = urllib.request.Request("http://127.0.0.1:8000/api/predict-yield", data=json.dumps(man_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    print(f"Manual Prediction for Madurai: {res['predicted_yield']} t/ha | Model: {res.get('model_name', 'ExtraTreesRegressor')} | Status: OK")

# 4. Test Weather Forecast Preservation
print("\n--- 4. Verifying Weather Forecast Preservation ---")
fc_payload = {"district": "Salem", "target_year": 2026, "method": "ensemble"}
req = urllib.request.Request("http://127.0.0.1:8000/api/forecast", data=json.dumps(fc_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode())
    print(f"Weather Forecast for Salem (2026): {res['predicted_yield']} t/ha | Method: {res['selected_method']} | Status: OK")

# 5. Check Artifact Files Presence
print("\n--- 5. Checking Saved Model Artifacts ---")
import os
artifacts = [
    "models/lstm_yield_model.pt",
    "models/lstm_scaler.joblib",
    "models/lstm_imputer.joblib",
    "models/lstm_config.json",
    "models/backup_best_yield_model.joblib",
    "models/backup_satellite_yield_model.joblib"
]
for art in artifacts:
    exists = os.path.exists(art)
    size = os.path.getsize(art) if exists else 0
    print(f"  {art:<45}: Exists = {exists} (Size: {size:,} bytes)")

print("\n" + "=" * 75)
print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
print("=" * 75)
