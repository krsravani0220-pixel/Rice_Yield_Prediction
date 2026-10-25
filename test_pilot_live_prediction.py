"""
Verification Test Suite for Pilot Districts Live Satellite Prediction
Tests POST /api/satellite-predict-live across all 5 pilot districts and 1 non-pilot district.
"""

import urllib.request
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"
PILOT_DISTRICTS = ["Thanjavur", "Thiruvarur", "Salem", "Tiruchirappalli", "Dharmapuri"]

def test_endpoint():
    print("=" * 70)
    print("RUNNING PILOT DISTRICTS SATELLITE PREDICTION VERIFICATION SUITE")
    print("=" * 70)

    results = {}

    for district in PILOT_DISTRICTS:
        print(f"\n--- Testing District: {district} ---")
        req_data = json.dumps({"district": district}).encode("utf-8")
        req = urllib.request.Request(
            f"{BASE_URL}/api/satellite-predict-live",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                status_code = resp.getcode()
                body = json.loads(resp.read().decode("utf-8"))
                results[district] = body

                print(f"Status Code: {status_code}")
                print(f"District Returned: {body.get('district')}")
                print(f"Retrieval Status: {body.get('retrieval_status')}")
                print(f"Cache Status: {body.get('cache_status')}")
                print(f"Acquisition Dates: {body.get('acquisition_dates')}")
                print(f"Product IDs: {body.get('product_ids')}")
                print(f"Observation Count: {body.get('observation_count')}")
                print(f"Data Sufficiency: {body.get('data_sufficiency')}")
                print(f"Model Name: {body.get('model_name')}")
                print(f"Predicted Yield (t/ha): {body.get('predicted_yield_t_ha')}")
                print(f"Vegetation Indices: {body.get('vegetation_indices')}")

                # Assertions
                assert body.get("district") == district, f"District mismatch: expected {district}, got {body.get('district')}"
                assert body.get("retrieval_status") == "success", f"Retrieval failed for {district}"
                assert body.get("predicted_yield_t_ha") is not None, f"Yield is None for {district}"
                assert body.get("predicted_yield_t_ha") > 0, f"Yield must be > 0, got {body.get('predicted_yield_t_ha')}"
                vi = body.get("vegetation_indices", {})
                assert "ndvi" in vi and vi["ndvi"]["mean"] is not None, "ndvi mean missing"
                assert "ndre" in vi, "ndre missing"
                assert "evi" in vi and vi["evi"]["mean"] is not None, "evi mean missing"
                assert "ndwi" in vi and vi["ndwi"]["mean"] is not None, "ndwi mean missing"
                assert vi["valid_pixels"] > 0, "valid_pixels must be > 0"
                print(f"[PASS] All assertions passed for {district}")

        except Exception as e:
            print(f"FAILED for {district}: {e}")
            sys.exit(1)

    # Verify that districts sharing granules have distinct statistics due to geographic masking
    print("\n--- Verifying Distinct Spatial Masking Across Districts Sharing Granules ---")
    salem_ndvi = results["Salem"]["vegetation_indices"]["ndvi"]["mean"]
    trichy_ndvi = results["Tiruchirappalli"]["vegetation_indices"]["ndvi"]["mean"]
    dharmapuri_ndvi = results["Dharmapuri"]["vegetation_indices"]["ndvi"]["mean"]
    thanjavur_ndvi = results["Thanjavur"]["vegetation_indices"]["ndvi"]["mean"]
    thiruvarur_ndvi = results["Thiruvarur"]["vegetation_indices"]["ndvi"]["mean"]

    print(f"Salem NDVI: {salem_ndvi} | Trichy NDVI: {trichy_ndvi} | Dharmapuri NDVI: {dharmapuri_ndvi}")
    print(f"Thanjavur NDVI: {thanjavur_ndvi} | Thiruvarur NDVI: {thiruvarur_ndvi}")

    assert len({salem_ndvi, trichy_ndvi, dharmapuri_ndvi, thanjavur_ndvi, thiruvarur_ndvi}) == 5, "All 5 districts must have unique NDVI values from their distinct geographic masks"
    print("[PASS] Spatial masking test passed: all 5 districts have authentic distinct pixel statistics!")

    # Test non-pilot district rejection
    print("\n--- Testing Non-Pilot District Rejection ---")
    non_pilot = "Madurai"
    req_data = json.dumps({"district": non_pilot}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/api/satellite-predict-live",
        data=req_data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"ERROR: Expected 400 for {non_pilot}, got {resp.getcode()}")
            sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"Expected HTTP {e.code} received: {e.read().decode('utf-8')}")
        assert e.code == 400, f"Expected 400, got {e.code}"
        print("[PASS] Non-pilot rejection passed!")

    print("\n" + "=" * 70)
    print("ALL API AND RASTER PROCESSING TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_endpoint()
