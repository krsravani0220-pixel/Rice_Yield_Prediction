import urllib.request
import urllib.error
import json

BASE_URL = "http://127.0.0.1:8000"

def run_test(test_num, name, payload, expected_status):
    print(f"\n--- TEST {test_num}: {name} ---")
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    headers = {'Content-Type': 'application/json'} if payload is not None else {}
    req = urllib.request.Request(f"{BASE_URL}/api/predict-yield", data=data, headers=headers)
    
    try:
        res = urllib.request.urlopen(req)
        status = res.getcode()
        res_json = json.loads(res.read().decode('utf-8'))
        print(f"Status Code: {status}")
        if status == expected_status:
            print(f"PASS: Received expected HTTP {expected_status}")
            print(f"  Predicted Yield: {res_json.get('predicted_yield')} tonnes/ha")
            return True
        else:
            print(f"FAIL: Expected HTTP {expected_status}, got {status}")
            return False
    except urllib.error.HTTPError as e:
        print(f"Status Code: {e.code}")
        err_msg = e.read().decode('utf-8')
        print(f"Response Detail: {err_msg[:120]}")
        if e.code == expected_status:
            print(f"PASS: Correctly rejected incomplete input with HTTP {expected_status}!")
            return True
        else:
            print(f"FAIL: Expected HTTP {expected_status}, got {e.code}")
            return False

if __name__ == '__main__':
    print("================ RUNNING ALL 6 REQUIRED VALIDATION TESTS ================")

    # TEST 3: Click Predict with completely empty payload
    t3 = run_test(3, "Click Predict with empty fields", {}, 422)

    # TEST 4: Enter only some fields (missing rainfall, N, P, K)
    partial_payload = {
        "District": "Thanjavur",
        "Year": 2024,
        "Soil_Type": "alluvial soil",
        "Kharif Temperature": 29.5
    }
    t4 = run_test(4, "Enter only partial fields", partial_payload, 422)

    # TEST 5: Enter ALL 25 required fields
    full_payload = {
        "District": "Thanjavur", "Year": 2024, "Soil_Type": "alluvial soil",
        "Kharif Temperature": 29.5, "Kharif Rainfall": 120.5, "Kharif Humidity": 70.2, "Kharif Wind_Speed": 3.2, "Kharif Soil_Moisture": 0.55,
        "Rabi Temperature": 25.1, "Rabi Rainfall": 95.0, "Rabi Humidity": 78.0, "Rabi Wind_Speed": 2.3, "Rabi Soil_Moisture": 0.65,
        "Zaid Temperature": 29.8, "Zaid Rainfall": 45.0, "Zaid Humidity": 62.0, "Zaid Wind_Speed": 2.4, "Zaid Soil_Moisture": 0.48,
        "Soil_PH": 7.2, "N": 300.0, "P": 20.0, "K": 200.0, "Fertilizer": 160.0, "Pesticide": 2.2, "Area": 60000.0
    }
    t5 = run_test(5, "Enter ALL required fields", full_payload, 200)

    # TEST 6: Enter values outside historical ranges (Extreme Rainfall 920 mm)
    extreme_payload = dict(full_payload)
    extreme_payload["Kharif Rainfall"] = 920.0
    t6 = run_test(6, "Enter value outside historical range (920 mm rainfall)", extreme_payload, 200)

    print("\n================ TEST SUITE SUMMARY ================")
    if all([t3, t4, t5, t6]):
        print("ALL VALIDATION TESTS PASSED!")
    else:
        print("SOME TESTS FAILED!")
