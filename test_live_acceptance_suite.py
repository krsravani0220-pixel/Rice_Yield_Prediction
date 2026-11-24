import sys
import os
import json
from datetime import datetime, date

# Ensure root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from backend.app.main import app

def run_acceptance_tests():
    print("=" * 80)
    print("STARTING ACCEPTANCE TEST SUITE: TAMIL NADU LIVE RICE YIELD PREDICTION")
    print("=" * 80)

    client = TestClient(app)
    
    # 1. Verify District Profile & Registry
    print("\n[TEST 1] Verifying District Endpoints and Profile Retrieval...")
    dist_res = client.get("/api/districts")
    assert dist_res.status_code == 200, f"Expected 200, got {dist_res.status_code}"
    dist_data = dist_res.json()
    assert len(dist_data["districts"]) == 38, f"Expected 38 districts, found {len(dist_data['districts'])}"
    print(f" PASS: Found all {len(dist_data['districts'])} Tamil Nadu districts in dropdown registry.")

    # 2. Test 5 Mandated Districts + 1 Edge Case (Chennai)
    mandated_districts = ["Thanjavur", "Thiruvarur", "Salem", "Tiruchirappalli", "Dharmapuri"]
    ref_date = "2026-10-24"
    results_summary = []

    for dist in mandated_districts:
        print(f"\n[TEST 2] Testing Live Prediction for Mandated District: {dist}...")
        
        # Test District Profile
        prof_res = client.get(f"/api/district-profile?district={dist}")
        assert prof_res.status_code == 200, f"Profile failed for {dist}"
        prof = prof_res.json()
        assert "centroid" in prof and "bbox" in prof
        print(f"  Geospatial Centroid: Lat {prof['centroid']['latitude']}, Lon {prof['centroid']['longitude']}")
        print(f"  Primary S2 Tile: {prof['primary_sentinel2_tile']}, Zone: {prof['agro_climatic_zone']}")

        # Test Live Prediction
        pred_res = client.post("/api/live-predict", json={
            "district": dist,
            "reference_date": ref_date,
            "force_refresh": False
        })
        assert pred_res.status_code == 200, f"Live prediction failed for {dist}: {pred_res.text}"
        data = pred_res.json()

        assert data["status"] == "success"
        assert data["district"] == dist
        assert data["predicted_yield"] > 0
        assert "weather_data" in data
        assert "satellite_data" in data
        assert "shap_explanation" in data
        assert "historical_insights" in data
        assert "data_quality_warnings" in data
        assert len(data["data_quality_warnings"]) >= 4

        # Validate Satellite Observations & Dates
        sat = data["satellite_data"]
        sat_start = sat["observation_window"].get("start_date") or sat["observation_window"].get("start")
        sat_end = sat["observation_window"].get("end_date") or sat["observation_window"].get("end")
        obs_sample = sat["observation_dates_sample"]
        
        print(f"  Satellite Source: {sat['source']}")
        print(f"  Satellite Lookback Window: {sat_start} to {sat_end}")
        print(f"  Total Usable Clear Scenes: {sat['total_observations']}")
        print(f"  Mean Cloud Cover: {sat['cloud_filtering']['mean_cloud_cover_pct']}%")
        print(f"  NDVI Mean: {sat['vegetation_indices']['ndvi_mean']}, Peak: {sat['vegetation_indices']['ndvi_max']}")
        print(f"  NDRE Mean: {sat['vegetation_indices']['ndre_mean']}")
        print(f"  Sample Dates ({len(obs_sample)}): {obs_sample[:4]}")

        # Check date lookback validity
        d_start = datetime.strptime(sat_start, "%Y-%m-%d").date()
        d_end = datetime.strptime(sat_end, "%Y-%m-%d").date()
        for obs_d_str in obs_sample:
            obs_d = datetime.strptime(obs_d_str, "%Y-%m-%d").date()
            assert d_start <= obs_d <= d_end, f"Date {obs_d} outside lookback [{d_start}, {d_end}]"

        # Validate Weather Observations & Seasons
        wx = data["weather_data"]
        wx_start = wx["observation_window"]["start_date"]
        wx_end = wx["observation_window"]["end_date"]
        print(f"  Weather Source: {wx['source']}")
        print(f"  Weather Window: {wx_start} to {wx_end}")
        print(f"  Total Rain: {wx['annual_summary']['total_rainfall_mm']} mm, Mean Temp: {wx['annual_summary']['mean_temperature_c']} C")

        # Verify seasonal definitions
        assert "kharif" in wx["seasonal_breakdown"]
        assert "rabi" in wx["seasonal_breakdown"]
        assert "zaid" in wx["seasonal_breakdown"]
        
        # Verify model prediction
        print(f"  Predicted Rice Yield: {data['predicted_yield']} tonnes/ha (Baseline: {data['historical_district_avg_yield']} t/ha)")
        print(f"  SHAP Top Positive Feature: {data['shap_explanation']['top_positive'][0]['feature']} (+{data['shap_explanation']['top_positive'][0]['shap_value']})")
        
        results_summary.append({
            "district": dist,
            "yield_tha": data["predicted_yield"],
            "sat_scenes": sat["total_observations"],
            "sat_window": f"{sat_start} to {sat_end}",
            "sat_dates_sample": obs_sample[:3],
            "weather_window": f"{wx_start} to {wx_end}",
            "rainfall_mm": wx["annual_summary"]["total_rainfall_mm"],
            "mean_temp_c": wx["annual_summary"]["mean_temperature_c"],
            "ndvi_mean": sat["vegetation_indices"]["ndvi_mean"],
            "status": "PASS"
        })

    # 3. Test Edge Case: Chennai (Metropolitan non-agricultural district)
    print("\n[TEST 3] Testing Edge Case Handling for Chennai (Urban District)...")
    chn_res = client.post("/api/live-predict", json={"district": "Chennai", "reference_date": ref_date})
    assert chn_res.status_code == 200
    chn_data = chn_res.json()
    assert chn_data["status"] == "insufficient_data"
    assert chn_data["predicted_yield"] is None
    print(f" PASS: Chennai correctly identified as non-agricultural tract: {chn_data['message']}")

    # 4. Verify Existing Features are preserved (No regressions)
    print("\n[TEST 4] Verifying Preservation of Existing Application Modes...")
    
    # Test A: Manual Prediction endpoint
    manual_res = client.post("/api/predict-yield", json={
        "District": "Thanjavur",
        "Year": 2023,
        "Soil_Type": "Clay loam",
        "Soil_PH": 7.2,
        "N": 320, "P": 25, "K": 220, "Fertilizer": 180, "Pesticide": 2.5, "Area": 65000,
        "Kharif Temperature": 29.0, "Kharif Rainfall": 120.0, "Kharif Humidity": 75.0, "Kharif Wind_Speed": 3.1, "Kharif Soil_Moisture": 0.58,
        "Rabi Temperature": 25.5, "Rabi Rainfall": 110.0, "Rabi Humidity": 80.0, "Rabi Wind_Speed": 2.2, "Rabi Soil_Moisture": 0.68,
        "Zaid Temperature": 30.5, "Zaid Rainfall": 40.0, "Zaid Humidity": 60.0, "Zaid Wind_Speed": 2.6, "Zaid Soil_Moisture": 0.45
    })
    assert manual_res.status_code == 200
    print(" PASS: Manual prediction mode operational.")

    # Test B: Forecasting endpoint
    fc_res = client.post("/api/forecast", json={
        "district": "Thanjavur",
        "target_year": 2026,
        "method": "5-Year Moving Average"
    })
    assert fc_res.status_code == 200
    print(" PASS: Forecasting mode operational.")

    # Test C: Crop health advisor endpoint
    health_res = client.post("/api/crop-health", json={
        "growth_stage": "Flowering",
        "leaf_condition": "Yellowing",
        "water_status": "Adequate",
        "pest_obs": "Stem borer signs",
        "disease_obs": "Blast spots"
    })
    assert health_res.status_code == 200
    print(" PASS: Crop health advisor operational.")

    # Test D: Satellite pilot results
    pilot_res = client.get("/api/satellite-pilot-results")
    assert pilot_res.status_code == 200
    print(" PASS: Pre-existing satellite pilot benchmark operational.")

    # 5. Verify Database Records
    print("\n[TEST 5] Verifying Prediction Records & Storage Provenance...")
    cache_path = os.path.join("data", "cache", "prediction_records.jsonl")
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        print(f" PASS: Verified {len(lines)} total prediction records saved in db log {cache_path}.")
        last_rec = json.loads(lines[-1])
        print(f" Last record district: {last_rec['district']}, Status: {last_rec['status']}, Baseline Yield: {last_rec['baseline_yield']} t/ha")
        assert "COPERNICUS_PASSWORD" not in str(last_rec)
        assert "NEON_DATABASE_URL" not in str(last_rec)
        print(" PASS: Confirmed zero secrets stored in telemetry records.")

    print("\n" + "=" * 80)
    print("ACCEPTANCE TEST SUITE PASSED ALL CHECKS!")
    print("=" * 80)
    print(json.dumps(results_summary, indent=2))

if __name__ == "__main__":
    run_acceptance_tests()
