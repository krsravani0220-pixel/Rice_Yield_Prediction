import urllib.request
import json

def test_api_case(case_name, payload):
    print(f"\n--- Testing {case_name} ---")
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/predict-yield',
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    try:
        res = urllib.request.urlopen(req)
        res_json = json.loads(res.read().decode('utf-8'))
        print(f"Status: SUCCESS (200 OK)")
        print(f"Predicted Yield: {res_json['predicted_yield']} tonnes/ha")
        print(f"SHAP Base Value: {res_json['shap_explanation']['base_value']}")
        print(f"SHAP Top Positive: {[c['feature'] + ': +' + str(c['shap_value']) for c in res_json['shap_explanation']['top_positive'][:3]]}")
        print(f"SHAP Top Negative: {[c['feature'] + ': ' + str(c['shap_value']) for c in res_json['shap_explanation']['top_negative'][:3]]}")
        print(f"Historical Insights Count: {len(res_json['historical_insights'])}")
        for ins in res_json['historical_insights']:
            if ins['status'] != 'Within Typical Range':
                print(f"  Alert: {ins['feature']} ({ins['user_value']}) -> {ins['status']}")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

# CASE 1: Standard Valid Input
payload_case1 = {
    "District": "Thanjavur",
    "Year": 2024,
    "Soil_Type": "alluvial soil",
    "Kharif Temperature": 29.5,
    "Kharif Rainfall": 120.5,
    "Kharif Humidity": 70.2,
    "Kharif Wind_Speed": 3.2,
    "Kharif Soil_Moisture": 0.55,
    "Soil_PH": 7.2,
    "N": 300, "P": 20, "K": 200,
    "Fertilizer": 160, "Pesticide": 2.2, "Area": 60000.0
}

# CASE 2: Rainfall ABOVE Historical Range (920 mm)
payload_case2 = {
    "District": "Thanjavur",
    "Year": 2024,
    "Soil_Type": "alluvial soil",
    "Kharif Rainfall": 920.0,
    "Kharif Temperature": 32.5,
    "Soil_PH": 7.2, "Area": 65000.0
}

# CASE 3: Rainfall BELOW Historical Range (12 mm)
payload_case3 = {
    "District": "Thanjavur",
    "Year": 2024,
    "Soil_Type": "alluvial soil",
    "Kharif Rainfall": 12.0,
    "Soil_PH": 5.2, "Area": 65000.0
}

# CASE 4: Mixed Decimals & Integers (23, 23.3, 23.35)
payload_case4 = {
    "District": "Madurai",
    "Year": 2025,
    "Soil_Type": "red soil",
    "Kharif Temperature": 28.356,
    "Kharif Rainfall": 85.12,
    "Kharif Wind_Speed": 2,
    "Soil_PH": 6.85,
    "N": 295, "P": 18, "K": 210,
    "Fertilizer": 155.5, "Pesticide": 2.15, "Area": 45000
}

if __name__ == '__main__':
    c1 = test_api_case("CASE 1: Standard Inputs", payload_case1)
    c2 = test_api_case("CASE 2: Rainfall ABOVE Historical Range (920 mm)", payload_case2)
    c3 = test_api_case("CASE 3: Rainfall BELOW Historical Range (12 mm)", payload_case3)
    c4 = test_api_case("CASE 4: Mixed Decimals & Integers", payload_case4)
    
    if all([c1, c2, c3, c4]):
        print("\n🎉 ALL 4 PREDICTION TEST CASES PASSED SUCCESSFULLY!")
    else:
        print("\n❌ SOME TEST CASES FAILED!")
