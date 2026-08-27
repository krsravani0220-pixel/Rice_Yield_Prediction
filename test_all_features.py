import sys
import urllib.request
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def test_api_call(title, url, payload=None):
    print(f"\n================ {title} ================")
    data = json.dumps(payload).encode('utf-8') if payload else None
    headers = {'Content-Type': 'application/json'} if payload else {}
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        res = urllib.request.urlopen(req)
        res_json = json.loads(res.read().decode('utf-8'))
        print(f"Status: SUCCESS (200 OK)")
        if 'predicted_yield' in res_json:
            print(f"  Predicted Yield: {res_json['predicted_yield']} tonnes/ha")
            print(f"  Mode: {res_json.get('mode')}")
            print(f"  SHAP Base Value: {res_json.get('shap_explanation', {}).get('base_value')}")
            print(f"  Suggestions EN Count: {len(res_json.get('suggestions_en', []))}")
            print(f"  Suggestions TA Count: {len(res_json.get('suggestions_ta', []))}")
            if 'forecasted_features' in res_json:
                print(f"  Forecasted Features Count: {len(res_json['forecasted_features'])}")
        elif 'advisories_en' in res_json:
            print(f"  Crop Health Advisories EN Count: {len(res_json['advisories_en'])}")
            print(f"  Crop Health Advisories TA Count: {len(res_json['advisories_ta'])}")
            print(f"  Sample EN Advice: {res_json['advisories_en'][0]}")
        elif 'best_model' in res_json:
            print(f"  Best Model: {res_json['best_model']}")
            print(f"  Metrics Rows Count: {len(res_json['metrics'])}")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == '__main__':
    # 1. Manual Prediction (Full Payload)
    p_manual = {
        "District": "Thanjavur", "Year": 2024, "Soil_Type": "alluvial soil",
        "Kharif Temperature": 29.5, "Kharif Rainfall": 120.5, "Kharif Humidity": 70.2, "Kharif Wind_Speed": 3.2, "Kharif Soil_Moisture": 0.55,
        "Rabi Temperature": 25.1, "Rabi Rainfall": 95.0, "Rabi Humidity": 78.0, "Rabi Wind_Speed": 2.3, "Rabi Soil_Moisture": 0.65,
        "Zaid Temperature": 29.8, "Zaid Rainfall": 45.0, "Zaid Humidity": 62.0, "Zaid Wind_Speed": 2.4, "Zaid Soil_Moisture": 0.48,
        "Soil_PH": 7.2, "N": 300.0, "P": 20.0, "K": 200.0, "Fertilizer": 160.0, "Pesticide": 2.2, "Area": 60000.0
    }
    t1 = test_api_call("1. MANUAL PREDICTION API", "http://127.0.0.1:8000/api/predict-yield", p_manual)

    # 2. Forecast Mode
    p_forecast = {
        "district": "Thanjavur",
        "target_year": 2026,
        "method": "Exponential Smoothing"
    }
    t2 = test_api_call("2. FORECAST MODE API", "http://127.0.0.1:8000/api/forecast", p_forecast)

    # 3. Crop Health Advisor
    p_health = {
        "growth_stage": "Tillering",
        "leaf_condition": "Yellowing",
        "water_status": "Drought Stress",
        "pest_obs": "Stem Borer",
        "disease_obs": "None"
    }
    t3 = test_api_call("3. CROP HEALTH ADVISOR API", "http://127.0.0.1:8000/api/crop-health", p_health)

    # 4. ML Model Benchmark
    t4 = test_api_call("4. ML MODEL BENCHMARK API", "http://127.0.0.1:8000/api/model-metrics")

    if all([t1, t2, t3, t4]):
        print("\n🎉 ALL 4 CORE MODULE APIS ARE 100% OPERATIONAL!")
    else:
        print("\n❌ SOME APIS FAILED!")

