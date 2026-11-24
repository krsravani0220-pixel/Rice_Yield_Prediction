"""
Copernicus Sentinel-2 Training Pipeline Comprehensive Acceptance Test Suite
===========================================================================
Validates:
  1. Pilot districts (Thanjavur, Thiruvarur, Salem, Tiruchirappalli, Dharmapuri)
  2. All 38 Tamil Nadu districts coverage
  3. Chennai edge case (urban tract with missing agricultural yield labels)
  4. Copernicus CDSE catalogue discovery, cloud masking, and caching
  5. Multi-spectral seasonal feature extraction (NDVI, NDRE, EVI, NDWI across Kharif, Rabi, Zaid)
  6. Dataset alignment with historical records (2015-2023) without label fabrication
  7. Chronological model training and evaluation (Train 2015-2021, Test 2022-2023)
  8. Model persistence, reloading, and inference
  9. SICKLE UNet3D architecture inspection, compatibility assessment, and fine-tuning demonstration
  10. FastAPI backend endpoints and database provenance logging
"""

import os
import sys
import json
import unittest
import numpy as np
import pandas as pd
import requests

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.satellite.district_registry import (
    TAMIL_NADU_DISTRICTS_REGISTRY,
    get_all_districts,
    get_district_profile
)
from src.satellite.copernicus_pipeline import (
    CopernicusArchiveCollector,
    CopernicusFeatureExtractor,
    CopernicusDatasetBuilder,
    SatelliteYieldModelTrainer
)
from src.satellite.sickle_adapter import SICKLEUNet3D, SICKLEModelAssessor


class TestCopernicusPipelineAcceptance(unittest.TestCase):
    """Rigorous acceptance test suite covering all major pipeline components."""

    @classmethod
    def setUpClass(cls):
        cls.pilot_districts = ["Thanjavur", "Thiruvarur", "Salem", "Tiruchirappalli", "Dharmapuri"]
        cls.all_districts = get_all_districts()
        cls.base_url = "http://127.0.0.1:8000"

    # --------------------------------------------------------------------------
    # 1. District Registry & Pilot Districts Coverage
    # --------------------------------------------------------------------------
    def test_01_all_30_districts_registry(self):
        """Verifies that all 38 Tamil Nadu districts are registered with coordinates and tiles."""
        self.assertEqual(len(self.all_districts), 38, f"Expected 38 districts, found {len(self.all_districts)}")
        for dist in self.all_districts:
            prof = get_district_profile(dist)
            self.assertIsNotNone(prof, f"Profile missing for {dist}")
            self.assertIn("lat", prof)
            self.assertIn("lon", prof)
            self.assertIn("primary_tile", prof)
            self.assertTrue(prof["lat"] > 8.0 and prof["lat"] < 14.0, f"Latitude out of bounds for {dist}")
            self.assertTrue(prof["lon"] > 76.0 and prof["lon"] < 81.0, f"Longitude out of bounds for {dist}")

    def test_02_pilot_districts_presence(self):
        """Verifies that all five pilot districts are recognized and profiled."""
        for pd_name in self.pilot_districts:
            self.assertIn(pd_name, self.all_districts)
            prof = get_district_profile(pd_name)
            self.assertIsNotNone(prof)

    # --------------------------------------------------------------------------
    # 2. Copernicus Catalogue Discovery, Cloud Filtering & Caching
    # --------------------------------------------------------------------------
    def test_03_catalogue_discovery_and_caching(self):
        """Verifies that catalogue queries retrieve observations and cache results on disk."""
        collector = CopernicusArchiveCollector()
        for dist in self.pilot_districts:
            res = collector.query_district_year_scenes(dist, 2022)
            self.assertEqual(res["district"], dist)
            self.assertEqual(res["year"], 2022)
            self.assertGreater(len(res["observations"]), 0, f"No observations found for {dist} 2022")
            # Verify cloud cover filtering constraint
            for obs in res["observations"]:
                if obs.get("cloud_cover_pct") is not None:
                    self.assertLessEqual(obs["cloud_cover_pct"], 25.0, "Observation exceeded cloud threshold")

    def test_04_all_30_districts_cached(self):
        """Verifies that all 270 district-year combinations across 2015-2023 are cached."""
        cache_dir = os.path.abspath("data/cache/copernicus_archive")
        self.assertTrue(os.path.exists(cache_dir))
        cached_files = [f for f in os.listdir(cache_dir) if f.endswith(".json")]
        self.assertGreaterEqual(len(cached_files), 270, f"Expected at least 270 cached files, found {len(cached_files)}")

    # --------------------------------------------------------------------------
    # 3. Spectral Feature Engineering & Seasonal Handling
    # --------------------------------------------------------------------------
    def test_05_seasonal_feature_extraction(self):
        """Verifies NDVI, NDRE, EVI, NDWI calculations across Kharif, Rabi, and Zaid."""
        collector = CopernicusArchiveCollector()
        extractor = CopernicusFeatureExtractor()

        obs_res = collector.query_district_year_scenes("Thanjavur", 2021)
        feat = extractor.extract_seasonal_features("Thanjavur", 2021, obs_res["observations"])

        expected_keys = [
            "Kharif_NDVI_mean", "Kharif_NDRE_mean", "Kharif_EVI_mean", "Kharif_NDWI_mean",
            "Rabi_NDVI_mean", "Rabi_NDRE_mean", "Rabi_EVI_mean", "Rabi_NDWI_mean",
            "Zaid_NDVI_mean", "Zaid_NDRE_mean", "Zaid_EVI_mean", "Zaid_NDWI_mean",
            "Annual_Peak_NDVI", "Annual_Mean_NDVI", "Annual_Total_Scenes"
        ]
        for k in expected_keys:
            self.assertIn(k, feat, f"Missing feature: {k}")
            self.assertGreater(feat[k], 0.0, f"Feature {k} should be positive")

        # In Thanjavur (Cauvery Delta), Rabi Samba is the major season and has peak vegetation
        self.assertGreaterEqual(feat["Rabi_NDVI_mean"], feat["Zaid_NDVI_mean"])

    # --------------------------------------------------------------------------
    # 4. Chennai Edge Case Handling
    # --------------------------------------------------------------------------
    def test_06_chennai_urban_edge_case(self):
        """Verifies Chennai is identified as an urban edge case with lower vegetation fraction."""
        extractor = CopernicusFeatureExtractor()
        collector = CopernicusArchiveCollector()

        obs_res = collector.query_district_year_scenes("Chennai", 2022)
        feat_chennai = extractor.extract_seasonal_features("Chennai", 2022, obs_res["observations"])
        feat_thanjavur = extractor.extract_seasonal_features("Thanjavur", 2022, obs_res["observations"])

        # Chennai urban center has significantly lower vegetation than agricultural Delta
        self.assertLess(feat_chennai["Annual_Mean_NDVI"], feat_thanjavur["Annual_Mean_NDVI"])

    # --------------------------------------------------------------------------
    # 5. Dataset Alignment & Provenance
    # --------------------------------------------------------------------------
    def test_07_training_dataset_construction(self):
        """Verifies the merged dataset shape, temporal span (2015-2023), and label counts."""
        dataset_path = os.path.abspath("outputs/data/satellite_yield_training_dataset.csv")
        self.assertTrue(os.path.exists(dataset_path), "Merged dataset file not found")

        df = pd.read_csv(dataset_path)
        self.assertEqual(len(df), 270, f"Expected exactly 270 rows (30 dist x 9 yrs), got {len(df)}")
        self.assertEqual(set(df["Year"].unique()), set(range(2015, 2024)))
        self.assertEqual(len(df["District"].unique()), 30)

        # 263 labeled valid rows, exactly 7 missing rows all in Chennai
        labeled_count = df["Yield"].notna().sum()
        self.assertEqual(labeled_count, 263, f"Expected 263 labeled rows, got {labeled_count}")

    # --------------------------------------------------------------------------
    # 6. Chronological Model Evaluation
    # --------------------------------------------------------------------------
    def test_08_chronological_splits_and_metrics(self):
        """Verifies model comparison metrics on the 2022-2023 chronological test split."""
        metrics_path = os.path.abspath("outputs/metrics/satellite_model_comparison.json")
        self.assertTrue(os.path.exists(metrics_path))

        with open(metrics_path, "r", encoding="utf-8") as f:
            comparison = json.load(f)

        model_names = [m["Model"] for m in comparison]
        self.assertIn("Simple Mean Baseline", model_names)
        self.assertIn("Historical Baseline Extra Trees", model_names)
        self.assertIn("Sentinel-2 Satellite-Only Model", model_names)
        self.assertIn("Multimodal Fusion Model (Satellite + Tabular)", model_names)

        for m in comparison:
            self.assertEqual(m["Test_Samples"], 59, "Test sample count should be 59 (29 dist x 2 yrs + 1 Chennai)")
            self.assertTrue(m["Test_MAE"] > 0, "Test MAE must be positive")
            self.assertTrue(m["Test_RMSE"] > 0, "Test RMSE must be positive")

        # Satellite-Only model must outperform Simple Mean Baseline
        sat_model = [m for m in comparison if m["Model"] == "Sentinel-2 Satellite-Only Model"][0]
        mean_model = [m for m in comparison if m["Model"] == "Simple Mean Baseline"][0]
        self.assertLess(sat_model["Test_MAE"], mean_model["Test_MAE"])
        self.assertLess(sat_model["Test_RMSE"], mean_model["Test_RMSE"])

    # --------------------------------------------------------------------------
    # 7. Model Persistence & Reloading
    # --------------------------------------------------------------------------
    def test_09_model_persistence_and_reloading(self):
        """Verifies that saved models load cleanly and make valid predictions."""
        import joblib
        sat_model_path = os.path.abspath("models/satellite_yield_model.joblib")
        meta_path = os.path.abspath("models/satellite_pipeline_meta.joblib")

        self.assertTrue(os.path.exists(sat_model_path))
        self.assertTrue(os.path.exists(meta_path))

        model = joblib.load(sat_model_path)
        meta = joblib.load(meta_path)

        scaler = meta["scaler_sat"]
        sat_cols = meta["satellite_features"]
        dummy_input = np.ones((1, len(sat_cols))) * 0.5
        X_s = scaler.transform(dummy_input)

        pred = model.predict(X_s)[0]
        self.assertTrue(pred > 1.0 and pred < 6.5, f"Unreasonable yield prediction: {pred}")

    # --------------------------------------------------------------------------
    # 8. SICKLE Pretrained Models Assessment & Controlled Fine-Tuning
    # --------------------------------------------------------------------------
    def test_10_sickle_checkpoints_and_assessment(self):
        """Verifies SICKLE UNet3D architecture and assessment report."""
        report_path = os.path.abspath("outputs/metrics/sickle_assessment_report.json")
        self.assertTrue(os.path.exists(report_path), "SICKLE assessment report missing")

        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        self.assertIn("compatibility_assessment", report)
        self.assertIn("controlled_fine_tuning_experiment", report)

        compat = report["compatibility_assessment"]
        self.assertEqual(compat["spectral_compatibility"]["expected_bands_count"], 12)
        self.assertEqual(compat["spatiotemporal_compatibility"]["input_tensor_shape"], "(B, 12, T, 32, 32)")

        exp = report["controlled_fine_tuning_experiment"]
        self.assertGreater(compat["crop_yield_checkpoint"]["total_parameters"], 3000000)
        self.assertGreater(exp["parameters_count"], 500000)
        self.assertEqual(exp["epochs_run"], 3)

    # --------------------------------------------------------------------------
    # 9. Backend REST API Endpoints
    # --------------------------------------------------------------------------
    def test_11_backend_status_endpoint(self):
        """Verifies GET /api/satellite-pipeline/status."""
        resp = requests.get(f"{self.base_url}/api/satellite-pipeline/status", timeout=10)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ready")
        self.assertEqual(data["districts_total"], 30)
        self.assertEqual(data["catalogue_cache"]["cached_district_years"], 270)

    def test_12_backend_coverage_endpoint(self):
        """Verifies GET /api/satellite-pipeline/coverage."""
        resp = requests.get(f"{self.base_url}/api/satellite-pipeline/coverage", timeout=10)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_districts"], 30)
        self.assertEqual(data["supported_districts"], 29)
        self.assertIn("Chennai", data["edge_case_districts"])

    def test_13_backend_metrics_endpoint(self):
        """Verifies GET /api/satellite-pipeline/metrics."""
        resp = requests.get(f"{self.base_url}/api/satellite-pipeline/metrics", timeout=10)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("model_comparison", data)
        self.assertIn("historical_reference_baseline", data)
        self.assertEqual(data["historical_reference_baseline"]["test_MAE"], 0.2666)

    def test_14_backend_prediction_pilot_and_chennai(self):
        """Verifies POST /api/satellite-predict for pilot districts and Chennai fallback."""
        # 1. Pilot district: Thanjavur
        resp_thanj = requests.post(
            f"{self.base_url}/api/satellite-predict",
            json={"district": "Thanjavur", "year": 2024},
            timeout=10
        )
        self.assertEqual(resp_thanj.status_code, 200)
        data_thanj = resp_thanj.json()
        self.assertFalse(data_thanj["fallback_used"])
        self.assertTrue(1.5 <= data_thanj["predicted_yield_tonnes_ha"] <= 6.0)
        self.assertIn("satellite_telemetry", data_thanj)
        self.assertIn("provenance", data_thanj)

        # 2. Edge Case: Chennai fallback
        resp_chennai = requests.post(
            f"{self.base_url}/api/satellite-predict",
            json={"district": "Chennai", "year": 2024},
            timeout=10
        )
        self.assertEqual(resp_chennai.status_code, 200)
        data_chennai = resp_chennai.json()
        self.assertTrue(data_chennai["fallback_used"])
        self.assertIn("Urban Non-Agricultural Fallback", data_chennai["data_quality_status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
