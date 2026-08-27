import sys
import urllib.request
import urllib.error
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8000"

def test_forecast(district, year, method, should_pass=True):
    print(f"\n--- Testing Forecast: District={district}, Year={year}, Method={method} ---")
    payload = {
        "district": district,
        "target_year": year,
        "method": method
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/forecast",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    try:
        res = urllib.request.urlopen(req)
        status = res.getcode()
        res_json = json.loads(res.read().decode('utf-8'))
        print(f"Status: {status} OK")
        if should_pass:
            print(f"  Mode: {res_json.get('mode')}")
            print(f"  Predicted Yield: {res_json.get('predicted_yield')} tonnes/ha")
            print(f"  Forecasted Features Count: {len(res_json.get('forecasted_features', {}))}")
            print(f"  Kharif Rainfall Forecast: {res_json.get('forecasted_features', {}).get('Kharif Rainfall')} mm")
            return True
        else:
            print(f"FAIL: Expected rejection for year {year}, but passed!")
            return False
    except urllib.error.HTTPError as e:
        print(f"Status: HTTP {e.code}")
        err_msg = e.read().decode('utf-8')
        print(f"Detail: {err_msg[:120]}")
        if not should_pass and e.code == 400:
            print(f"PASS: Successfully rejected invalid forecast year {year}")
            return True
        else:
            print(f"FAIL: Unexpected error for year {year}")
            return False
    except Exception as e:
        print(f"FAILED with error: {e}")
        return False

if __name__ == '__main__':
    print("================ E2E FORECAST MODE TEST SUITE ================")
    
    # Valid Years: 2026 and 2027
    t1 = test_forecast("Thanjavur", 2026, "Exponential Smoothing", should_pass=True)
    t2 = test_forecast("Thanjavur", 2027, "Exponential Smoothing", should_pass=True)
    t3 = test_forecast("Madurai", 2026, "Moving Average", should_pass=True)
    t4 = test_forecast("Coimbatore", 2027, "Linear Trend", should_pass=True)
    
    # Invalid Years: 2024, 2025, 2028, 2030 (Must be rejected)
    t5 = test_forecast("Thanjavur", 2028, "Exponential Smoothing", should_pass=False)
    t6 = test_forecast("Madurai", 2030, "Exponential Smoothing", should_pass=False)

    print("\n================ SUMMARY ================")
    if all([t1, t2, t3, t4, t5, t6]):
        print("🎉 ALL FORECAST E2E TESTS PASSED!")
    else:
        print("❌ SOME FORECAST TESTS FAILED!")
