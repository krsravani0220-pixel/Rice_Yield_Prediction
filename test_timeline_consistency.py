"""
Rice Yield Prediction - Reference Timeline Consistency Test Suite
==================================================================
Tests:
1. Historical year selection (1997-2023)
2. Current year dynamic handling (system date)
3. Future year forecasting (2027+)
4. Backend date validation (< 1997 rejection, non-pilot satellite rejection)
5. All three prediction modes (Manual, Forecast, Satellite)
6. Frontend & backend consistency
"""

import os
import sys
from datetime import datetime

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi import HTTPException
from backend.app.main import (
    app,
    get_district_year_params,
    predict_yield,
    forecast_yield,
    satellite_predict_live,
    get_satellite_district_prediction,
    ManualPredictRequest,
    ForecastRequest,
    SatellitePredictLiveRequest,
    inference_system
)

def run_tests():
    print("=" * 80)
    print("RUNNING REFERENCE TIMELINE & YEAR CONSISTENCY VERIFICATION SUITE")
    print("=" * 80)

    current_year = datetime.now().year
    print(f"System Detected Current Year: {current_year}")
    print(f"System Detected Current Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("-" * 80)

    # -------------------------------------------------------------------------
    # TEST 1: Historical Data & Year Selection (1997 - 2023)
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Historical Data (1997-2023) Observations & Integrity:")
    for yr in [1997, 2005, 2015, 2020, 2023]:
        res = get_district_year_params(district="Thanjavur", year=yr)
        assert res["source_type"] == "Dataset Value", f"Expected Dataset Value for {yr}, got {res['source_type']}"
        assert res["is_historical"] is True, f"Expected is_historical=True for {yr}"
        assert res["year"] == yr
        params = res["params"]
        assert "Area" in params and params["Area"] is not None
        assert "Kharif Rainfall" in params and params["Kharif Rainfall"] is not None
        print(f"  ✓ Year {yr} loaded genuine dataset record: Area={params.get('Area')} ha, Yield={params.get('Yield')} t/ha")

    # Verify invalid or excluded district returns 400
    try:
        get_district_year_params(district="InvalidDistrict", year=1997)
        assert False, "Should have rejected invalid district"
    except HTTPException as e:
        assert e.status_code == 400, f"Expected 400, got {e.status_code}"
        print(f"  ✓ Invalid district correctly rejected with 400: {e.detail}")

    # Verify missing historical record handling (if any year is not found in processed_df)
    try:
        # Simulate check with year in historical range that has no row
        # (e.g. temporary filter check)
        orig_df = inference_system.processed_df
        inference_system.processed_df = orig_df[orig_df['Year'] != 1998] # temporarily hide 1998
        get_district_year_params(district="Thanjavur", year=1998)
        assert False, "Should have returned 404 for unrecorded historical year"
    except HTTPException as e:
        assert e.status_code == 404, f"Expected 404, got {e.status_code}"
        print(f"  ✓ Unrecorded historical year correctly returned 404 without fabrication: {e.detail}")
    finally:
        inference_system.processed_df = orig_df

    # -------------------------------------------------------------------------
    # TEST 2: Current Year Dynamic Handling
    # -------------------------------------------------------------------------
    print(f"\n[TEST 2] Current Year ({current_year}) Dynamic Handling:")
    res_cur = get_district_year_params(district="Thanjavur", year=current_year)
    assert res_cur["source_type"] == "Forecasted Value"
    assert res_cur["is_historical"] is False
    assert res_cur["year"] == current_year
    print(f"  ✓ /api/district-year-params for current year ({current_year}) returns Forecasted Value (unobserved ground truth)")

    # Test ForecastRequest default target_year is dynamic
    fc_req_default = ForecastRequest(district="Thanjavur")
    assert fc_req_default.target_year == current_year, f"Expected default {current_year}, got {fc_req_default.target_year}"
    print(f"  ✓ ForecastRequest default target_year dynamically evaluates to current year: {fc_req_default.target_year}")

    # -------------------------------------------------------------------------
    # TEST 3: Future Year Forecasting (2027, 2028, 2030, 2035)
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Future Year Forecasting (Multi-year horizons & methods):")
    methods = ["Exponential Smoothing", "5-Year Moving Average", "Linear Trend"]
    future_years = [current_year + 1, current_year + 2, current_year + 4, current_year + 9]

    for f_yr in future_years:
        for m in methods:
            req = ForecastRequest(district="Thanjavur", target_year=f_yr, method=m)
            res = forecast_yield(req)
            assert res["mode"].startswith("Forecast Mode"), f"Mode unexpected: {res['mode']}"
            assert res["is_historical"] is False
            assert res["predicted_yield"] > 0.0
            assert "all_methods_forecasts" in res
            assert len(res["all_methods_forecasts"]) == 3
            print(f"  ✓ Future Forecast {f_yr} ({m}): Predicted Yield = {res['predicted_yield']} t/ha")

    # -------------------------------------------------------------------------
    # TEST 4: Backend Date Validation & Constraints
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Backend Boundary & Date Validation:")
    # A. Year prior to 1997 in get_district_year_params
    try:
        get_district_year_params(district="Thanjavur", year=1996)
        assert False, "Should have rejected year 1996"
    except HTTPException as e:
        assert e.status_code == 400
        print(f"  ✓ Year 1996 correctly rejected in /api/district-year-params: {e.detail}")

    # B. Year prior to 1997 in forecast_yield
    try:
        forecast_yield(ForecastRequest(district="Thanjavur", target_year=1990))
        assert False, "Should have rejected forecast year 1990"
    except HTTPException as e:
        assert e.status_code == 400
        print(f"  ✓ Year 1990 correctly rejected in /api/forecast: {e.detail}")

    # C. Non-pilot district rejection in satellite live prediction
    try:
        satellite_predict_live(SatellitePredictLiveRequest(district="Madurai"))
        assert False, "Should have rejected non-pilot district Madurai"
    except HTTPException as e:
        assert e.status_code == 400
        print(f"  ✓ Non-pilot district 'Madurai' correctly rejected for Satellite Prediction: {e.detail}")

    # -------------------------------------------------------------------------
    # TEST 5: All Three Prediction Modes Execution
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Validating All Three Prediction Modes End-to-End:")

    # MODE 1: Manual Prediction Mode (for historical, current, and future years)
    base_input = {
        "District": "Thanjavur", "Soil_Type": "alluvial soil",
        "Kharif Temperature": 29.5, "Kharif Rainfall": 120.5, "Kharif Humidity": 70.2, "Kharif Wind_Speed": 3.2, "Kharif Soil_Moisture": 0.55,
        "Rabi Temperature": 25.1, "Rabi Rainfall": 95.0, "Rabi Humidity": 78.0, "Rabi Wind_Speed": 2.3, "Rabi Soil_Moisture": 0.65,
        "Zaid Temperature": 29.8, "Zaid Rainfall": 45.0, "Zaid Humidity": 62.0, "Zaid Wind_Speed": 2.4, "Zaid Soil_Moisture": 0.48,
        "Soil_PH": 7.2, "N": 300.0, "P": 20.0, "K": 200.0, "Fertilizer": 160.0, "Pesticide": 2.2, "Area": 60000.0
    }

    for test_yr in [2005, current_year, current_year + 2]:
        m_req = ManualPredictRequest(Year=test_yr, **base_input)
        m_res = predict_yield(m_req)
        assert m_res["predicted_yield"] > 0
        assert m_res["year"] == test_yr
        assert "shap_explanation" in m_res
        print(f"  ✓ Mode 1 (Manual) for Year {test_yr}: Predicted Yield = {m_res['predicted_yield']} t/ha, SHAP Base = {m_res['shap_explanation']['base_value']}")

    # MODE 2: Weather Forecast-Based Prediction Mode
    fc_res = forecast_yield(ForecastRequest(district="Salem", target_year=current_year + 1, method="Exponential Smoothing"))
    assert fc_res["predicted_yield"] > 0
    assert fc_res["target_year"] == current_year + 1
    assert fc_res["is_historical"] is False
    print(f"  ✓ Mode 2 (Forecast) for Salem Year {current_year + 1}: Predicted Yield = {fc_res['predicted_yield']} t/ha")

    # MODE 3: Satellite-Based Prediction Mode for Pilot Districts
    pilot_dist = "Thanjavur"
    today_str = datetime.now().strftime("%Y-%m-%d")
    sat_live_req = SatellitePredictLiveRequest(district=pilot_dist, reference_date=today_str)
    sat_live_res = satellite_predict_live(sat_live_req)
    assert sat_live_res["retrieval_status"] == "success"
    assert sat_live_res["predicted_yield_t_ha"] is not None
    assert today_str in sat_live_res["requested_observation_window"]
    print(f"  ✓ Mode 3 (Satellite Live) for {pilot_dist} (Ref Date: {today_str}): Predicted Yield = {sat_live_res['predicted_yield_t_ha']} t/ha")
    print(f"    Obs Window: {sat_live_res['requested_observation_window']}")
    print(f"    Sequence: {sat_live_res['data_sufficiency']['sequence_years']}")

    # Also test get_satellite_district_prediction endpoint with dynamic year
    sat_dist_res = get_satellite_district_prediction(district="Thanjavur")
    assert sat_dist_res["status"] == "success"
    assert sat_dist_res["year"] == current_year
    print(f"  ✓ /api/satellite-district-prediction default year evaluated to current year: {sat_dist_res['year']}")

    # -------------------------------------------------------------------------
    # TEST 6: Frontend & Backend Consistency Check
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Frontend & Backend Consistency Verification:")
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html_src = f.read()

    with open("frontend/app.js", "r", encoding="utf-8") as f:
        js_src = f.read()

    # Check that hardcoded 2026/27 constraints are removed from UI copy
    assert "Explore Forecast (2026/27)" not in html_src
    assert "Allowed future target years: <strong>2026</strong> and <strong>2027</strong>." not in html_src
    assert 'min="1997-01-01"' in html_src
    assert 'value="2026-10-24"' not in html_src

    # Check JS dynamic population logic
    assert "populateYearSelectors()" in js_src
    assert "initDateControls()" in js_src
    assert "Historical Years (1997–2023)" in js_src
    assert "new Date().getFullYear()" in js_src
    print("  ✓ Frontend HTML & JS successfully verified for dynamic year population & 1997 reference baseline.")

    print("\n" + "=" * 80)
    print("🎉 ALL 6 VERIFICATION TEST SUITES PASSED FLAWLESSLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
