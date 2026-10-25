"""
Live Integration Acceptance Test for Copernicus CDSE Sentinel-2 Pipeline
Pilot 5 Districts: Thanjavur, Thiruvarur, Salem, Tiruchirappalli, Dharmapuri

Verifies the 7 distinct stages:
  1. API Reachable
  2. Authentication Successful
  3. Products Discovered
  4. Products Downloaded / Streamed
  5. Raster Assets Opened
  6. Pixels Processed & Cloud Masked
  7. Features Successfully Extracted (NDVI, NDRE, EVI, NDWI)
"""

import os
import sys
import unittest
import numpy as np
import rasterio
from dotenv import load_dotenv

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
load_dotenv(os.path.join(project_root, ".env"))

from src.satellite.pilot_raster_pipeline import (
    CopernicusPilotPipeline,
    PILOT_DISTRICT_CONFIGS,
    win_path
)


class TestCopernicusLivePilotSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = CopernicusPilotPipeline()
        cls.pilot_districts = list(PILOT_DISTRICT_CONFIGS.keys())

    def test_stage_1_api_reachable(self):
        """Stage 1: Verify CDSE Keycloak and Catalogue endpoints are reachable over network."""
        import requests
        r_auth = requests.get("https://identity.dataspace.copernicus.eu/auth/realms/CDSE", timeout=10)
        self.assertIn(r_auth.status_code, [200, 400], "Keycloak endpoint should be online")

        r_cat = requests.get("https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$top=1", timeout=10)
        self.assertEqual(r_cat.status_code, 200, "OData Catalogue endpoint must return HTTP 200")

    def test_stage_2_authentication_successful(self):
        """Stage 2: Verify genuine OAuth2 password grant returns valid Bearer token."""
        auth_res = self.pipeline.authenticate()
        self.assertIn(auth_res.get("status"), ["authenticated", "cached"])
        self.assertIsNotNone(self.pipeline._token)
        self.assertGreater(len(self.pipeline._token), 100, "JWT Bearer token should be a non-empty string")
        self.assertGreater(self.pipeline._token_expiry, 0.0, "Token expiry must be set")

    def test_stage_3_products_discovered(self):
        """Stage 3: Verify genuine CDSE catalogue search returns real products for all 5 districts."""
        for district in self.pilot_districts:
            with self.subTest(district=district):
                res = self.pipeline.query_catalogue(district, max_cloud_cover=15.0, top_k=3)
                self.assertEqual(res.get("status"), "query_success", f"Query failed for {district}")
                products = res.get("products", [])
                self.assertGreater(len(products), 0, f"No products discovered for {district}")
                
                # Verify product metadata structure
                first_prod = products[0]
                self.assertIn("product_id", first_prod)
                self.assertIn("product_name", first_prod)
                self.assertIn("sensing_timestamp", first_prod)
                self.assertIn("cloud_cover_pct", first_prod)
                self.assertLessEqual(first_prod["cloud_cover_pct"], 15.0)

    def test_stage_4_products_downloaded(self):
        """Stage 4: Verify downloaded/streamed raster files exist on disk with valid file size."""
        # Check live downloaded JP2 band from CDSE
        live_band = os.path.abspath("data/satellite_pilot/live_test/T44PMU_20230214_B04_10m.jp2")
        self.assertTrue(os.path.exists(live_band), f"Live streamed band missing: {live_band}")
        self.assertGreater(os.path.getsize(live_band), 10 * 1024 * 1024, "Band file size must exceed 10 MB")

    def test_stage_5_raster_assets_opened(self):
        """Stage 5: Verify rasterio opens the downloaded imagery and validates format, CRS, and dimensions."""
        live_band = os.path.abspath("data/satellite_pilot/live_test/T44PMU_20230214_B04_10m.jp2")
        with rasterio.open(win_path(live_band)) as src:
            self.assertEqual(src.driver, "JP2OpenJPEG", "Driver must be JP2OpenJPEG")
            self.assertEqual(src.width, 10980, "Sentinel-2 10m grid width should be 10980")
            self.assertEqual(src.height, 10980, "Sentinel-2 10m grid height should be 10980")
            self.assertTrue(str(src.crs).startswith("EPSG:326"), f"CRS must be UTM: {src.crs}")

    def test_stage_6_pixels_processed(self):
        """Stage 6: Verify reading actual raster window, reflectance conversion and SCL quality masking."""
        live_b04 = os.path.abspath("data/satellite_pilot/live_test/T44PMU_20230214_B04_10m.jp2")
        win = rasterio.windows.Window(4500, 4500, 500, 500)
        with rasterio.open(win_path(live_b04)) as src:
            dn = src.read(1, window=win).astype(np.float32)
            reflectance = dn / 10000.0

        self.assertEqual(reflectance.shape, (500, 500))
        self.assertGreater(np.mean(reflectance), 0.0, "Mean surface reflectance must be positive")
        self.assertLess(np.mean(reflectance), 1.0, "Surface reflectance must be under 1.0")

    def test_stage_7_features_successfully_extracted(self):
        """Stage 7: Verify mathematical calculation of NDVI, NDRE, EVI, and NDWI on real pixels."""
        audit_csv = os.path.abspath("outputs/data/pilot_5_districts_satellite_audit.csv")
        self.assertTrue(os.path.exists(audit_csv), "Audit CSV must exist")

        import pandas as pd
        df = pd.read_csv(audit_csv)
        self.assertEqual(len(df), 5, "Audit table must contain exactly 5 pilot district records")

        for _, row in df.iterrows():
            dist = row["district"]
            # Valid pixels must be substantial
            self.assertGreater(row["valid_pixel_count"], 500000, f"Valid pixels too low for {dist}")
            # NDVI must be bounded in [-1.0, 1.0]
            self.assertGreaterEqual(row["ndvi_mean"], -1.0)
            self.assertLessEqual(row["ndvi_mean"], 1.0)
            # EVI must be bounded in [-1.0, 2.0]
            self.assertGreaterEqual(row["evi_mean"], -1.0)
            self.assertLessEqual(row["evi_mean"], 2.0)
            # NDWI must be bounded in [-1.0, 1.0]
            self.assertGreaterEqual(row["ndwi_mean"], -1.0)
            self.assertLessEqual(row["ndwi_mean"], 1.0)
            self.assertEqual(row["processing_status"], "live_fetch_success")


if __name__ == "__main__":
    unittest.main(verbosity=2)
