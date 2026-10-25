import urllib.request
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=" * 60)
    print("VERIFYING FRONTEND & BACKEND CONTRACTS")
    print("=" * 60)

    # 1. Check API endpoint returns 30 districts
    resp = urllib.request.urlopen('http://127.0.0.1:8000/api/districts')
    data = json.loads(resp.read().decode('utf-8'))
    districts = data.get('districts', [])
    print(f"Total districts from /api/districts: {len(districts)}")
    assert len(districts) == 30, f"Expected 30 districts, got {len(districts)}"

    # 2. Check frontend index.html elements
    with open('frontend/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    assert 'id="live-district-select"' in html, "live-district-select not found"
    assert 'id="satellite-district-dropdown"' in html, "satellite-district-dropdown not found"
    assert 'Select Pilot District (5 Pilot Districts)' in html, "Pilot district label not found"
    assert 'id="live-veg-ndre-mean"' in html, "NDRE metric element missing"
    assert 'id="live-veg-evi-mean"' in html, "EVI metric element missing"
    assert 'id="live-veg-ndwi-mean"' in html, "NDWI metric element missing"
    assert 'id="live-sufficiency-banner"' in html, "Sufficiency banner missing"
    print("[PASS] HTML structure contains all required pilot satellite UI components.")

    # 3. Check frontend app.js logic
    with open('frontend/app.js', 'r', encoding='utf-8') as f:
        js = f.read()

    assert 'const pilotDistricts = ["Thanjavur", "Thiruvarur", "Salem", "Tiruchirappalli", "Dharmapuri"];' in js
    assert "liveDistSelect.add(new Option(d, d));" in js
    assert "/api/satellite-predict-live" in js
    print("[PASS] JavaScript strictly restricts satellite dropdowns to 5 pilot districts.")

    # 4. Check POST /api/satellite-predict-live for Salem
    req_data = json.dumps({"district": "Salem"}).encode("utf-8")
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/satellite-predict-live',
        data=req_data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as r:
        pred_res = json.loads(r.read().decode('utf-8'))
        print(f"[PASS] Live prediction API succeeded for {pred_res['district']}:")
        print(f"       Yield: {pred_res['predicted_yield_t_ha']} t/ha")
        print(f"       NDVI: {pred_res['vegetation_indices']['ndvi']['mean']}")
        print(f"       NDRE: {pred_res['vegetation_indices']['ndre']['mean']}")
        print(f"       EVI:  {pred_res['vegetation_indices']['evi']['mean']}")
        print(f"       NDWI: {pred_res['vegetation_indices']['ndwi']['mean']}")
        print(f"       Valid Pixels: {pred_res['vegetation_indices']['valid_pixels']}")
        print(f"       Model: {pred_res['model_name']}")

    print("=" * 60)
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    main()
