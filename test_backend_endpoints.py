"""
Backend Endpoints Test Suite (FastAPI TestClient)
==================================================
Tests existing core endpoints and newly integrated satellite endpoints:
1. /api/districts
2. /api/predict-yield
3. /api/forecast
4. /api/crop-health
5. /api/model-metrics
6. /api/satellite-pilot-results
7. /api/satellite-district-features (Thanjavur, Thiruvarur, Salem, Tiruchirappalli, Dharmapuri)
8. /api/satellite-district-prediction
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath('.'))

from backend.app.main import app

class TestBackendEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_districts(self):
        res = self.client.get("/api/districts")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("districts", data)
        self.assertIn("Thanjavur", data["districts"])
        self.assertIn("Salem", data["districts"])

    def test_02_predict_yield_manual(self):
        payload = {
            "District": "Thanjavur", "Year": 2024, "Soil_Type": "alluvial soil",
            "Kharif Temperature": 29.5, "Kharif Rainfall": 120.5, "Kharif Humidity": 70.2, "Kharif Wind_Speed": 3.2, "Kharif Soil_Moisture": 0.55,
            "Rabi Temperature": 25.1, "Rabi Rainfall": 95.0, "Rabi Humidity": 78.0, "Rabi Wind_Speed": 2.3, "Rabi Soil_Moisture": 0.65,
            "Zaid Temperature": 29.8, "Zaid Rainfall": 45.0, "Zaid Humidity": 62.0, "Zaid Wind_Speed": 2.4, "Zaid Soil_Moisture": 0.48,
            "Soil_PH": 7.2, "N": 300.0, "P": 20.0, "K": 200.0, "Fertilizer": 160.0, "Pesticide": 2.2, "Area": 60000.0
        }
        res = self.client.post("/api/predict-yield", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("predicted_yield", data)
        self.assertGreater(data["predicted_yield"], 0.0)

    def test_03_forecast(self):
        payload = {"district": "Thanjavur", "target_year": 2026, "method": "Exponential Smoothing"}
        res = self.client.post("/api/forecast", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("predicted_yield", data)

    def test_04_crop_health(self):
        payload = {
            "growth_stage": "Tillering",
            "leaf_condition": "Yellowing",
            "water_status": "Drought Stress",
            "pest_obs": "Stem Borer",
            "disease_obs": "None"
        }
        res = self.client.post("/api/crop-health", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("advisories_en", data)

    def test_05_satellite_pilot_results(self):
        res = self.client.get("/api/satellite-pilot-results")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["model"], "[S2]_unet3d_season")
        self.assertIn("metrics", data)
        self.assertIn("plots", data)
        self.assertEqual(len(data["plots"]), 6)

    def test_06_satellite_district_features_all_five(self):
        for d in ["Thanjavur", "Thiruvarur", "Salem", "Tiruchirappalli", "Dharmapuri"]:
            res = self.client.get(f"/api/satellite-district-features?district={d}")
            self.assertEqual(res.status_code, 200, f"Failed for district: {d}")
            data = res.json()
            self.assertEqual(data["district"], d)
            self.assertIn("multi_spectral_features", data)
            self.assertIn("coverage_status", data)

    def test_07_satellite_district_prediction(self):
        # Thanjavur: Real SICKLE model execution succeeds
        res = self.client.get("/api/satellite-district-prediction?district=Thanjavur&year=2023")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["district"], "Thanjavur")
        self.assertEqual(data["status"], "success")
        self.assertGreater(data["baseline_tabular_yield_tha"], 0.0)
        self.assertIsNotNone(data["satellite_enhanced_yield_tha"])
        self.assertGreater(data["satellite_enhanced_yield_tha"], 0.0)
        self.assertIn("model_used", data)
        self.assertGreater(data["usable_observations_count"], 0)

        # Salem & Dharmapuri: Honestly report insufficient data without fabricating
        for d in ["Salem", "Dharmapuri"]:
            res = self.client.get(f"/api/satellite-district-prediction?district={d}&year=2023")
            self.assertEqual(res.status_code, 200, f"Failed for district: {d}")
            data = res.json()
            self.assertEqual(data["district"], d)
            self.assertEqual(data["status"], "insufficient_data")
            self.assertIsNone(data["satellite_enhanced_yield_tha"])
            self.assertIn("insufficient_data_reason", data)
            self.assertIn("model_used", data)
            self.assertGreater(data["usable_observations_count"], 0)
            self.assertIn("observation_date_range", data)

    def test_08_predict_yield_with_satellite_integration(self):
        """Test POST /api/predict-yield with optional include_satellite=True."""
        payload = {
            "District": "Thanjavur", "Year": 2024, "Soil_Type": "alluvial soil",
            "Kharif Temperature": 29.5, "Kharif Rainfall": 120.5, "Kharif Humidity": 70.2, "Kharif Wind_Speed": 3.2, "Kharif Soil_Moisture": 0.55,
            "Rabi Temperature": 25.1, "Rabi Rainfall": 95.0, "Rabi Humidity": 78.0, "Rabi Wind_Speed": 2.3, "Rabi Soil_Moisture": 0.65,
            "Zaid Temperature": 29.8, "Zaid Rainfall": 45.0, "Zaid Humidity": 62.0, "Zaid Wind_Speed": 2.4, "Zaid Soil_Moisture": 0.48,
            "Soil_PH": 7.2, "N": 300.0, "P": 20.0, "K": 200.0, "Fertilizer": 160.0, "Pesticide": 2.2, "Area": 60000.0,
            "include_satellite": True
        }
        res = self.client.post("/api/predict-yield", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("predicted_yield", data)
        self.assertIn("satellite_prediction", data)
        self.assertEqual(data["satellite_prediction"]["district"], "Thanjavur")
        self.assertEqual(data["satellite_prediction"]["status"], "success")


if __name__ == '__main__':
    print("=" * 70)
    print("RUNNING BACKEND ENDPOINTS REGRESSION TEST SUITE")
    print("=" * 70)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBackendEndpoints)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
