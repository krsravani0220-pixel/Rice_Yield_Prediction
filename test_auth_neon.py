import sys
import urllib.request
import urllib.error
import json

BASE_URL = "http://127.0.0.1:8000"

def make_req(path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.getcode(), json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

def run_tests():
    print("================ TESTING NEON CLOUD & AUTH ENDPOINTS ================")
    
    # 1. Neon Status
    code, res = make_req("/api/auth/neon-status")
    print(f"1. Neon Status (Code: {code}):", res.get("engine"))
    assert code == 200

    # 2. Register User
    user_payload = {
        "full_name": "Murugan Gounder",
        "email": "murugan.thanjavur@agri.tn.gov.in",
        "password": "FarmPassword2026",
        "district": "Thanjavur",
        "role": "Farmer",
        "phone": "9842100000"
    }
    code, res = make_req("/api/auth/register", user_payload)
    print(f"2. Register User (Code: {code}):", res.get("message") or res.get("detail"))
    # Either registered (200) or already exists (400)
    token = res.get("token")

    # 3. Login User
    login_payload = {
        "email": "murugan.thanjavur@agri.tn.gov.in",
        "password": "FarmPassword2026"
    }
    code, res = make_req("/api/auth/login", login_payload)
    print(f"3. Login User (Code: {code}):", res.get("message") or res.get("detail"))
    assert code == 200
    token = res["token"]
    print(f"   Received JWT Token: {token[:35]}...")

    # 4. Get Profile (/api/auth/me)
    code, res = make_req("/api/auth/me", token=token)
    print(f"4. Profile /me (Code: {code}):", res.get("user", {}).get("full_name"))
    assert code == 200

    # 5. Save Prediction to Neon Cloud
    save_payload = {
        "district": "Thanjavur",
        "year": 2026,
        "prediction_type": "manual",
        "predicted_yield": 3.82,
        "unit": "tonnes/ha",
        "input_summary": {
            "Rainfall": 125.0,
            "Temperature": 29.2,
            "Soil_PH": 7.1
        },
        "shap_insights": {
            "top_positive": ["Kharif Rainfall (+0.18 t/ha)"]
        }
    }
    code, res = make_req("/api/auth/save-prediction", save_payload, token=token)
    print(f"5. Save Prediction (Code: {code}):", res.get("message"))
    assert code == 200

    # 6. Fetch Prediction History from Neon Cloud
    code, res = make_req("/api/auth/history", token=token)
    print(f"6. Fetch History (Code: {code}): Total Records = {res.get('count')}")
    assert code == 200
    assert res["count"] > 0
    print(f"   First Record Yield: {res['history'][0]['predicted_yield']} tonnes/ha ({res['history'][0]['district']})")

    print("\n🎉 ALL NEON CLOUD & AUTHENTICATION ENDPOINTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
